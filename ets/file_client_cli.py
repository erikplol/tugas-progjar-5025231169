import os
import time
import socket
import base64
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

SERVER_ADDRESS = ('172.16.16.101', 1231)
TEST_FILES = {
    '10MB': 'file_10MB.dat',
    '50MB': 'file_50MB.dat',
    '100MB': 'file_100MB.dat'
}

def send_command(command_str):
    try:
        with socket.create_connection(SERVER_ADDRESS) as sock:
            sock.sendall((command_str + "\r\n\r\n").encode())
            data_received = ""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            return json.loads(data_received)
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}

def upload_worker(filepath):
    try:
        with open(filepath, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        filename = os.path.basename(filepath)
        command = f"UPLOAD {filename}||{encoded}"
        start = time.time()
        result = send_command(command)
        end = time.time()
        return {
            'status': result['status'],
            'time': end - start,
            'bytes': os.path.getsize(filepath) if result['status'] == 'OK' else 0
        }
    except Exception as e:
        return {'status': 'ERROR', 'time': 0, 'bytes': 0}

def download_worker(filename):
    command = f"GET {filename}"
    start = time.time()
    result = send_command(command)
    end = time.time()
    if result['status'] == 'OK':
        return {
            'status': 'OK',
            'time': end - start,
            'bytes': len(base64.b64decode(result['data_file']))
        }
    return {'status': 'ERROR', 'time': 0, 'bytes': 0}

def run_stress_test(operation, size, client_pool_size):
    filename = TEST_FILES[size]
    results = []
    func = upload_worker if operation == 'UPLOAD' else download_worker
    target = filename if operation == 'UPLOAD' else os.path.basename(filename)

    with ThreadPoolExecutor(max_workers=client_pool_size) as executor:
        futures = [executor.submit(func, target) for _ in range(client_pool_size)]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def main():
    operations = ['UPLOAD', 'DOWNLOAD']
    sizes = ['10MB', '50MB', '100MB']
    client_pools = [1, 5, 50]
    server_pools = [1, 5, 50]
    
    with open('stress_test_results.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            'Nomor', 'Operasi', 'Volume', 'Client Pool', 'Server Pool',
            'Waktu Total per Client (s)', 'Throughput per Client (B/s)',
            'Client Sukses', 'Client Gagal', 'Server Sukses', 'Server Gagal'
        ])

        test_no = 1
        for op in operations:
            for size in sizes:
                for c_pool in client_pools:
                    for s_pool in server_pools:
                        results = run_stress_test(op, size, c_pool)
                        success = sum(1 for r in results if r['status'] == 'OK')
                        fail = len(results) - success
                        total_time = sum(r['time'] for r in results) / len(results)
                        total_bytes = sum(r['bytes'] for r in results)
                        throughput = total_bytes / sum(r['time'] for r in results) if results else 0
                        writer.writerow([
                            test_no, op, size, c_pool, s_pool,
                            round(total_time, 2), int(throughput),
                            success, fail, success, fail
                        ])
                        print(f"Done test #{test_no} - {op} {size} C:{c_pool} S:{s_pool}")
                        test_no += 1

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    main()