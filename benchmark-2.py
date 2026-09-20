"""
Benchmark 2: CPU-Bound Work (GIL bottleneck vs. Free-Threading)

This script measures pure mathematical compute time across single-threaded, multi-threaded, and multi-processed implementations.
"""

import sys
import sysconfig
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def is_gil_enabled() -> bool:
    """Check if the GIL is currently enabled in Python 3.13/3.14+."""
    if hasattr(sys, "_is_gil_enabled"):
        return sys._is_gil_enabled()
    # Fallback check for build options
    status = sysconfig.get_config_var("Py_GIL_DISABLED")
    return status != 1

def cpu_heavy_task(n: int) -> int:
    """A CPU-bound function that performs heavy computation in Python."""
    count = 0
    for i in range(n):
        count += i * i
    return count

def run_cpu_benchmark():
    gil_status = "ENABLED" if is_gil_enabled() else "DISABLED"
    print(f"==========================================")
    print(f" Python Version: {sys.version.split()[0]}")
    print(f" Global Interpreter Lock (GIL): {gil_status}")
    print(f"==========================================")

    iterations = 25_000_000
    tasks = [iterations] * 4  # 4 CPU-bound tasks

    # 1. Single Threaded Execution
    start = time.perf_counter()
    for task in tasks:
        cpu_heavy_task(task)
    single_thread_time = time.perf_counter() - start
    print(f"1. Single-Threaded Time:  {single_thread_time:.3f} s")

    # 2. Multi-Threaded Execution (4 Threads)
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(cpu_heavy_task, tasks))
    multi_thread_time = time.perf_counter() - start
    print(f"2. Multi-Threaded Time:   {multi_thread_time:.3f} s")

    # 3. Multi-Processed Execution (4 Processes)
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(cpu_heavy_task, tasks))
    multi_process_time = time.perf_counter() - start
    print(f"3. Multi-Processed Time:  {multi_process_time:.3f} s")

    print("\nPerformance Comparison:")
    print(f"- Threading vs Single Thread: {single_thread_time / multi_thread_time:.2f}x speedup")
    print(f"- Multiprocessing vs Single:  {single_thread_time / multi_process_time:.2f}x speedup")

if __name__ == "__main__":
    run_cpu_benchmark()
