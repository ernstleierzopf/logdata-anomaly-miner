#!/bin/bash

python3 -m flake8 /usr/lib/logdata-anomaly-miner --config /home/aminer/logdata-anomaly-miner/aecid-testsuite/.flake8
exit $?
