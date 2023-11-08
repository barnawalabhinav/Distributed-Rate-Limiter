#!/bin/bash

cd /home/abhinav/redisraft
if test -f redisraft.so; then
    rm redisraft.so
fi
if test -d build; then
    rm -r build
fi
mkdir build
cd build
cmake ..
make

redis-cli SHUTDOWN
redis-cli -a pass SHUTDOWN

for arg in "$@";
do
    redis-cli -p $arg SHUTDOWN
    redis-server --port $arg --daemonize yes --server_cpulist 0-0 --dbfilename raft$arg.rdb --loadmodule /home/abhinav/redisraft/redisraft.so --raft.log-filename raftlog$arg.db --raft.addr localhost:$arg
done

redis-cli -p $1 raft.cluster init;
for arg in "${@:2}";
do
    redis-cli -p $arg RAFT.CLUSTER JOIN localhost:$1
done;
