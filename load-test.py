from locust import HttpUser, task, between, events, runners
import random
import statistics
import os
import json

API_ENDPOINT = "/render"
payloads = []
request_durations = []
response_codes = []
payload_folder = "./payloads"

for filename in os.listdir(payload_folder):
    if filename.endswith(".json"):
        with open(os.path.join(payload_folder, filename), 'r') as file:
            payload = json.load(file)
            payloads.append(payload)

if not payloads:
    raise Exception("No JSON payloads found in the 'payloads' directory.")

class LoadTester(HttpUser):
    wait_time = between(0.1, 0.5)

    @task
    def post_request(self):
        payload = random.choice(payloads)
        with self.client.post(API_ENDPOINT, json=payload, catch_response=True) as response:
            request_durations.append(response.elapsed.total_seconds())
            response_codes.append(response.status_code)

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Calculate statistics after the load test is complete."""
    if request_durations:
        avg_duration = statistics.mean(request_durations)
        stddev_duration = statistics.stdev(request_durations) if len(request_durations) > 1 else 0
        
        print("\n=== Load Test Results ===")
        print(f"Total requests: {len(request_durations)}")
        print(f"Average request duration: {avg_duration:.4f} seconds")
        print(f"Standard deviation of request duration: {stddev_duration:.4f} seconds")
        print("Response code distribution:")
        for code in set(response_codes):
            print(f"  {code}: {response_codes.count(code)} responses")

# Usage:
# Run the script using Locust, specifying the number of users (concurrency level) and spawn rate:
# locust -f path/to/script.py --host=https://<api-host> --users 100 --spawn-rate 10
