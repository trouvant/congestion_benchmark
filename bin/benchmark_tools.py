#!/usr/bin/env python

import os, sys, re
import numpy as np
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def plot_rtt(algo_name, out_dir):
    fmat = r"(?P<time>[\d.]*) (?P<rtt>[\d.]*)"

    in_file = out_dir+algo_name+'.rtt.out'
    out_file = out_dir+algo_name+'.rtt.png'
    cdf_file = out_dir+algo_name+'.rttCDF.png'

    time = []
    rtt = []
    with open(in_file) as f:
        for line in f:
            searchObj = re.search(fmat, line)
            if searchObj is not None:
                t = float(searchObj.groupdict()['time'])
                time.append(t)
                s = float(searchObj.groupdict()['rtt'])
                rtt.append(s)
    plt.figure()
    plt.plot(time,rtt,'.', label=algo_name)
    plt.ylabel('RTT (usec)')
    plt.xlabel('Time (sec)')
    plt.title('RTT for '+algo_name+' experiment')
    plt.grid()
    plt.savefig(out_file)
    print "Saved plot: ", out_file

    # Compute the CDF
    sorted_data = np.sort(rtt)
    yvals=np.arange(len(sorted_data))/float(len(sorted_data)-1)
    plt.figure()
    #plt.xlim(0,300)
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for '+algo_name+' experiment')
    plt.plot(sorted_data, yvals, '.', label=algo_name)
    plt.savefig(cdf_file)
    print "Saved plot: ", cdf_file

    return sorted_data, yvals

"""
    Plot the given CDFs on the same figure for easier comparison
"""
def plot_allRTTcdf(out_dir, timely_cdf, hopeMax_cdf, hopeSum_cdf):
    
    allCDF_file = out_dir+'Timely-Hope.rttCDF_benchmark.png'
    plt.figure()
    plt.xlabel('RTT (usec)')
    plt.title('CDF of RTT for benchmarked congestion control algorithms')

    plt.plot(timely_cdf[0], timely_cdf[1], '-', label='Timely')
    plt.plot(hopeMax_cdf[0], hopeMax_cdf[1], '-', label='Hope-Max')
    plt.plot(hopeSum_cdf[0], hopeSum_cdf[1], '-', label='Hope-Sum')

    plt.legend(loc='lower right')
    plt.savefig(allCDF_file)
    print "Saved plot: ", allCDF_file

def plot_throughput(algo_name, num_clients, out_dir, num_leafs=0, num_spine=1):
    
    tr_file = out_dir+algo_name+'.tr'
    out_file = out_dir+algo_name+'.thp.png'
    granularity = 0.001
    clock = 0
    time = []

    num_nodes = num_clients + num_leafs + num_spine + 1
    throughputs = []
    sum_bytes = []
    last_seq = []
    for i in range(num_nodes):
	throughputs.append([])
	sum_bytes.append(0.0)
	last_seq.append(0.0)

    with open(tr_file) as f:
        for line in f:
            split_line = line.split()
            if ((split_line[0] == '-' and split_line[4] == 'tcp')):
                t = float(split_line[1])
		s = int(split_line[2]) #source node
		if ( t-clock < granularity):
		    # Don't count for retransmissions
		    if ( int(split_line[10]) > last_seq[s] ):
		        sum_bytes[s] += int(split_line[5])
			last_seq[s] = int(split_line[10])
		
		else:
		    time.append(t)
		    clock += granularity
		    
		    for i in range(num_nodes):
			dummy_thp = sum_bytes[i] * 8 /granularity /1000000
			throughputs[i].append(dummy_thp)
			sum_bytes[i] = 0.0
		    
		    sum_bytes[s] += int(split_line[5])
    time.append(t)
    for i in range(num_nodes):
	dummy_thp = sum_bytes[i] * 8 /granularity /1000000
	throughputs[i].append(dummy_thp)

    total_thp = []
    for n in range(len(time)):
	total_thp.append(0.0)
	for i in range(num_clients):
	    total_thp[n] += throughputs[i][n]

    plt.figure()
    for i in range(num_clients):
	node_name = 'Client_{}'.format(i)
        plt.plot(time,throughputs[i],linestyle='-', marker='', label=node_name)

    plt.plot(time,total_thp,linestyle='-', marker='', label='Total')
	
    plt.yscale('log')
    plt.ylabel('Throughput (Mbps)')
    plt.xlabel('Time (sec)')
    plt.title('Throughput for '+algo_name+' experiment')
    plt.legend(bbox_to_anchor=(1.04,0.5), loc="center left", borderaxespad=0)
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print "Saved plot: ", out_file

    return time,total_thp

"""
   Plot the given throughputs in the same figure for easier comparison
"""
def plot_allTotalThp(out_dir, timely_thp, hopeMax_thp, hopeSum_thp):
    
    allThp_file = out_dir+'Timely-Hope.thp_benchmark.png'
    plt.figure()
    plt.ylabel('Throughput (Mbps)')
    plt.xlabel('Time (sec)')
    plt.title('Total throughputs for benchmarked congestion control algorithms')

    plt.plot(timely_thp[0], timely_thp[1], '-', label='Timely')
    plt.plot(hopeMax_thp[0], hopeMax_thp[1], '-', label='Hope-Max')
    plt.plot(hopeSum_thp[0], hopeSum_thp[1], '-', label='Hope-Sum')

    plt.legend(loc='lower right')
    plt.savefig(allThp_file)
    print "Saved plot: ", allThp_file

"""
Parse the sampled queue size output file and plot the queue size over time
"""
def plot_queue(algo_name, out_dir):
    fmat = r"(?P<time>[\d.]*) (?P<from_node>[\d]*) (?P<to_node>[\d]*) (?P<q_size_B>[\d.]*) (?P<q_size_p>[\d.]*) (?P<arr_p>[\d.]*) (?P<dep_p>[\d.]*) (?P<drop_p>[\d.]*) (?P<arr_B>[\d.]*) (?P<dep_B>[\d.]*) (?P<drop_B>[\d.]*)"

    in_file = out_dir+algo_name+'.queue.out'
    out_file = out_dir+algo_name+'.queue.png'

    time = []
    q_size = []
    with open(in_file) as f:
        for line in f:
            searchObj = re.search(fmat, line)
            if searchObj is not None:
                t = float(searchObj.groupdict()['time'])
                time.append(t)
                s = float(searchObj.groupdict()['q_size_p'])
                q_size.append(s)
    
    plt.figure()
    plt.plot(time,q_size,linestyle='-', marker='', label='Queue in packets')
    plt.yscale('log')
    #plt.xscale('log')
    #plt.xlim(0,0.2)
    plt.ylabel('Queue (packets)')
    plt.xlabel('Time (sec)')
    plt.title('Queue size for '+algo_name+' experiment')
    plt.grid()
    plt.savefig(out_file, bbox_inches="tight")
    print "Saved plot: ", out_file

