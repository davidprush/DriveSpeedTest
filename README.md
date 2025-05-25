# DriveSpeedTest
A simple Python program to test the speed of a drive.
# Drive Performance Testing Script

This script is designed for Fedora Linux on ARM64, specifically for testing NVMe drives. It checks for required tools, verifies sudo privileges, lists available drives, and allows for performance testing on a user-selected drive.

## Installation

Before running this script:

1. **Ensure you have `sudo` access** on your system.
2. **Install Python 3** if not already installed (`sudo dnf install python3`).

## How to Run

- **Command**: Run the script with elevated privileges:
  ```bash
  sudo python3 DriveSpeedTest.py
  ```

## Features
- Sudo Verification: Checks if the script is running with superuser privileges to ensure all operations can be performed.
- Tool Installation: Automatically checks for and installs smartmontools and pip if not present, ensuring all necessary utilities are available.
- Drive Listing: Lists available block devices, focusing on SSDs and NVMe drives using lsblk.
- Drive Selection: Allows user interaction to select a drive for testing from a displayed list.

## Performance Tests: 
- Sequential Write/Read: Measures speed for writing/reading data in a sequential manner.
- Random Write/Read: Tests performance with random I/O operations, simulating real-world scenarios.
- Large File Write: Writes a large file to assess performance over larger data sets.
- Health Status: Checks the health of the selected drive using SMART data via smartctl.
- Cache Management: Clears system cache before tests to ensure results are not impacted by cached data.
- System Load: Displays system load information (CPU, memory, disk usage) to contextualize performance test results.

## Notes

- Drive Selection: 
The script uses lsblk to list drives. It filters for SATA and NVMe drives or those identified as 'disk'. 
The user selects the drive by entering a number corresponding to the listed drive.

- Performance Testing:
Tests are performed on a temporary file created on the selected drive. 
Sequential tests use a 1MB buffer, while random tests use a 4KB block size for operations.

- Permissions: 
Running with sudo is necessary for cache clearing, checking SSD health, and possibly executing some performance tests.
Error Handling:
If no suitable drives are found, or there's an issue with listing drives, the script will inform or exit accordingly.

- User Interaction:
The script requires user input for drive selection, making it less suitable for automated scenarios but highly interactive for manual testing.
Environment: 
Tailored for Fedora on ARM64 with NVMe drives. Adjustments might be needed for other Fedora versions or different architectures.

## Limitations
- Manual Drive Selection: Requires user input, which might not be ideal for automation or batch testing scenarios.
- Specific to Fedora: The script uses Fedora-specific commands for installation. Users of other distributions would need to adjust package installation commands.
- NVMe/SATA Focus: The drive listing might miss other types of storage devices, like USB or optical drives.
- Performance Variability: Test results can vary based on current system load, drive health, and other environmental factors; thus, multiple runs might be necessary for reliability.
- Cache Clearance: The method used for cache clearing might not be comprehensive for all situations or might not clear all relevant caches on all systems.

## Potential Improvements
- Automated Drive Selection: Implement options for automatic drive selection or configuration through command-line arguments for automation.
- Error Logging: Add more detailed error logging to help diagnose issues encountered during execution.
- Broadened Drive Detection: Expand drive type detection to include other storage technologies like USB drives or network storage.
- Multi-Drive Testing: Allow for simultaneous or sequential testing of multiple drives for comparative analysis.
- Advanced Benchmarking: Integrate with or support other benchmarking tools for more comprehensive testing scenarios.
- Performance Consistency: Implement methods to run tests multiple times and provide average results or handle cache differently for consistency.
- Cross-Distribution Compatibility: Generalize the script or provide variants for different Linux distributions.
- User Interface: Enhance user interaction with a more intuitive interface, possibly through a CLI tool or GUI for non-command-line users.
- Script Modularization: Break down the script into more modular components for easier maintenance and expansion.

***Remember, performance results can vary based on current system load, drive health, and other factors. Multiple runs might be necessary to get a reliable average.***
