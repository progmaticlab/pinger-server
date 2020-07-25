#!/bin/bash

if [[ -z "${MASTER}" ]]; then
    echo "MASTER env is undefined"
    exit 1
fi

reg="${SELFREGISTER:-1}"
if [ $reg ]; then
  curl -s http://$MASTER:8000/register
fi

while :
do
  hosts=$(curl -s http://$MASTER:8000/hosts) 
  pids=""
  for host in $hosts
  do
    ping -q -c 1 -w 10 $host &> /dev/null &
    pids+=" $!"
  done
  res="{"
  for p in $pids
  do
    if wait $p; then
  	  r=0
    else
  	  r=1
    fi
    res="$res\"$host\": $r,"
  done
  res="$res\"0.0.0.0\": 0}"
  curl -v -X POST -H 'Content-Type: application/json' \
    -d "$res" http://$MASTER:8000/test
  sleep 3
done
