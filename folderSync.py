"""
Author: Alexandre Rodrigues
Email: alexdinis.rodrigues@gmail.com

To run the file 'folderSync.py' in the current directory, use the following command: 
python folderSync.py <source_path> <replica_path> <logfile> <synch_interval>
(for example: python folderSync.py ./source_folder ./replica_folder ./logFile.log 30)
""" 

import filecmp
import logging
import os
import shutil
import sys
import time
from pathlib import Path

# Set up logging configuration to a log file and the console.
def create_logging(logfile):
    logging.basicConfig(
    filename=logfile,
    format="TIME: %(asctime)s -> ACTION: %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
    level=logging.INFO,
    )
    log_name = logging.getLogger()
    log_name.addHandler(logging.StreamHandler())
    return log_name

# Remove a certain replica file and log the action executed.
def remove_file(replica_file, log):
    if replica_file.is_dir():
        shutil.rmtree(replica_file)
        log.info(f"Removed {replica_file}")
    else:
        os.remove(replica_file)
        log.info(f"Removed {replica_file}")

# Synchronize files of source and replica folders.
def folder_synchronization(source_folder, replica_folder, log):
    source_path = Path(source_folder)
    replica_path = Path(replica_folder)
    # Create a source folder if it doesn't exist
    if not source_path.exists():
        os.makedirs(source_path, exist_ok=True)
        log.info(f"Created {source_path}")
    # Create a replica folder if it doesn't exist
    if not replica_path.exists():
        os.makedirs(replica_path, exist_ok=True)
        log.info(f"Created {replica_path}")
    for source_file in source_path.rglob('*'):
        current_path = os.path.relpath(source_file, source_path)
        replica_file = replica_path / current_path
        if source_file.is_dir():
            # If the file updated in source folder is another folder create it inside replica folder 
            if not replica_file.exists():
                os.makedirs(replica_file, exist_ok=True)
                log.info(f"Created {replica_file}")
        else:
            # Copy a file from source folder to replica folder if it doesn't exist in replica folder
            if not replica_file.exists():
                shutil.copy2(source_file, replica_file)
                log.info(f"Created {source_file} and copied to {replica_file}")
            # Copy the new version of a file from source folder to replica folder if it has been updated
            elif not filecmp.cmp(source_file, replica_file, shallow=False):
                shutil.copy2(source_file, replica_file)
                log.info(f"Copied changes from {source_file} to {replica_file}")
    # Remove files from replica folder that no longer exist in source folder
    for replica_file in replica_path.rglob('*'):
        current_path = os.path.relpath(replica_file, replica_path)
        source_file = source_path / current_path
        if not source_file.exists():
            remove_file(replica_file, log)

# Execute synchronization between source and replica folders at defined intervals.
def periodic_synchronization(source_folder, replica_folder, log, synch_interval):
    try:
        while True:
            log.info("Synchronization between folders has started")
            folder_synchronization(source_folder, replica_folder, log)
            log.info("Synchronization between folders has finished")
            time.sleep(synch_interval)
    except KeyboardInterrupt:
        log.info("Synchronization between folders has stopped")

# Check if the command has the correct amount of arguments
nr_args = len(sys.argv)
if nr_args != 5:
    print("The number of arguments inserted in this command is incorrect")
    sys.exit(1)
# Command line args assigned to variables
source_path = sys.argv[1]
replica_path = sys.argv[2]
logfile = sys.argv[3]
synch_interval = int(sys.argv[4])
periodic_synchronization(source_path, replica_path, create_logging(logfile), synch_interval)