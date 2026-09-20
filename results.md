# Benchmark 1

## 3.14 - GIL ON
```
➜  gil-testing python ./benchmark-2.py
==========================================
 Python Version: 3.14.5
 Global Interpreter Lock (GIL): ENABLED
==========================================
1. Single-Threaded Time:  4.152 s
2. Multi-Threaded Time:   4.043 s
3. Multi-Processed Time:  1.180 s

Performance Comparison:
- Threading vs Single Thread: 1.03x speedup
- Multiprocessing vs Single:  3.52x speedup
```

## 3.14 - GIL OFF
```
==========================================
 Python Version: 3.14.5
 Global Interpreter Lock (GIL): ENABLED
==========================================
--- Running 20 I/O-bound tasks ---
Sequential Execution Time: 10.06 seconds
Threaded Execution Time (5 threads): 2.03 seconds
Speedup: 4.96x
```

## 3.14 - GIL OFF
```
==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): DISABLED
==========================================
--- Running 20 I/O-bound tasks ---
Sequential Execution Time: 10.08 seconds
Threaded Execution Time (5 threads): 2.02 seconds
Speedup: 4.98x
```

# Benchmark 2 --

## 3.14 - GIL OFF
```
➜  gil-testing python ./benchmark-2.py    
==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): DISABLED
==========================================
1. Single-Threaded Time:  3.981 s
2. Multi-Threaded Time:   1.310 s
3. Multi-Processed Time:  1.309 s

Performance Comparison:
- Threading vs Single Thread: 3.04x speedup
- Multiprocessing vs Single:  3.04x speedup
➜  gil-testing python local 3.12
```