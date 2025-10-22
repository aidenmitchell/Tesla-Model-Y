#!/usr/bin/env python3

with open('scanlog.txt', 'r') as f:
    lines = [l.strip() for l in f.readlines()]

successful_pids = []
for i in range(len(lines) - 1):
    if lines[i].startswith('> 22') and len(lines[i]) == 8:
        pid = lines[i][3:7]
        next_line = lines[i+1]
        if next_line and not next_line.startswith('>'):
            if 'NO DATA' not in next_line and next_line != 'OK':
                if any(next_line.startswith(prefix) for prefix in ['788', '78A', '798', '7A8', '7AA', '7B8', '7E8']):
                    successful_pids.append((pid, next_line[:3], next_line))

print(f"Found {len(successful_pids)} PIDs that got responses")

unique_pids = sorted(set([p[0] for p in successful_pids]))
print(f"\nUnique PIDs with data ({len(unique_pids)} total):")
for pid in unique_pids[:80]:
    ecus = sorted(set([ecu for p, ecu, _ in successful_pids if p == pid]))
    print(f"0x{pid} ({int(pid, 16):4d}) - ECUs: {', 0x'.join(ecus)}")

print("\n\nSample responses:")
for pid, ecu, response in successful_pids[:20]:
    print(f"PID 0x{pid} -> {response}")
