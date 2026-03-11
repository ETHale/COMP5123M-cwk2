import subprocess
import requests
import time 

EDGE_URL = "http://20.203.185.236:31674/api/v1/query_range"

queries = {
    "cpu": "sum(rate(container_cpu_usage_seconds_total[30s]))", 
    "memory": "container_memory_usage_bytes",
    "cpu_utilization": "sum(rate(container_cpu_usage_seconds_total[30s])) / count(node_cpu_seconds_total)",
    "memory_utilization": "sum(container_memory_usage_bytes) / sum(machine_memory_bytes)",
}

# call the prometheus API to get the metrics
def get_metrics(query, start_time=None, end_time=None):
    r = requests.get(EDGE_URL, params={
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

print("Begin work test...")

start_time = int(time.time())

subprocess.run([
    "wrk",
    "-t4",
    "-c200",
    "-d2m",
    "http://20.203.185.236:32077"
])

end_time = int(time.time())

time.sleep(5)  # wait for metrics to be collected

# log the metrics
metrics = {}
for name, q in queries.items():
    peak, avg = get_metrics(q, start_time, end_time)
    metrics[name] = {"peak": peak, "avg": avg}

print(metrics)