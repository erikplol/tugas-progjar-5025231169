# ETS - Pemrograman Jaringan
1. Membuat file dummy
```
fallocate -l 10M file_10MB.dat
fallocate -l 50M file_50MB.dat
fallocate -l 100M file_100MB.dat
```
2. Server run
- Multiprocess
```
python3 file_server_multiprocess_pool.py
```
- Multithread
```
python3 file_server_multithread_pool.py
```
