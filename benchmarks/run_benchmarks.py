#!/usr/bin/env python3
"""
DedupFS Native C++17 Benchmark CLI Wrapper
Executes the compiled C++17 Benchmarking Engine (./bin/dedupfs benchmark)
for 100% algorithmic fairness, zero interpreter overhead, and POSIX I/O symmetry.
"""

import sys
import subprocess
from pathlib import Path

def main():
    root = Path(__file__).resolve().parent.parent
    bin_path = root / "bin" / "dedupfs"
    
    if not bin_path.exists():
        print(f"[ERROR] DedupFS binary not found at {bin_path}. Compiling via 'make all'...")
        subprocess.run(["make", "all"], cwd=str(root), check=True)
        
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "datasets/test_small_250MB/work"
    cmd = [str(bin_path), "benchmark", str(target_dir)]
    if len(sys.argv) > 2:
        cmd.extend(sys.argv[2:])
        
    res = subprocess.run(cmd, cwd=str(root))
    sys.exit(res.returncode)

if __name__ == "__main__":
    main()
