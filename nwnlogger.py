#!/usr/bin/env python3

# A python 3 script that you configure with .env and setup with systemd. The idea is to listen for the Neverwinter Nights Process and then copy the logs once the game closes, that way you never
# forget to save them.

import time
import sys
import signal 
import os
import psutil
import select
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv


# Load Enviroment Variables 
load_dotenv()

# Configure Logging 
logging.basicConfig(level=logging.INFO)

# These defaults assume a Ubuntu / Debian based Linux distribution. 

PROC_NAME = os.getenv("PROC_NAME", "nwmain-linux")
# Doing expand user because a lot of the time NWN's logs are in the home directory and just a literal "~" will not suffice
LOG_SOURCE = os.path.expanduser(os.getenv("LOG_SOURCE", "~/.local/share/Neverwinter Nights/logs"))
LOG_OUTPUT = os.getenv("LOG_OUTPUT", "~/NWN Logs")
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN", 120))

def receive_signal(signal, frame):
    logging.info("Stopping Gracefully")
    sys.exit(0)
    
signal.signal(signal.SIGTERM, receive_signal)

def is_running(process:str ) -> int|None:
    """
    Checks to see if the given process string is running.
    """
    for proc in psutil.process_iter(['name']):
        try:
            # check for the process. If it's running, return the ID
            if(process.lower() == proc.info['name'].lower()):
                return proc.pid
        except (psutil.NoSuchProcess, psutil.ZombieProcess, psutil.AccessDenied):
            pass
    # Otherwise return none.
    return None

def persist_logs() -> bool:
    now = datetime.now()
    folder_name = os.path.expanduser(f"{LOG_OUTPUT}/{now.strftime('%Y-%m-%d %H%M%S')} Logs")
    # Ensure our new output directory exists. If it doesn't, make it exist. 
    if not os.path.isdir(folder_name):
        os.makedirs(folder_name)
    
    for file in os.listdir(LOG_SOURCE):
        # Check if the file has the word "log" in it. 
        if("log" in file.lower()):
            logging.info(f"Saving {file} as a log.")
            # If it does, copy it over. 
            shutil.move(f"{LOG_SOURCE}/{file}",folder_name)



def main():
    try:
        while True:
            # Keep checking if NWN is running every 2 minutes. Once it is running, register the process ID
            pid = is_running(PROC_NAME)
            if(pid):
                # Open a file descriptor on that File ID and park it with the kernel. It'll pause execution until the program closes.
                file_descriptor = os.pidfd_open(pid)
                try:
                    select.select([file_descriptor],[],[])
                    # Continues execution here when the program closes. 
                    persist_logs()
                    # Close the descriptor even on a crash.
                finally:
                    # Clean up the file descriptor. 
                    os.close(file_descriptor)
            # Sleep if it's not running for 2 minutes. 
            time.sleep(COOLDOWN_SECONDS)
            
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
    main()