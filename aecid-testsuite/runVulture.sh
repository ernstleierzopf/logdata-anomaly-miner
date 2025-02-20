#!/bin/bash

vulture /usr/lib/logdata-anomaly-miner --min-confidence=100 --exclude ".venv/*.py"
exit $?
