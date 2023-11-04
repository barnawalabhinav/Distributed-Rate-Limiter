#!/bin/bash

# Define a variable for the path
REDISRAFT_PATH="/Users/divyanka/redisraft"

# Function to check if Redis is running on a port
is_redis_running() {
    redis-cli -p $1 ping > /dev/null 2>&1
    return $?
}

# Function to wait for Redis to start
wait_for_redis_to_start() {
    local port=$1
    echo "Waiting for Redis to start on port $port..."
    for i in {1..10}; do
        if is_redis_running $port; then
            echo "Redis is now running on port $port."
            return 0
        fi
        sleep 1
    done
    echo "Failed to start Redis on port $port."
    return 1
}

echo "Deleting old redisraft files..."
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
echo "Deleting old redisraft files...done"

# Check if redis-cli and redis-server are in the user's PATH
if ! command -v redis-cli &> /dev/null || ! command -v redis-server &> /dev/null; then
    echo "redis-cli or redis-server not found in PATH"
    exit 1
fi

# Shut down the default Redis server
echo "Shutting down redis server..."
redis-cli SHUTDOWN NOSAVE
sleep 2

# Loop through all arguments
for arg in "$@"; do
    # Shut down the Redis server listening on the port provided in the argument
    echo "Shutting down redis server on port $arg..."
    redis-cli -p $arg SHUTDOWN NOSAVE
    sleep 2
    # Start the Redis server with the specified configurations
    echo "Starting redis server on port $arg..."
    redis-server --port $arg --daemonize yes --dbfilename raft$arg.rdb --loadmodule $REDISRAFT_PATH/redisraft.so --raft.log-filename raftlog$arg.db --raft.addr localhost:$arg
    # Wait for Redis to start before moving on
    wait_for_redis_to_start $arg || exit 1
done

# Initialize the raft cluster on the first port
echo "Initializing raft cluster on port $1..."
redis-cli -p $1 raft.cluster init

# Join the other instances to the raft cluster
for arg in "${@:2}"; do
    echo "Joining raft cluster on port $arg..."
    redis-cli -p $arg RAFT.CLUSTER JOIN localhost:$1 || exit 1
done

echo "Raft cluster configuration complete."
