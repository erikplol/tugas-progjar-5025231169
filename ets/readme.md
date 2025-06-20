# ETS - Pemrograman Jaringan
1. Membuat file dummy
```
fallocate -l 10M 10MB.dat
fallocate -l 50M 50MB.dat
fallocate -l 100M 100MB.dat
```
2. Server run
- Multiprocess
```
python3 file_server.py --operation server --pool {jumlah pool}
```
- Multithread
```
python3 file_server.py --operation thread --pool {jumlah pool}
```
3. Client run
```
python3 file_client_cli.py --client-pool {jumlah pool} --server-pool {jumlah pool}
```