# logger.py - CSV logger for flight data

import os
import csv
import datetime
from config import LOG_FOLDER
from drone_interface import state

class FlightLogger:
    def __init__(self):
        os.makedirs(LOG_FOLDER, exist_ok=True)
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        self.filename = os.path.join(LOG_FOLDER, f'flight_log_{timestamp}.csv')
        self.file = open(self.filename, 'w', newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['time', 'padx', 'pady', 'error_x', 'error_y', 'vx', 'vy', 'tof', 'h'])

    def start(self):
        self.start_time = datetime.datetime.now()

    def log_step(self, padx, pady, error_x, error_y, vx, vy):
        tof = state.get('tof', 'NA')
        h = state.get('h', 'NA')
        elapsed = (datetime.datetime.now() - self.start_time).total_seconds()
        self.writer.writerow([elapsed, padx, pady, error_x, error_y, vx, vy, tof, h])

    def close(self):
        self.file.close()
        print(f"[INFO] Log saved to {self.filename}")

