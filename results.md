# Benchmark 1 - Python 3.14

## GIL ON

```
python3.14 -X gil=1 ./benchmark-1.py

==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): ENABLED
==========================================
--- Running 20 I/O-bound tasks ---
Sequential Execution Time: 10.08 seconds
Threaded Execution Time (5 threads): 2.03 seconds
Speedup: 4.96x
```

## GIL OFF

```
python3.14 -X gil=0 ./benchmark-1.py

==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): DISABLED
==========================================
--- Running 20 I/O-bound tasks ---
Sequential Execution Time: 10.08 seconds
Threaded Execution Time (5 threads): 2.02 seconds
Speedup: 4.99x
```

---

# Benchmark 2 - Python 3.14

## GIL ON
```
python3.14 -X gil=1 ./benchmark-2.py

==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): ENABLED
==========================================
1. Single-Threaded Time:  3.949 s
2. Multi-Threaded Time:   3.915 s
3. Multi-Processed Time:  1.144 s

Performance Comparison:
- Threading vs Single Thread: 1.01x speedup
- Multiprocessing vs Single:  3.45x speedup
```

## GIL OFF
```
python3.14 -X gil=0 ./benchmark-2.py

==========================================
 Python Version: 3.14.0
 Global Interpreter Lock (GIL): DISABLED
==========================================
1. Single-Threaded Time:  4.011 s
2. Multi-Threaded Time:   1.619 s
3. Multi-Processed Time:  1.149 s

Performance Comparison:
- Threading vs Single Thread: 2.48x speedup
- Multiprocessing vs Single:  3.49x speedup
```