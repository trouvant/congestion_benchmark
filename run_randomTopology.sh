#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/randomTopology_sim.py --timely --hope_max 
#--hope_squ

#echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
#sudo python -m SimpleHTTPServer 80

