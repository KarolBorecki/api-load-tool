import requests
import json
import random
import time
from multiprocessing import Pool, cpu_count

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

def simulate_post_requests(n_requests):
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(send_post_request, range(n_requests))
    for status_code, result in results:
        print(f"POST request returned status code {status_code} with response: {result}")

def simulate_get_requests(n_requests):
    with Pool(processes=cpu_count()) as pool:
        results = pool.map(send_get_request, range(1, n_requests + 1))
    for status_code, result in results:
        print(f"GET request returned status code {status_code} with response: {result}")

if __name__ == "__main__":
    n_requests = 100
    start_time = time.time()
    print("Simulating POST requests...")
    simulate_post_requests(n_requests)
    print("Simulating GET requests...")
    simulate_get_requests(n_requests)
    end_time = time.time()
    print(f"Simulated load with {n_requests} POST and GET requests in {end_time - start_time:.2f} seconds.")
