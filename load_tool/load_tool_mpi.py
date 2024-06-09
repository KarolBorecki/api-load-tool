from mpi4py import MPI
import requests
import json
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

def simulate_requests(task_id, request_type):
    if request_type == 'POST':
        return send_post_request(task_id)
    elif request_type == 'GET':
        return send_get_request(task_id)
    else:
        raise ValueError("Invalid request type")

def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    n_requests = 100  
    request_type = 'POST' if rank % 2 == 0 else 'GET'  

    task_ids = list(range(rank, n_requests, size))

    results = []
    for task_id in task_ids:
        status_code, response = simulate_requests(task_id, request_type)
        results.append((status_code, response))
        print(f"Process {rank}: {request_type} request returned status code {status_code} with response: {response}")

if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print(f"Simulation completed in {end_time - start_time:.2f} seconds.")
