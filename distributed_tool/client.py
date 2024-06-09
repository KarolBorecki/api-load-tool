from multiprocessing.managers import BaseManager
from queue import Queue
import random, sys, os, time


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


def validate_input(ip_address: str, port: int, number_of_requests: int, number_of_tasks: int, api_url: str) -> None:
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

    if not api_url:
        print("Api url must be specified")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python client.py [server ip] [server port] [number of requests] [number of tasks] [api url]")
        sys.exit(1)

    ip_address, port, number_of_requests, number_of_tasks, api_url = sys.argv[1:6]
    validate_input(ip_address, int(port), int(number_of_requests), int(number_of_tasks), api_url)

    password = os.environ.get('AUTHKEY', "test")
    if not password:
        print("AUTHKEY must be provided in environment variables")
        sys.exit(1)

    payload = {"key": "value"}  # Example payload
    headers = {"Authorization": "Bearer token"}  # Example headers
    request_data = [["GET", api_url, headers, payload] for _ in range(int(number_of_requests))]  # Example request data, adjust as necessary
    main(ip_address, int(port), bytes(password, 'utf-8'), int(number_of_requests), int(number_of_tasks), request_data)
