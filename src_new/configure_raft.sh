#!/bin/bash

# Define a variable for the path
REDISRAFT_PATH="/Users/divyanka/redisraft"

cd $REDISRAFT_PATH
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

# Assuming the `redis-cli` and `redis-server` are in the user's PATH
# Shut down the default Redis server
redis-cli SHUTDOWN
# Attempt to shut down a server with authentication
redis-cli -a pass SHUTDOWN

# Loop through all arguments
for arg in "$@";
do
    # Shut down the Redis server listening on the port provided in the argument
    redis-cli -p $arg SHUTDOWN
    # Start the Redis server with the specified configurations
    redis-server --port $arg --daemonize yes --dbfilename raft$arg.rdb --loadmodule $REDISRAFT_PATH/redisraft.so --raft.log-filename raftlog$arg.db --raft.addr localhost:$arg
done

# Initialize the raft cluster on the first port
redis-cli -p $1 raft.cluster init
# Join the other instances to the raft cluster
for arg in "${@:2}";
do
    redis-cli -p $arg RAFT.CLUSTER JOIN localhost:$1
done
