import re
import sys
import statistics

path = sys.argv[1]
with open(path, "r", encoding="utf-8", errors="replace") as f:
    lines = set(f.read().splitlines())

starts = {}
ends = {}
for line in lines:
    m = re.search(r"TIMING START task\(([^)]+)\) (\d+)", line)
    if m:
        starts[m.group(1)] = int(m.group(2))
        continue
    m = re.search(r"TIMING END task\(([^)]+)\) (\d+)", line)
    if m:
        ends.setdefault(m.group(1), []).append(int(m.group(2)))

tasks = sorted(starts.keys() & ends.keys())
if not tasks:
    print("NO TIMING DATA FOUND")
    sys.exit(1)

latencies = []
for t in tasks:
    end = max(ends[t])  # completed can be confirmed by more than one race-free path in theory; take latest
    latencies.append((end - starts[t]) / 1e9)

span = (max(max(ends[t]) for t in tasks) - min(starts[t] for t in tasks)) / 1e9
print(f"tasks_completed={len(tasks)} (starts={len(starts)} ends={len(ends)})")
print(f"protocol_span_s={span:.3f}")
print(f"avg_latency_s={statistics.mean(latencies):.3f}")
print(f"min_latency_s={min(latencies):.3f}")
print(f"max_latency_s={max(latencies):.3f}")
