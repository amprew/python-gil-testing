To install:
```
PYTHON_CONFIGURE_OPTS="--disable-gil" pyenv install 3.14.0
```

Check
```
➜  gil-testing python -c "import sys; print(sys._is_gil_enabled())"      
False
```

# Demystifying the Python GIL: Threads, Processes, and the Free-Threaded Future of Python 3.14

If you have spent any time writing concurrent code in Python, you have likely run into a infamous three-letter acronym: **the GIL** (Global Interpreter Lock).

For decades, the GIL has been both Python’s greatest implementation simplification and its most debated bottleneck. However, Python 3.13 introduced experimental support for removing the GIL (PEP 703), and with **Python 3.14**, free-threading has become significantly more mature, efficient, and accessible.

In this post, we will break down:

1. What threads and processes actually are (and how they differ).

2. What the GIL is and why CPython originally needed it.

3. Why `threading` was still useful **even with** the GIL.

4. How Python 3.14 removes the GIL and makes multithreading truly parallel.

5. Runnable Python code examples to benchmark performance on your own system.

## 1. Threads vs. Processes: What's the Difference?

Before diving into Python specifics, let's establish a clear distinction between **Processes** and **Threads**.

| 

| **Feature** | **Process** | **Thread** | 
| **Memory** | Own isolated memory space. | Shares memory space with parent process. | 
| **Creation Cost** | High (expensive context switching & setup). | Low (lightweight, fast creation). | 
| **Communication** | Requires Inter-Process Communication (IPC, queues, pipes). | Easy (reads/writes shared variables directly). | 
| **Crash Impact** | If one crashes, others remain unaffected. | If one thread causes a fatal crash, the whole process dies. | 

* **Process**: Think of a process as a whole office building. It has its own resources, power supply, and mailroom. If Company A in Building A goes bankrupt, Company B in Building B keeps running.

* **Thread**: Think of threads as workers inside that office building. They share the same desks, coffee machines, and whiteboards (memory). They can talk to each other instantly, but if someone accidentally burns the building down, everyone is affected.

## 2. What is the Python GIL?

The **Global Interpreter Lock (GIL)** is a mutual exclusion lock (mutex) used by CPython—the standard Python implementation—to prevent multiple native threads from executing Python bytecodes at the same time.

### Why did CPython have a GIL in the first place?

1. **Memory Management (Reference Counting):** CPython uses reference counting for garbage collection. Every time an object is referenced, its internal `ob_refcnt` integer increments. If two threads modify this count simultaneously without synchronization, memory leaks or double-free crashes occur. Protecting every object individually would introduce severe overhead; locking the entire interpreter with the GIL was simple and extremely fast for single-threaded programs.

2. **C Extensions Integration:** Many existing C extensions (like `numpy`) depended on thread-unsafe C libraries. The GIL made writing C extensions straightforward.

### The Catch:

Even if your CPU has 16 or 32 physical cores, standard CPython under the GIL only lets **one thread run Python code at a time**.

```
Single-threaded on multi-core CPU with GIL:
[ Core 1 ]  -->  [ Thread 1 Runs ] ------------------------>
[ Core 2 ]  -->  ( Idle / Waiting for GIL )
[ Core 3 ]  -->  ( Idle / Waiting for GIL )
[ Core 4 ]  -->  ( Idle / Waiting for GIL )

```

## 3. Why is Threading Useful *With* the GIL?

If the GIL prevents true multi-core parallel execution of Python code, why do people use `threading` at all?

The answer lies in the distinction between **CPU-bound** and **I/O-bound** tasks:

* **CPU-bound tasks**: Heavy mathematical calculations, image processing, video encoding, matrix operations.

* **I/O-bound tasks**: Network requests (APIs, web scraping), database queries, reading/writing files to disk.

### The GIL Releases During I/O

When a Python thread initiates an I/O operation (like calling `requests.get()` or reading a file), CPython explicitly **releases the GIL**. While Thread A waits for the server to send data over the network, Thread B acquires the GIL and processes its work.

```
I/O-bound concurrency under GIL:
[ Thread 1 (Network) ]  --Releases GIL--> [ Waits for Response ] --Acquires GIL-->
[ Thread 2 (Network) ]                    [ Executes Python ]    --Releases GIL-->

```

Thus, for web scraping, network servers, or file processors, `threading` (and `asyncio`) provides massive speedups even with the GIL active!

## 4. How Threading Gets Faster Without the GIL (Python 3.14)

PEP 703 introduced **Free-Threaded Python**—a build of CPython that disables the GIL entirely. In Python 3.14, free-threading features improved thread safety guarantees, mimalloc memory allocator refinements, and optimized thread-safe reference counting (such as biased reference counting).

Without the GIL, true **parallel execution** becomes possible for CPU-bound tasks across multiple CPU cores:

```
Multi-core execution WITHOUT the GIL (Python 3.14 Free-Threaded):
[ Core 1 ]  -->  [ Thread 1 Runs CPU Work ]  ================>
[ Core 2 ]  -->  [ Thread 2 Runs CPU Work ]  ================>
[ Core 3 ]  -->  [ Thread 3 Runs CPU Work ]  ================>
[ Core 4 ]  -->  [ Thread 4 Runs CPU Work ]  ================>

```

When you scale CPU-bound tasks across multiple threads without the GIL, total execution time drops almost linearly with the number of physical cores available.

## 5. Code Examples & Benchmarks

Run these benchmark scripts to test performance differences on your machine.

### Benchmark 1: I/O-Bound Work (GIL vs. No-GIL both benefit)

This script simulates waiting for I/O (e.g., API requests). Notice how multithreading provides huge performance gains **regardless** of whether the GIL is present.

```
import time
import concurrent.futures

def simulate_io_task(task_id: int) -> float:
    """Simulates a network or disk I/O bound task."""
    time.sleep(0.5)  # Releases the GIL in CPython
    return task_id

def run_io_benchmark():
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

```

### Benchmark 2: CPU-Bound Work (GIL bottleneck vs. Free-Threading)

This script measures pure mathematical compute time across single-threaded, multi-threaded, and multi-processed implementations.

```
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

```

## 6. How to Run Free-Threaded Python 3.14

To test free-threaded execution locally, install a free-threaded Python binary (often named `python3.14t` or compiled with `--disable-gil`).

You can toggle the GIL dynamically on supported builds:

```
# Force GIL ON
python3.14 -X gil=1 cpu_benchmark.py

# Force GIL OFF (Free-threaded mode)
python3.14 -X gil=0 cpu_benchmark.py

```

### Expected Results Matrix:

| **Mode** | **GIL Status** | **Single-Threaded Time** | **Multi-Threaded Time (4 Threads)** | **Multi-Process Time (4 Workers)** | 
| Standard Python | **Enabled** | \~2.0s | **\~2.0s - 2.2s** (No speedup due to GIL) | **\~0.6s** (True multi-core) | 
| Free-Threaded Python | **Disabled** | \~2.1s | **\~0.6s** (True multi-core thread speedup!) | **\~0.6s** (True multi-core) | 

## Summary: When to Use What?

* **Use Threads (`threading` / `ThreadPoolExecutor`)**: For I/O-bound tasks (web requests, file I/O). In Python 3.14 Free-Threaded builds, also use threads for CPU-bound tasks without needing heavy process management!

* **Use Processes (`multiprocessing` / `ProcessPoolExecutor`)**: For CPU-bound tasks in standard GIL-enabled Python builds, or when strict memory isolation between tasks is required.

* **Use Async (`asyncio`)**: For single-threaded, high-concurrency I/O (e.g., thousands of open network sockets).
