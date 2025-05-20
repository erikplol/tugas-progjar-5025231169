import argparse
import os
import time
import socket
import base64
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

BUFFER_SIZE = 65536  # 64KB
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
                data = sock.recv(BUFFER_SIZE)
                if not data:
                    break
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            return json.loads(data_received)
    except Exception as e:
        return {'status': 'ERROR', 'data': str(e)}

def remote_get(filename=""):
    start_time = time.time()
    command_str = f"GET {filename}\r\n"
    hasil = send_command(command_str)
    elapsed_time = time.time() - start_time

    if hasil and hasil.get('status') == 'OK':
        try:
            namafile = hasil['data_namafile']
            isifile = base64.b64decode(hasil['data_file'])
            with open(namafile, 'wb+') as fp:
                fp.write(isifile)
            print(f"File '{namafile}' berhasil di-download.")
            return {
                'status': 'OK',
                'filename': namafile,
                'bytes': len(isifile),
                'time': elapsed_time,
                'error': None
            }
        except Exception as e:
            print(f"Gagal menulis file: {str(e)}")
            return {
                'status': 'ERROR',
                'filename': filename,
                'bytes': -1,
                'time': elapsed_time,
                'error': str(e)
            }
    else:
        print("Gagal mendapatkan file")
        return {
            'status': 'ERROR',
            'filename': filename,
            'bytes': -1,
            'time': elapsed_time,
            'error': hasil.get('data', 'Unknown error') if hasil else 'No response'
        }

def remote_upload(filepath):
    start_time = time.time()
    try:
        with open(filepath, 'rb') as f:
            file_bytes = f.read()
            encoded = base64.b64encode(file_bytes).decode()

        filename = os.path.basename(filepath)
        command_str = f"UPLOAD {filename}||{encoded}\r\n\r\n"
        hasil = send_command(command_str)
        elapsed_time = time.time() - start_time

        if hasil and hasil.get('status') == 'OK':
            print(f"Berhasil upload file: {filename}")
            return {
                'status': 'OK',
                'filename': filename,
                'bytes': len(file_bytes),
                'time': elapsed_time,
                'error': None
            }
        else:
            print(f"Gagal upload file: {hasil.get('data', 'Unknown error')}")
            return {
                'status': 'ERROR',
                'filename': filename,
                'bytes': -1,
                'time': elapsed_time,
                'error': hasil.get('data', 'Unknown error')
            }
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Gagal upload file: {str(e)}")
        return {
            'status': 'ERROR',
            'filename': filepath,
            'bytes': -1,
            'time': elapsed_time,
            'error': str(e)
        }

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
                        'bytes': -1,
                        'time': -1,
                        'error': 'Invalid result format'
                    }
            except Exception as e:
                result = {
                    'status': 'ERROR',
                    'filename': target,
                    'bytes': -1,
                    'time': -1,
                    'error': str(e)
                }
            results.append(result)
    return results

def run_single_test(args):
    test_no, op, size, client_pools, server_pools = args
    results = run_stress_test(op, size, client_pools)

    success = sum(1 for r in results if r.get('status') == 'OK')
    fail = len(results) - success
    total_bytes = sum(r.get('bytes', 0) for r in results if r.get('bytes', 0) > 0)
    total_time = sum(r.get('time', 0) for r in results if r.get('time', 0) > 0)

    print(f"Total bytes: {total_bytes}, Total time: {total_time}")
    throughput = total_bytes / total_time if total_time > 0 else 0

    row = [
        test_no, op, size, client_pools, server_pools,
        round(total_time, 5), int(throughput),
        success, fail, success, fail
    ]
    print(f"Done test #{test_no} - {op} {size} C:{client_pools} S:{server_pools}")
    return row

def main(client_pools, server_pools):
    operations = ['UPLOAD', 'DOWNLOAD']
    sizes = ['10MB', '50MB', '100MB']

    if not os.path.exists('stress_test_results.csv'):
        with open('stress_test_results.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'Test No', 'Operation', 'Size', 'Client Pool',
                'Server Pool', 'Total Time (s)', 'Throughput (B/s)',
                'Success Client', 'Fail Client', 'Success Server', 'Fail Server'
            ])

    test_no = 1
    all_results = []

    for op in operations:
        for size in sizes:
            args = (test_no, op, size, client_pools, server_pools)
            result = run_single_test(args)
            all_results.append(result)
            test_no += 1

    with open('stress_test_results.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(all_results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Stress test client-server file transfer")
    parser.add_argument('--client-pool', type=int, default=1,
                        help="Ukuran thread pool di sisi klien")
    parser.add_argument('--server-pool', type=int, default=1,
                        help="Ukuran thread pool di sisi server (untuk logging)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    main(args.client_pool, args.server_pool)
