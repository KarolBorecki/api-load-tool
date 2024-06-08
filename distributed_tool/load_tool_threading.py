import requests
import concurrent.futures
import json
import random
import time
from multiprocessing import cpu_count

API_URL = 'http://localhost:5000/tasks'


def send_post_request(task_id, api_url):
    payload = {
        'title': f'Task {task_id}',
        'description': f'Description for task {task_id}',
        'done': False
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)
    return response.status_code, response.json()


def send_get_request(task_id, api_url):
    response = requests.get(f"{api_url}/{task_id}")
    return response.status_code, response.json()


def simulate_load_example(n_requests, n_threads, api_url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        post_tasks = [executor.submit(send_post_request, i, api_url) for i in range(n_requests)]

        for future in concurrent.futures.as_completed(post_tasks):
            status_code, result = future.result()
            print(f"POST request returned status code {status_code} with response: {result}")

        get_tasks = [executor.submit(send_get_request, i, api_url) for i in range(1, n_requests + 1)]

        for future in concurrent.futures.as_completed(get_tasks):
            status_code, result = future.result()
            print(f"GET request returned status code {status_code} with response: {result}")


def simulate_load_get(lower_b, upper_b, n_threads, api_url):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        get_tasks = [executor.submit(send_get_request, i, api_url) for i in range(lower_b, upper_b)]

        for future in concurrent.futures.as_completed(get_tasks):
            status_code, result = future.result()
            print(f"GET request returned status code {status_code} with response: {result}")
            results.append([status_code, result])

    return results

def simulate_load(lower_b, upper_b, n_threads, requests_data):
    results = []

    tasks = []
    requests_data_iter = iter(requests_data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        for i in range(lower_b, upper_b):
            http_method, api_url = next(requests_data_iter)
            send_request = send_get_request if http_method.upper() == "GET" else send_post_request
            tasks.append(executor.submit(send_request, i, api_url))

        for future in concurrent.futures.as_completed(tasks):
            status_code, result = future.result()
            print(f"Request returned status code {status_code} with response: {result}")
            results.append([status_code, result])

    return results



def simulate_load_post(n_requests, n_threads, api_url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        post_tasks = [executor.submit(send_post_request, i, api_url) for i in range(n_requests)]

        for future in concurrent.futures.as_completed(post_tasks):
            status_code, result = future.result()
            print(f"POST request returned status code {status_code} with response: {result}")


if __name__ == "__main__":
    n_requests = 100
    n_threads = 100
    start_time = time.time()
    simulate_load(n_requests, n_threads, API_URL)
    end_time = time.time()
    print(f"Simulated load with {n_requests} requests in {end_time - start_time:.2f} seconds.")
