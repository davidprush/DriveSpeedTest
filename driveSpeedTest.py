import time
import os
import random
import psutil
import subprocess
import shlex

def check_and_install_tool(tool_name, install_command):
    try:
        subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print(f"{tool_name} not found. Attempting to install...")
        try:
            subprocess.run(shlex.split(install_command), check=True, shell=True)
            print(f"{tool_name} installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {tool_name}: {e}")
    except subprocess.CalledProcessError:
        print(f"{tool_name} is installed but not functioning correctly.")

def verify_sudo():
    """Check if the script is running with sudo privileges."""
    if os.geteuid() != 0:
        print("This script requires superuser privileges. Please run with sudo.")
        exit(1)
    else:
        print("Running with sudo privileges.")

def list_drives():
    """List available block devices, focusing on SSDs and NVMe drives."""
    try:
        # Use lsblk to list block devices, filtering for SSD/NVMe
        result = subprocess.run(["lsblk", "-d", "-o", "NAME,TRAN,TYPE,SIZE"], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')[1:]  # Skip header
        drives = [line.split() for line in lines if line]
        # Filter for SSDs or NVMe drives
        return [d for d in drives if d[1] in ['sata', 'nvme'] or d[2] == 'disk']
    except subprocess.CalledProcessError as e:
        print(f"Failed to list drives: {e}")
        return []

def select_drive():
    """Allow user to select a drive from the list."""
    drives = list_drives()
    if not drives:
        print("No suitable drives found.")
        exit(1)
    
    print("Available drives:")
    for i, drive in enumerate(drives):
        print(f"{i}: {drive[0]} ({drive[2]}, {drive[1]}, {drive[3]})")
    
    while True:
        try:
            choice = int(input("Enter the number of the drive to test: "))
            if 0 <= choice < len(drives):
                return f"/dev/{drives[choice][0]}"
            else:
                print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a number.")

def test_sequential_write(file_path, size_in_mb):
    buffer = bytearray(1024 * 1024)  # 1MB buffer
    start_time = time.time()
    
    with open(file_path, 'wb') as f:
        for _ in range(size_in_mb):
            f.write(buffer)
    
    end_time = time.time()
    speed = size_in_mb / (end_time - start_time)
    return speed

def test_sequential_read(file_path):
    buffer = bytearray(1024 * 1024)  # 1MB buffer
    start_time = time.time()
    
    with open(file_path, 'rb') as f:
        while f.readinto(buffer):
            pass
    
    end_time = time.time()
    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    speed = file_size_mb / (end_time - start_time)
    return speed

def test_random_write(file_path, size_in_mb, block_size_kb=4):
    block_size = block_size_kb * 1024
    buffer = bytearray(block_size)
    file_size = size_in_mb * 1024 * 1024  # Convert MB to bytes
    
    start_time = time.time()
    
    with open(file_path, 'rb+') as f:
        for _ in range(int(size_in_mb * 1024 / block_size_kb)):  # Assume 4KB blocks for simplicity
            offset = random.randint(0, file_size - block_size)
            f.seek(offset)
            f.write(buffer)
    
    end_time = time.time()
    speed = size_in_mb / (end_time - start_time)  # This gives operations per second rather than MB/s
    return speed

def test_random_read(file_path, size_in_mb, block_size_kb=4):
    block_size = block_size_kb * 1024
    file_size = os.path.getsize(file_path)
    if size_in_mb * 1024 * 1024 > file_size:
        print("Warning: Requested read size exceeds file size. Adjusting to file size.")
        size_in_mb = file_size / (1024 * 1024)
    
    start_time = time.time()
    
    with open(file_path, 'rb') as f:
        for _ in range(int(size_in_mb * 1024 / block_size_kb)):
            offset = random.randint(0, file_size - block_size)
            f.seek(offset)
            f.read(block_size)
    
    end_time = time.time()
    speed = size_in_mb / (end_time - start_time)  # This gives operations per second rather than MB/s
    return speed

def large_file_test(file_path, size_in_gb):
    chunk_size = 1024 * 1024 * 1024  # 1GB
    buffer = bytearray(chunk_size)
    start_time = time.time()
    
    with open(file_path, 'wb') as f:
        for _ in range(size_in_gb):
            f.write(buffer)
    
    end_time = time.time()
    speed = size_in_gb / (end_time - start_time)
    return speed

def clear_cache():
    try:
        subprocess.run(shlex.split("sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'"), check=True)
        print("Cache cleared.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clear cache: {e}")

def check_ssd_health(drive_path):
    try:
        result = subprocess.run(["sudo", "smartctl", "-a", drive_path], capture_output=True, text=True, check=True)
        health_status = "Unknown"
        for line in result.stdout.split('\n'):
            if "SMART overall-health self-assessment test result" in line:
                health_status = line.split(':')[1].strip()
        return health_status
    except subprocess.CalledProcessError as e:
        print(f"Failed to check SSD health: {e}")
        return "Error"

def get_system_load():
    load = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    return {
        'cpu_load': load,
        'memory_usage': memory.percent,
        'disk_usage': disk.percent
    }

if __name__ == "__main__":
    # Verify sudo privileges
    verify_sudo()

    # Check and install required tools
    check_and_install_tool("smartctl", "sudo dnf install -y smartmontools")
    check_and_install_tool("pip", "sudo dnf install -y python3-pip")
    subprocess.run(["pip", "install", "--upgrade", "pip"], check=True)
    subprocess.run(["pip", "install", "psutil"], check=True)

    # Let user select drive
    nvme_drive = select_drive()

    test_file = "testfile.bin"
    size_to_test = 1000  # MB for small tests

    # Clear cache before running tests
    clear_cache()

    # Check SSD health for selected drive
    health = check_ssd_health(nvme_drive)
    print(f"Selected Drive Health Status: {health}")

    # System load
    load_info = get_system_load()
    print(f"System Load: CPU={load_info['cpu_load']}%, Memory={load_info['memory_usage']}%, Disk={load_info['disk_usage']}%")

    # Performance tests on selected drive
    print(f"Testing on drive: {nvme_drive}")

    print(f"Testing sequential write speed for {size_to_test}MB...")
    print(f"Write speed: {test_sequential_write(test_file, size_to_test):.2f} MB/s")

    print(f"Testing sequential read speed for {size_to_test}MB...")
    print(f"Read speed: {test_sequential_read(test_file):.2f} MB/s")

    print(f"Testing random write speed for {size_to_test}MB...")
    print(f"Random write speed: {test_random_write(test_file, size_to_test):.2f} ops/s")

    print(f"Testing random read speed for {size_to_test}MB...")
    print(f"Random read speed: {test_random_read(test_file, size_to_test):.2f} ops/s")

    # Large file test - 1GB here
    large_test_file = "testfile_large.bin"
    print(f"Testing write speed for a {size_to_test // 1024}GB file...")
    print(f"Large file write speed: {large_file_test(large_test_file, size_to_test // 1024):.2f} GB/s")

    # Clean up the test files
    os.remove(test_file)
    os.remove(large_test_file)
