import os
import time
import random
import psutil
import logging
import threading
from pathlib import Path
from statistics import mean, median, stdev

# Setup logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='ssd_benchmark_advanced.log', 
                    filemode='w')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

def write_file(file_path, size_mb):
    try:
        with open(file_path, 'wb') as f:
            f.write(b'\0' * (size_mb * 1024 * 1024))
    except IOError as e:
        logging.error(f"Error writing to file {file_path}: {e}")
        raise

def read_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            f.read()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise

def random_access(file_path, size_mb):
    try:
        with open(file_path, 'r+b') as f:
            for _ in range(1000):  # Arbitrary number of accesses for a simple test
                position = random.randint(0, size_mb * 1024 * 1024 - 1)
                f.seek(position)
                f.read(1)
    except IOError as e:
        logging.error(f"Error during random access on file {file_path}: {e}")
        raise

def small_write(file_path):
    try:
        with open(file_path, 'ab') as f:
            for _ in range(1000):  # Write 1000 small chunks
                f.write(b'\0' * 1024)  # 1KB each
    except IOError as e:
        logging.error(f"Error during small write operations on file {file_path}: {e}")
        raise

def perform_benchmark(operation, file_path, size_mb, results):
    start_time = time.time()
    if operation == 'sequential_write':
        write_file(file_path, size_mb)
    elif operation == 'sequential_read':
        read_file(file_path)
    elif operation == 'random_access':
        random_access(file_path, size_mb)
    elif operation == 'small_write':
        small_write(file_path)
    end_time = time.time()
    results.append(end_time - start_time)

def benchmark(test_file, size_mb, cycles, threads):
    operations = ['sequential_write', 'sequential_read', 'random_access', 'small_write']
    all_results = {op: [] for op in operations}
    
    for _ in range(cycles):
        threads_list = []
        for operation in operations:
            t = threading.Thread(target=perform_benchmark, args=(operation, str(test_file), size_mb, all_results[operation]))
            threads_list.append(t)
            t.start()
        
        for t in threads_list:
            t.join()
    
    detailed_stats = {}
    for operation, times in all_results.items():
        detailed_stats[operation] = {
            'average': mean(times),
            'max': max(times),
            'min': min(times),
            'median': median(times),
            'stdev': stdev(times) if len(times) > 1 else 0
        }
    
    return detailed_stats

def get_available_drives():
    try:
        drives = [p.mountpoint for p in psutil.disk_partitions() if p.fstype]
        if not drives:
            raise ValueError("No writable drives found.")
        return drives
    except Exception as e:
        logging.error(f"Error getting available drives: {e}")
        raise

def main():
    try:
        drives = get_available_drives()
        print("Available drives:")
        for i, drive in enumerate(drives):
            print(f"  {i + 1}. {drive}")
            logging.info(f"Drive {i + 1}: {drive}")

        drive_index = int(input("Select drive by number: ")) - 1
        if drive_index < 0 or drive_index >= len(drives):
            raise ValueError("Invalid drive selection.")

        test_file = Path(drives[drive_index]) / 'test_file.bin'
        print(f"Selected drive: {drives[drive_index]}")
        size_mb = int(input("Enter test file size in MB: "))
        cycles = int(input("Enter number of test cycles: "))
        threads = int(input("Enter number of concurrent threads (e.g., 4): "))

        print("Starting benchmarks...")
        results = benchmark(test_file, size_mb, cycles, threads)
        
        print("\nBenchmark Results:")
        for operation, stats in results.items():
            print(f"  {operation.replace('_', ' ').title()}:")
            print(f"    - Average: {stats['average']:.6f} seconds")
            print(f"    - Max: {stats['max']:.6f} seconds")
            print(f"    - Min: {stats['min']:.6f} seconds")
            print(f"    - Median: {stats['median']:.6f} seconds")
            print(f"    - Standard Deviation: {stats['stdev']:.6f} seconds")
            logging.info(f"{operation.replace('_', ' ').title()}: {stats}")

        # Clean up
        try:
            if test_file.exists():
                test_file.unlink()
                print("Test file cleaned up.")
                logging.info(f"Cleaned up test file: {test_file}")
        except IOError as e:
            logging.warning(f"Could not delete test file {test_file}: {e}")
            print(f"Warning: Could not clean up test file: {e}")

    except ValueError as ve:
        logging.error(f"ValueError in input: {ve}")
        print(f"Error: {ve}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
