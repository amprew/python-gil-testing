"""
Benchmark 1: I/O-Bound Work (GIL vs. No-GIL both benefit)

This script simulates waiting for I/O (e.g., API requests). Notice how multithreading provides huge performance gains regardless of whether the GIL is present.
"""
import time
import sys
import sysconfig
import concurrent.futures

def is_gil_enabled() -> bool:
    """Check if the GIL is currently enabled in Python 3.13/3.14+."""
    if hasattr(sys, "_is_gil_enabled"):
        return sys._is_gil_enabled()
    return sysconfig.get_config_var("Py_GIL_DISABLED") != 1

def simulate_io_task(task_id: int) -> float:
    """Simulates a network or disk I/O bound task."""
    time.sleep(0.5)  # Releases the GIL in CPython
    return task_id

def run_io_benchmark():
    gil_status = "ENABLED" if is_gil_enabled() else "DISABLED"
    print("==========================================")
    print(f" Python Version: {sys.version.split()[0]}")
    print(f" Global Interpreter Lock (GIL): {gil_status}")
    print("==========================================")

    num_tasks = 20
    print(f"--- Running {num_tasks} I/O-bound tasks ---")

    # Sequential execution
    start_time = time.perf_counter()
    for i in range(num_tasks):
        simulate_io_task(i)
    seq_time = time.perf_counter() - start_time
    print(f"Sequential Execution Time: {seq_time:.2f} seconds")

    # Threaded execution (5 workers)
    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        list(executor.map(simulate_io_task, range(num_tasks)))
    thread_time = time.perf_counter() - start_time
    print(f"Threaded Execution Time (5 threads): {thread_time:.2f} seconds")
    print(f"Speedup: {seq_time / thread_time:.2f}x\n")

if __name__ == "__main__":
    run_io_benchmark()
