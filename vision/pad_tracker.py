# pad_tracker.py - Mission pad position tracking
from control.drone_interface import state
from config import TEST_MODE
import time

origin_x = 0
origin_y = 0

def get_pad_position():
    # Test mode: simulate pad detection
    if TEST_MODE:
        return True, 0, 0  # Simulate pad at center
        
    try:
        # Debug: Print available state keys
        if len(state) == 0:
            print("[DEBUG] No state data received yet")
            return False, 0, 0
            
        # Debug: Show what keys are available
        if 'padx' not in state or 'pady' not in state:
            print(f"[DEBUG] Pad missing at state: {state}")
            print(f"[DEBUG] Available state keys: {list(state.keys())}")
            return False, 0, 0
            
        if state.get('padx') is None or state.get('pady') is None:
            return False, 0, 0
        padx = int(state['padx'])
        pady = int(state['pady'])
        return True, padx, pady
    except (ValueError, KeyError, TypeError) as e:
        print(f"[DEBUG] Error parsing pad position: {e}")
        return False, 0, 0

def wait_for_pad_origin():
    global origin_x, origin_y
    
    if TEST_MODE:
        print("[INFO] TEST MODE: Bypassing mission pad detection")
        origin_x = 0
        origin_y = 0
        print(f"[INFO] Test origin set at ({origin_x}, {origin_y})")
        return
    
    print("[INFO] Waiting for mission pad to be detected...")
    print("[INFO] Make sure you have a mission pad visible to the drone's bottom camera")
    start_time = time.time()
    timeout = 30  # 30 second timeout
    
    while time.time() - start_time < timeout:
        found, padx, pady = get_pad_position()
        if found:
            origin_x = padx
            origin_y = pady
            print(f"[INFO] Origin set at ({origin_x}, {origin_y})")
            return
        time.sleep(0.5)  # Increased sleep time for less spam
        elapsed = time.time() - start_time
        if elapsed % 5 < 0.5:  # Print every 5 seconds
            print(f"[INFO] Still waiting for pad... ({elapsed:.1f}s elapsed)")
    
    print(f"[ERROR] Mission pad not detected within {timeout} seconds")
    print("[ERROR] Please check:")
    print("  1. Mission pad is visible to the drone's bottom camera")
    print("  2. Mission pad detection is enabled (mon command)")
    print("  3. Mission pad direction is set correctly (mdirection 2)")
    print("  4. Drone is at appropriate height to see the pad")
    print("  5. Or set TEST_MODE = True in config.py to bypass pad detection")
    raise TimeoutError("Mission pad not detected within 30 seconds")
