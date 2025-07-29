# precision_landing.py - Modular layered descent landing

from drone_interface import send, state
from pad_tracker import get_pad_position
from config import (LAND_ALTITUDES, LAND_THRESHOLD, STABLE_COUNT_REQUIRED,
                   LAND_ALIGNMENT_ITERATIONS, LAND_ALIGNMENT_DELAY,
                   LAND_DESCENT_DISTANCE, LAND_DESCENT_DELAY)
import time

def is_aligned(error_x, error_y):
    return abs(error_x) < LAND_THRESHOLD and abs(error_y) < LAND_THRESHOLD

def send_alignment_command(error_x, error_y):
    # More aggressive alignment for better precision
    vx = max(-20, min(20, int(error_x * 0.8)))
    vy = max(-20, min(20, int(error_y * 0.8)))
    send(f"rc {vx} {vy} 0 0")

def get_current_altitude():
    """Get current altitude from drone state"""
    try:
        return int(state.get('h', 0))
    except (ValueError, TypeError):
        return 0

def descend_to_altitude(target_altitude):
    """Descend to a specific altitude using relative movement"""
    current_alt = get_current_altitude()
    if current_alt == 0:
        print("[WARNING] Could not get current altitude, using default descent")
        send(f"go 0 0 -{LAND_DESCENT_DISTANCE} 20")
        time.sleep(LAND_DESCENT_DELAY)
        return
    
    descent_needed = current_alt - target_altitude
    if descent_needed <= 0:
        print(f"[INFO] Already at or below target altitude {target_altitude}cm")
        return
    
    print(f"[INFO] Descending from {current_alt}cm to {target_altitude}cm ({descent_needed}cm)")
    
    # Use relative movement to descend
    send(f"go 0 0 -{descent_needed} 20")
    time.sleep(LAND_DESCENT_DELAY)
    
    # Verify descent
    new_alt = get_current_altitude()
    print(f"[INFO] New altitude: {new_alt}cm")

def precision_land():
    print("[INFO] Starting precision landing")
    current_altitude = get_current_altitude()
    print(f"[INFO] Starting altitude: {current_altitude}cm")
    
    for i, target_alt in enumerate(LAND_ALTITUDES):
        print(f"[INFO] Aligning at layer {i+1} (target: {target_alt}cm)")
        stable_count = 0
        pad_lost_count = 0
        
        # First descend to the target altitude
        descend_to_altitude(target_alt)
        
        # Then align at this altitude
        for iteration in range(LAND_ALIGNMENT_ITERATIONS):
            found, padx, pady = get_pad_position()
            if not found:
                pad_lost_count += 1
                if pad_lost_count > 10:  # If pad lost for too long, abort
                    print(f"[WARNING] Pad lost for too long at layer {i+1}, aborting landing")
                    send("rc 0 0 0 0")
                    return False
                send("rc 0 0 0 0")
                continue
            
            pad_lost_count = 0  # Reset counter when pad is found
            error_x, error_y = padx, pady
            
            # Debug output every 10 iterations
            if iteration % 10 == 0:
                print(f"[DEBUG] Layer {i+1}, Iter {iteration}: padx={padx:.1f}, pady={pady:.1f}, error_x={error_x:.1f}, error_y={error_y:.1f}")
            
            if is_aligned(error_x, error_y):
                stable_count += 1
                if stable_count > STABLE_COUNT_REQUIRED:
                    current_alt = get_current_altitude()
                    print(f"[INFO] Aligned at layer {i+1} (altitude: {current_alt}cm) after {iteration} iterations")
                    break
            else:
                stable_count = 0
                
            send_alignment_command(error_x, error_y)
            time.sleep(LAND_ALIGNMENT_DELAY)
        else:
            print(f"[WARNING] Failed to align at layer {i+1} within {LAND_ALIGNMENT_ITERATIONS} iterations")
            return False

    print("[INFO] Landing...")
    send("rc 0 0 0 0")
    send("land")
    return True

