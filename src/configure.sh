#!/bin/bash

declare -i n_servers=$1+1
declare -i start_port=$2
declare -i port

for off in $(seq 0 $n_servers)
do
    port=$start_port+$off-2
    echo $port
    redis-cli -p $port SHUTDOWN
    redis-server --port $port --daemonize yes --server_cpulist $off-$off
done
