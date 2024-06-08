# api-load-tool

Usage:

1. Start server from distributed_tool/server.py
    ```shell 
   python3 server.py [ip_address] [port]
    ```
2. Start workers from distributed_tool/worker.py that will listen for incoming tasks from server
    ```shell
   python3 worker.py [ip_address] [port] [number of tasks]
    ```
3. Run client from distributed_tool/client.py that will divide data and send them to active workers
    ```shell
   python3 client.py [ip_address] [port] [number of requests] [number of tasks] [api_url]
    ```