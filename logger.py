# logger.py - CSV logger for flight data (revised)

import os
import csv
import datetime
from config import LOG_FOLDER
from control.drone_interface import state

class FlightLogger:
    def __init__(self):
        # Ensure log directory exists
        os.makedirs(LOG_FOLDER, exist_ok=True)
        # Generate timestamped filename
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = os.path.join(LOG_FOLDER, f'flight_log_{timestamp}.csv')
        # Open file and set up DictWriter with consistent fieldnames
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=[
            'time', 'padx', 'pady', 'error_x', 'error_y',
            'vx', 'vy', 'vz', 'h', 'tof', 'cam'
        ])
        self.writer.writeheader()

    def start(self):
        # Record the start time for elapsed calculations
        self.start_time = datetime.datetime.now()

    def log(self, padx, pady, error_x, error_y, vx, vy, vz, cam):
        """
        Log a single step of flight data.
        - padx, pady: raw pad position offsets
        - error_x, error_y: centering errors
        - vx, vy, vz: commanded velocities
        - cam: current camera mode
        """
        # Read sensor states
        tof = state.get('tof', 'NA')
        h   = state.get('h', 'NA')
        # Compute elapsed time in seconds
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        # Write out all fields in a consistent order
        self.writer.writerow({
            'time':   elapsed,
            'padx':   padx,
            'pady':   pady,
            'error_x': error_x,
            'error_y': error_y,
            'vx':     vx,
            'vy':     vy,
            'vz':     vz,
            'h':      h,
            'tof':    tof,
            'cam':    cam
        })
        # Flush immediately to disk
        self.file.flush()

    def log_step(self, padx, pady, error_x, error_y, vx, vy):
        """
        Convenience wrapper for logging during the orbit phase.
        Assumes no vertical movement (vz=0) and infers camera mode from state.
        """
        cam = state.get('cam', 'NA')
        # Call the full log method with vz=0
        self.log(padx, pady, error_x, error_y, vx, vy, 0, cam)

    def error(self, msg):
        """
        Log an error‐level message to stdout.
        """
        print(f"[ERROR] {msg}")


    def close(self):
        self.file.close()
        print(f"[INFO] Log saved to {self.filename}")

