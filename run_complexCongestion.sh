#!/bin/bash

source ./dctcp-ns2/settings.sh
./lib/complexCongestion_sim.py --hope --timely

sudo python -m SimpleHTTPServer 80
echo "Please navigate to:  http://<IP_ADDRESS> in your browser to view the results."
