import subprocess
import requests
import time 

EDGE_URL = "http://20.203.185.236:31674/api/v1/query_range"
CLOUD_URL = "http://20.250.0.245:32186/api/v1/query_range"

EDGE_VM = "http://20.203.185.236:32077"
CLOUD_VM = "http://20.250.0.245:32077"

queries = {
    "cpu_usage": "sum(rate(container_cpu_usage_seconds_total[30s]))", 
    "memory": "container_memory_usage_bytes",
    "cpu_utilization": "sum(rate(container_cpu_usage_seconds_total[30s])) / count(node_cpu_seconds_total)",
    "memory_utilization": "sum(container_memory_usage_bytes) / sum(machine_memory_bytes)",
}

# call the prometheus API to get the metrics
def get_metrics(query, url, start_time=None, end_time=None):
    r = requests.get(url, params={
        'query': query,
        'start': start_time,
        'end': end_time,
        'step': '15s'
    })
    
    if r.status_code != 200:
        print(f"Failed to fetch metrics for query: {query}, HTTP status: {r.status_code}")
        return None, None

    data = r.json().get("data", {}).get("result", [])
    
    if not data:
        print(f"No data returned for query: {query}")
        return None, None

    values = []
    for result in data:
        for value in result.get("values", []):  # 'values' contains time-series data
            values.append(float(value[1]))  # value[1] is the metric value

    if values:
        return max(values), sum(values) / len(values)
    else:        
        return 0, 0

def work_test(test_cloud : bool, threads = 4, connections = 200):
    url = EDGE_URL
    vm = EDGE_VM
    if (test_cloud):
        url = CLOUD_URL
        vm = CLOUD_VM

    start_time = int(time.time())

    subprocess.run([
        "wrk",
        f"-t{threads}",
        f"-c{connections}",
        "-d2m",
        vm
    ])

    end_time = int(time.time())

    time.sleep(1)

    # log the metrics
    metrics = {}
    for name, q in queries.items():
        peak, avg = get_metrics(q, url, start_time, end_time)
        metrics[name] = {"peak": peak, "avg": avg}

    print(metrics)

print("Begin wrk test...")
tests = [
    [False, 3],
    [True, 3]
]
for testCloud, count in tests:
    for i in range(0, count):
        if (testCloud):
            print("\nTESTING CLOUD VM")
        else:
            print("\nTESTING EDGE VM")
        work_test(testCloud, 8, 400)

