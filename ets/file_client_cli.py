import os
import time
import socket
import base64
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import argparse

SERVER_ADDRESS = ('172.16.16.101', 1231)
TEST_FILES = {
    '10MB': 'file_10MB.dat',
    '50MB': 'file_50MB.dat',
    '100MB': 'file_100MB.dat'
}

# ... (fungsi send_command, remote_get, remote_upload, run_stress_test tetap sama) ...


def run_stress_test(operation, size, client_pool_size):
    filename = TEST_FILES[size]
    results = []
    func = remote_upload if operation == 'UPLOAD' else remote_get
    target = filename if operation == 'UPLOAD' else os.path.basename(filename)

    with ThreadPoolExecutor(max_workers=client_pool_size) as executor:
        futures = [executor.submit(func, target) for _ in range(client_pool_size)]
        for future in as_completed(futures):
            try:
                result = future.result()
                if not isinstance(result, dict):
                    result = {
                        'status': 'ERROR',
                        'filename': target,
                        'bytes': 0,
                        'time': 0,
                        'error': 'Invalid result format'
                    }
            except Exception as e:
                result = {
                    'status': 'ERROR',
                    'filename': target,
                    'bytes': 0,
                    'time': 0,
                    'error': str(e)
                }
            results.append(result)
    return results


def main(client_pools, server_pools):
    operations = ['UPLOAD', 'DOWNLOAD']
    sizes = ['10MB', '50MB', '100MB']

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
                        success = sum(1 for r in results if r.get('status') == 'OK')
                        fail = len(results) - success
                        total_bytes = sum(r.get('bytes', 0) for r in results)
                        total_time = sum(r.get('time', 0) for r in results if r.get('time', 0) > 0)
                        throughput = total_bytes / total_time if total_time > 0 else 0
                        writer.writerow([
                            test_no, op, size, c_pool, s_pool,
                            round(total_time, 2), int(throughput),
                            success, fail, success, fail
                        ])
                        print(f"Done test #{test_no} - {op} {size} C:{c_pool} S:{s_pool}")
                        test_no += 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stress test client-server file transfer")
    parser.add_argument('--client-pool', type=int, default=1,
                        help="Daftar ukuran client pool, contoh: 1,5,50")
    parser.add_argument('--server-pool', type=int, default=1,
                        help="Daftar ukuran server pool, contoh: 1,5,50")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    main(args.client_pool, args.server_pool)
