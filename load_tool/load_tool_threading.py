import requests
import concurrent.futures
import json
import random
import time

API_URL = 'http://localhost:5000/tasks'

def send_post_request(task_id):
    payload = {
        'title': f'Task {task_id}',
        'description': f'Description for task {task_id}',
        'done': False
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
    return response.status_code, response.json()

def send_get_request(task_id):
    response = requests.get(f"{API_URL}/{task_id}")
    return response.status_code, response.json()

def simulate_load(n_requests, n_threads):
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        post_tasks = [executor.submit(send_post_request, i) for i in range(n_requests)]
        
        for future in concurrent.futures.as_completed(post_tasks):
            status_code, result = future.result()
            print(f"POST request returned status code {status_code} with response: {result}")

        get_tasks = [executor.submit(send_get_request, i) for i in range(1, n_requests+1)]
        
        for future in concurrent.futures.as_completed(get_tasks):
            status_code, result = future.result()
            print(f"GET request returned status code {status_code} with response: {result}")

if __name__ == "__main__":
    n_requests = 100
    n_threads = 10
    start_time = time.time()
    simulate_load(n_requests, n_threads)
    end_time = time.time()
    print(f"Simulated load with {n_requests} requests in {end_time - start_time:.2f} seconds.")
