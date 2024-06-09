import json
import sys
import os
import time
from multiprocessing.managers import BaseManager
from queue import Queue


class QueueManager(BaseManager):
    pass


def create_scopes(number_of_requests: int, number_of_tasks: int) -> list[tuple[int, int]]:
    res_table = []

    base_requests_per_task = number_of_requests // number_of_tasks
    remaining_requests = number_of_requests % number_of_tasks

    start_index = 0
    for i in range(number_of_tasks):
        requests_for_this_task = base_requests_per_task + (1 if i < remaining_requests else 0)
        end_index = start_index + requests_for_this_task
        res_table.append((start_index, end_index))
        start_index = end_index

    return res_table


def sent_data(number_of_requests: int, number_of_tasks: int, request_data: list, in_queue: Queue) -> None:
    scopes = create_scopes(number_of_requests, number_of_tasks)
    for scope in scopes:
        data_tuple = (scope, request_data)
        print("Data sent to worker: ", data_tuple)
        in_queue.put(data_tuple)


def collect_results(tasks: int, number_of_requests: int, out_queue: Queue) -> list[None | list]:
    received_results = 0
    whole_result = [None for _ in range(number_of_requests)]
    while received_results < tasks:
        partial_result = out_queue.get()
        received_results += 1

        scope, requests_stats = partial_result
        print(f"Got partial result for scope: {scope} from worker with result: {requests_stats}")

        start, stop = scope
        whole_result[start:stop] = requests_stats
        print(f"Appended partial result to whole result: {whole_result[:3]}...{whole_result[-3:]} \n")

    return whole_result


def main(ip_address: str, port: int, password: bytes, number_of_requests: int, number_of_tasks: int,
         request_data: list) -> None:
    QueueManager.register("in_queue")
    QueueManager.register("out_queue")

    manager = QueueManager(address=(ip_address, port), authkey=password)
    manager.connect()

    sent_data(number_of_requests, number_of_tasks, request_data, in_queue=manager.in_queue())
    print("\n\nData sent from client to server. Waiting for results...")
    start_time = time.time()
    result = collect_results(number_of_tasks, number_of_requests, out_queue=manager.out_queue())
    end_time = time.time()
    print("Got all results from workers: ", result)

    elapsed_time = end_time - start_time
    print(f"It took: {elapsed_time:.2f}s")


def load_requests_from_file(file_path: str) -> list:
    try:
        with open(file_path, 'r') as file:
            request_data = json.load(file)
        return request_data
    except Exception as e:
        print(f"Failed to read requests from file: {e}")
        sys.exit(1)


def validate_input(ip_address: str, port: int, number_of_requests: int, number_of_tasks: int) -> None:
    if port <= 0:
        print("Port must be greater than 0")
        sys.exit(1)

    if not ip_address:
        print("IP address must be provided")
        sys.exit(1)

    if number_of_requests <= 0:
        print("Number of requests must be greater than 0")
        sys.exit(1)

    if number_of_tasks <= 0:
        print("Number of tasks must be greater than 0")
        sys.exit(1)

    if number_of_requests < number_of_tasks:
        print("Number of requests should be greater than number of tasks")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print(
            f"Expected 5 args, got {len(sys.argv)}.\n"
            f"Usage: python client.py [server ip] [server port] [number of tasks] [--f file_path]")
        sys.exit(1)

    ip_address = sys.argv[1]
    port = int(sys.argv[2])
    number_of_tasks = int(sys.argv[3])
    file_path = sys.argv[5]

    if sys.argv[4] != '--f':
        print("The fourth argument must be --f followed by the file path")
        sys.exit(1)

    tests_data = load_requests_from_file(file_path)

    for test_num, test_data in enumerate(tests_data):
        print(f"Starting test number {test_num + 1}")

        if not isinstance(test_data, dict) or not all(k in test_data for k in ["number_of_requests", "method", "url", "headers", "payload"]):
            print("Each request data should be a dictionary with keys: number_of_requests, method, url, headers, payload")
            sys.exit(1)

        number_of_requests = test_data["number_of_requests"]
        method = test_data["method"]
        url = test_data["url"]
        headers = test_data["headers"]
        payload = test_data["payload"]

        request_data = [[method, url, headers, payload] for _ in range(number_of_requests)]
        password = os.environ.get('AUTHKEY', "test")
        if not password:
            print("AUTHKEY must be provided in environment variables")
            sys.exit(1)

        validate_input(ip_address, port, number_of_requests, number_of_tasks)
        main(ip_address, port, bytes(password, 'utf-8'), number_of_requests, number_of_tasks, request_data)

        print(f"Finished test number {test_num + 1}")
