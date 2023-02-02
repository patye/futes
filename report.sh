#!/bin/bash
hdata=$(jq --arg time "$(date +%s)" '.time=$time' code/system-json.txt | jq '.time=(.time|tonumber)')
curl -X POST -k -u elastic:Elast1c@123 https://stream.developerz.hu/elastic/heating/_doc -H 'Content-Type: application/json' -d "$hdata"
