# drone_interface.py - Commands and state handling for Tello

import socket
import time
import threading
from config import TELLO_IP, TELLO_CMD_PORT, TELLO_STATE_PORT

cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cmd_sock.bind(('', 9000))
cmd_sock.settimeout(5)

state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
state_sock.bind(('', TELLO_STATE_PORT))
state_sock.settimeout(5)

state = {}
state_thread = None
battery_thread = None
running = True
battery_percent = 0


def tof(self):
    raw = self._read_tof_sensor()
    # clamp between 20 cm and 200 cm
    return max(20, min(raw, 200))



def send(cmd: str, delay: float = 0.03):
    try:
        print(">>", cmd)
        cmd_sock.sendto(cmd.encode(), (TELLO_IP, TELLO_CMD_PORT))
        time.sleep(delay)
    except (socket.error, OSError) as e:
        print(f"[ERROR] Failed to send command '{cmd}': {e}")

def query_battery(timeout: float = 2.0):
    """Query battery percentage from the drone."""
    try:
        cmd_sock.sendto(b"battery?", (TELLO_IP, TELLO_CMD_PORT))
        cmd_sock.settimeout(timeout)
        data, _ = cmd_sock.recvfrom(1024)
        return int(data.decode().strip())
    except (socket.timeout, ValueError, OSError) as e:
        print(f"[WARNING] Battery query failed: {e}")
        return None
    finally:
        cmd_sock.settimeout(5)

def _battery_poller():
    global battery_percent, running
    while running:
        level = query_battery()
        if level is not None:
            battery_percent = level
        time.sleep(5)

def start_battery_monitor():
    global battery_thread
    battery_thread = threading.Thread(target=_battery_poller, daemon=True)
    battery_thread.start()

def stop_battery_monitor():
    global battery_thread
    if battery_thread and battery_thread.is_alive():
        battery_thread.join(timeout=1.0)

def _state_listener():
    global state, running
    while running:
        try:
            data, _ = state_sock.recvfrom(1024)
            parts = data.decode().strip().split(';')
            for item in parts:
                if ':' in item:
                    k, v = item.split(':')
                    state[k] = v
        except socket.timeout:
            continue
        except (socket.error, OSError, UnicodeDecodeError) as e:
            print(f"[ERROR] State listener error: {e}")
            continue

def start_state_reader():
    global state_thread
    state_thread = threading.Thread(target=_state_listener, daemon=True)
    state_thread.start()

def stop_state_reader():
    global running, state_thread
    running = False
    if state_thread and state_thread.is_alive():
        state_thread.join(timeout=1.0)

def cleanup_sockets():
    """Clean up socket resources"""
    try:
        cmd_sock.close()
        state_sock.close()
    except:
        pass

def initialize_drone():
    try:
        print("[INFO] Initializing drone communication...")
        send('command')
        time.sleep(1)
        
        print("[INFO] Enabling video stream...")
        send('streamon')
        time.sleep(2)
        
        print("[INFO] Enabling mission pad detection...")
        send('mon')  # Enable mission pad detection
        time.sleep(1)
        
        print("[INFO] Setting mission pad direction...")
        send('mdirection 2')  # Set mission pad direction to downward
        time.sleep(1)
        
        print("[INFO] Taking off...")
        send('takeoff')
        time.sleep(3)
        
        print("[INFO] Drone initialization complete")
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize drone: {e}")
        raise


