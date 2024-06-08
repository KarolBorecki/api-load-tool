from multiprocessing.managers import BaseManager
from queue import Queue
import sys, os, time
from load_tool_threading import simulate_load


class QueueManager(BaseManager):
    pass


def process_single_task(in_queue: Queue, out_queue: Queue) -> None:
    data_tuple = in_queue.get()
    start_time = time.time()
    scope, request_data = data_tuple

    print(f"I got task scope: {scope}")
    start, stop = scope
    task_data = request_data[start:stop]

    request_responses_data = simulate_load(start, stop, 10, task_data)

    out_queue.put((scope, request_responses_data))
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(
        f"[{elapsed_time} s] Result for task scope: {scope} is: {request_responses_data[:3]}...{request_responses_data[-3:]}")


def process_tasks(in_queue: Queue, out_queue: Queue, amount_of_tasks: int) -> None:
    task_count = 0
    while amount_of_tasks == -1 or task_count < amount_of_tasks:
        process_single_task(in_queue, out_queue)
        task_count += 1
        print(f"Result sent to server ({task_count}/{amount_of_tasks if amount_of_tasks != -1 else '∞'})")
        print("-" * 50)


def main(ip_address: str, port: int, password: bytes, amount_of_tasks: int) -> None:
    print("Connecting to server")
    QueueManager.register("in_queue")
    QueueManager.register("out_queue")
    manager = QueueManager(address=(ip_address, port), authkey=password)
    manager.connect()

    print("Worker connected to server")
    in_queue = manager.in_queue()
    out_queue = manager.out_queue()

    process_tasks(in_queue, out_queue, amount_of_tasks)
    print("All results sent to server")


def validate_input(ip_address: str, port: int, amount_of_tasks: int) -> None:
    if port <= 0:
        print("Port must be greater than 0")
        sys.exit(1)

    if not ip_address:
        print("IP address must be provided")
        sys.exit(1)

    if amount_of_tasks <= 0 and amount_of_tasks != -1:
        print("Amount of tasks must be greater than 0 or equal to -1")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(
            "Usage: python worker.py [server ip] [server port] [amount of tasks after which worker will shutdown | -1 for infinite tasks]")
        sys.exit(1)
    ip_address, port, amount_of_tasks = sys.argv[1:4]
    validate_input(ip_address, int(port), int(amount_of_tasks))

    password = os.environ.get('AUTHKEY', "test")
    if not password:
        print("AUTHKEY must be provided in environment variables")
        sys.exit(1)

    main(ip_address, int(port), bytes(password, 'utf-8'), int(amount_of_tasks))
