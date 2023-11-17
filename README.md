# Distributed-Rate-Limiter

Rate Limiter and Throttling System that maintains a consistent rate and limits access to multiple servers.

## Requirements

Redis Version 7.2.0

## How to Run

Migrate to the directory `src`, and

1. Run this command on one terminal/machine for the server.

    ```
    python3 main.py
    ```

2. Set the `REQUEST_IP` to the IP of the server machine in `constants.py` and run this command on another terminal/machine for the clients.

    ```
    python3 client_main.py
    ```

3. One can set the number of clients, the client rates, the rate limit, the number of servers, the number of workers, total runtime from `constants.py`. However, the number of clients and the rates cannot be arbitrarily increased as they depend on the machines capabilities (the number of cores, processing power, etc.)
