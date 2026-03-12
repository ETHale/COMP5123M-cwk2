import re
import json

file_path = "results.txt"

tests = []
current = {}

with open(file_path) as f:
    for line in f:
        line = line.strip()

        if "TESTING EDGE VM" in line:
            current = {"env": "Edge"}
        elif "TESTING CLOUD VM" in line:
            current = {"env": "Cloud"}

        elif "Latency" in line:
            current["latency_ms"] = float(re.findall(r"Latency\s+([\d\.]+)ms", line)[0])

        elif "Requests/sec:" in line:
            current["requests_sec"] = float(line.split(":")[1].strip())

        elif "Transfer/sec:" in line:
            current["transfer_mb"] = float(re.findall(r"([\d\.]+)", line)[0])

        elif line.startswith("{"):
            metrics = json.loads(line.replace("'", '"'))

            current["cpu_usage_avg"] = metrics["cpu_usage"]["avg"]
            current["cpu_usage_peak"] = metrics["cpu_usage"]["peak"]
            current["memory_avg"] = metrics["memory"]["avg"]
            current["memory_peak"] = metrics["memory"]["peak"]
            current["cpu_util_avg"] = metrics["cpu_utilization"]["avg"]
            current["cpu_util_peak"] = metrics["cpu_utilization"]["peak"]
            current["mem_util_avg"] = metrics["memory_utilization"]["avg"]
            current["mem_util_peak"] = metrics["memory_utilization"]["peak"]

            tests.append(current)

# Print Markdown table
headers = [
    "Environment",
    "Latency(ms)",
    "Req/sec",
    "Transfer(MB/s)",
    "CPU Usage Avg (s)",
    "CPU Usage Peak (s)",
    "Memory Avg (bytes)",
    "Memory Peak (bytes)",
    "CPU Util Avg (%)",
    "CPU Util Peak (%)",
    "Mem Util Avg (%)",
    "Mem Util Peak (%)",
]

print("| " + " | ".join(headers) + " |")
print("|" + " --- |"*len(headers))

for t in tests:
    row = [
        t["env"],
        f"{t['latency_ms']:.2f}",
        f"{t['requests_sec']:.2f}",
        f"{t['transfer_mb']:.2f}",
        f"{t['cpu_usage_avg']:.3f}",
        f"{t['cpu_usage_peak']:.3f}",
        f"{t['memory_avg']:.0f}",
        f"{t['memory_peak']:.0f}",
        f"{t['cpu_util_avg']:.3f}",
        f"{t['cpu_util_peak']:.3f}",
        f"{t['mem_util_avg']:.3f}",
        f"{t['mem_util_peak']:.3f}",
    ]

    print("| " + " | ".join(row) + " |")