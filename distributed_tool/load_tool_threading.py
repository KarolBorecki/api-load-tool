import requests
import concurrent.futures
import json
import random
import time
from multiprocessing import cpu_count

API_URL = 'http://localhost:5000/tasks'


def simulate_load_get(lower_b, upper_b, n_threads, api_url):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        get_tasks = [executor.submit(send_get_request, api_url, None, None) for _ in range(lower_b, upper_b)]

        for future in concurrent.futures.as_completed(get_tasks):
            status_code, response_json, request_time = future.result()
            # print(f"GET request returned status code {status_code} with response: {response_json} in time {request_time:.2f}")
            results.append([status_code, response_json])

    return results


def simulate_load_example(n_requests, n_threads, api_url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        post_tasks = [executor.submit(send_post_request, api_url, None, None) for i in range(n_requests)]

        for future in concurrent.futures.as_completed(post_tasks):
            status_code, result = future.result()
            # print(f"POST request returned status code {status_code} with response: {result}")

        get_tasks = [executor.submit(send_get_request, api_url, None, None) for i in range(1, n_requests + 1)]

        for future in concurrent.futures.as_completed(get_tasks):
            status_code, result = future.result()
            # print(f"GET request returned status code {status_code} with response: {result}")


def simulate_load_post(n_requests, n_threads, api_url):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        post_tasks = [executor.submit(send_post_request, api_url, None, None) for i in range(n_requests)]

        for future in concurrent.futures.as_completed(post_tasks):
            status_code, result = future.result()
            # print(f"POST request returned status code {status_code} with response: {result}")


def send_post_request(api_url, payload=None, headers=None):
    start_time = time.time()
    response = requests.post(api_url,
                             data=json.dumps(payload) if payload else None,
                             headers=headers if headers else None)
    request_time = time.time() - start_time
    return response.status_code, response.json(), request_time


def send_get_request(api_url, payload=None, headers=None):
    start_time = time.time()
    response = requests.get(api_url,
                            data=json.dumps(payload) if payload else None,
                            headers=headers if headers else None)
    request_time = time.time() - start_time

    return response.status_code, response.json(), request_time


def simulate_load(lower_b, upper_b, n_threads, requests_data):
    results = []

    tasks = []
    requests_data_iter = iter(requests_data)
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        for i in range(lower_b, upper_b):
            try:
                http_method, api_url, headers, payload = next(requests_data_iter)
            except StopIteration:
                print(f"No more requests_data... Ending task")
                break

            send_request = send_get_request if http_method.upper() == "GET" else send_post_request
            tasks.append(executor.submit(send_request, api_url, payload, headers))

        for future in concurrent.futures.as_completed(tasks):
            try:
                status_code, response_json, request_time = future.result()
                #print(f"Request returned status code {status_code} with response: {response_json} in time {request_time:.2f}")
                results.append([status_code, response_json, request_time])
            except Exception as e:
                print(f"An error occurred: {e}")
                results.append([None, None, None])


    return results


if __name__ == "__main__":
    n_requests = 100
    n_threads = 100
    print("Starting...")
    start_time = time.time()
    result = simulate_load(0, 100, 10, [
        ["GET", "http://127.0.0.1:5000/tasks/1"] for i in range(10)
    ])
    end_time = time.time()
    print(f"Simulated load with {len(result)} requests in {end_time - start_time:.2f} seconds.")
