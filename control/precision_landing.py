# precision_landing.py - Modular layered descent landing

from control.drone_interface import send, state
from vision.pad_tracker import get_pad_position
from config import (
    LAND_ALTITUDES,
    LAND_CONV_RADIUS,
    STABLE_COUNT_REQUIRED,
    LAND_ALIGNMENT_ITERATIONS,
    LAND_ALIGNMENT_DELAY,
    LAND_DESCENT_DISTANCE,
    LAND_DESCENT_DELAY
)
import time
import math
import threading
import sys
import termios
import tty

def is_aligned(error_x, error_y, threshold=LAND_CONV_RADIUS):
    return math.hypot(error_x, error_y) < threshold

def send_alignment_command(error_x, error_y):
    vx = max(-20, min(20, int(error_x * 0.8)))
    vy = max(-20, min(20, int(error_y * 0.8)))
    send(f"rc {vx} {vy} 0 0")

def get_current_altitude():
    try:
        return int(state.get('h', 0))
    except (ValueError, TypeError):
        return 0

def descend_to_altitude(target_altitude, logger):
    current_alt = get_current_altitude()
    if current_alt <= 0:
        print(f"[WARNING] Invalid altitude reading (h={current_alt}cm), using fallback descent + re‑alignment")
        send(f"go 0 0 -{LAND_DESCENT_DISTANCE} 20")
        time.sleep(LAND_DESCENT_DELAY)
        found, padx, pady = get_pad_position()
        if found:
            send_alignment_command(padx, pady)
            time.sleep(LAND_ALIGNMENT_DELAY)
        return
    descent_needed = current_alt - target_altitude
    if descent_needed <= 0:
        print(f"[INFO] Already at or below target altitude {target_altitude}cm")
        return
    print(f"[INFO] Descending from {current_alt}cm to {target_altitude}cm ({descent_needed}cm)")
    send(f"go 0 0 -{descent_needed} 20")
    cam = state.get('cam', 'NA')
    logger.log(
        0, 0, 0, 0, 0, 0, -descent_needed, cam
    )
    time.sleep(LAND_DESCENT_DELAY)
    new_alt = get_current_altitude()
    print(f"[INFO] New altitude: {new_alt}cm")

def search_pad(timeout=8, search_radius=15, steps=8):
    import math
    start = time.time()
    print("[INFO] Starting active pad search...")
    points = [
        (int(search_radius * math.cos(2*math.pi*i/steps)),
         int(search_radius * math.sin(2*math.pi*i/steps)))
        for i in range(steps)
    ]
    for idx, (dx, dy) in enumerate(points):
        if time.time() - start > timeout:
            break
        print(f"[DEBUG] Searching pad at offset (x={dx}, y={dy}) [step {idx+1}/{steps}]")
        try:
            send(f"go {dx} {dy} 0 10")
        except Exception as e:
            print(f"[WARNING] Move failed: {e}")
        time.sleep(1.0)
        found, padx, pady = get_pad_position()
        if found:
            print(f"[INFO] Pad detected at ({padx}, {pady}) during search!")
            send("rc 0 0 0 0")
            return True, padx, pady
    print(f"[ERROR] Pad not detected after active search ({timeout}s)")
    send("rc 0 0 0 0")
    return False, 0, 0

def getch():
    """Get a single character from standard input (blocking, no echo)."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def manual_control_mode():
    print("[INFO] Manual keyboard control mode activated.")
    print("Use WASD/arrow keys to move, Q/E for yaw, Z/X for up/down. 'L' to exit and try auto-landing, Ctrl+C to emergency stop.")
    while True:
        key = getch()
        if key in ['w', 'W', '\x1b[A']:
            send("rc 0 20 0 0")
        elif key in ['s', 'S', '\x1b[B']:
            send("rc 0 -20 0 0")
        elif key in ['a', 'A', '\x1b[D']:
            send("rc -20 0 0 0")
        elif key in ['d', 'D', '\x1b[C']:
            send("rc 20 0 0 0")
        elif key in ['q', 'Q']:
            send("rc 0 0 0 -20")
        elif key in ['e', 'E']:
            send("rc 0 0 0 20")
        elif key in ['z', 'Z']:
            send("rc 0 0 20 0")
        elif key in ['x', 'X']:
            send("rc 0 0 -20 0")
        elif key in ['l', 'L']:
            send("rc 0 0 0 0")
            print("[INFO] Auto-landing requested by user.")
            return 'land'
        elif key in ['c', 'C']:
            send("rc 0 0 0 0")
            print("[INFO] Continue manual search.")
        elif key in ['\x03']: # Ctrl+C
            print("[EMERGENCY] Emergency stop requested.")
            send("rc 0 0 0 0")
            send("land")
            sys.exit(0)
        else:
            send("rc 0 0 0 0")

def wait_for_pad_or_manual():
    """
    Multi-stage pad search: hover, auto-search, then manual override.
    Returns True when pad is found and user requests landing.
    """
    # Hover search (brief)
    for _ in range(20):  # 2 seconds at 0.1s intervals
        found, padx, pady = get_pad_position()
        if found:
            print("[INFO] Pad found during initial hover.")
            return True, padx, pady
        send("rc 0 0 0 0")
        time.sleep(0.1)
    # Auto-search
    found, padx, pady = search_pad(timeout=8)
    if found:
        print("[INFO] Pad found during auto-search.")
        return True, padx, pady
    # Manual mode
    print("[WARNING] Pad not found. Switching to manual search mode.")
    print("[INSTRUCTION] Use WASD/arrow keys to move the drone. Press 'L' when pad is detected to resume landing.")
    pad_found = [False, 0, 0]
    found_event = threading.Event()
    def monitor_pad():
        while not found_event.is_set():
            found, padx, pady = get_pad_position()
            if found:
                print("[INFO] Pad detected! Press 'L' to resume auto landing.")
                pad_found[0] = True
                pad_found[1] = padx
                pad_found[2] = pady
                found_event.set()
            time.sleep(0.2)
    t = threading.Thread(target=monitor_pad, daemon=True)
    t.start()
    while True:
        key = getch()
        if key in ['w', 'W', '\x1b[A']:
            send("rc 0 20 0 0")
        elif key in ['s', 'S', '\x1b[B']:
            send("rc 0 -20 0 0")
        elif key in ['a', 'A', '\x1b[D']:
            send("rc -20 0 0 0")
        elif key in ['d', 'D', '\x1b[C']:
            send("rc 20 0 0 0")
        elif key in ['q', 'Q']:
            send("rc 0 0 0 -20")
        elif key in ['e', 'E']:
            send("rc 0 0 0 20")
        elif key in ['z', 'Z']:
            send("rc 0 0 20 0")
        elif key in ['x', 'X']:
            send("rc 0 0 -20 0")
        elif key in ['l', 'L']:
            if pad_found[0]:
                print("[INFO] Pad found and 'L' pressed. Resuming auto landing.")
                send("rc 0 0 0 0")
                return True, pad_found[1], pad_found[2]
            else:
                print("[INFO] Pad not detected yet, keep searching.")
        elif key in ['\x03']:
            print("[EMERGENCY] Emergency stop requested.")
            send("rc 0 0 0 0")
            send("land")
            sys.exit(0)
        else:
            send("rc 0 0 0 0")

def precision_land(logger):
    print("[INFO] Starting precision landing")
    start_altitude = get_current_altitude()
    print(f"[INFO] Starting altitude: {start_altitude}cm")
    for i, target_alt in enumerate(LAND_ALTITUDES):
        print(f"[INFO] Aligning at layer {i+1} (target: {target_alt}cm)")
        stable_count = 0
        pad_lost_count = 0
        descend_to_altitude(target_alt, logger)
        # Multi-stage pad reacquisition (hover, auto, manual)
        found, padx, pady = wait_for_pad_or_manual()
        if not found:
            print(f"[ERROR] Aborting landing: pad not detected at layer {i+1} (altitude {target_alt}cm)")
            send("rc 0 0 0 0")
            return False
        print(f"[INFO] Pad acquired at {target_alt}cm, starting alignment...")
        for iteration in range(LAND_ALIGNMENT_ITERATIONS):
            found, padx, pady = get_pad_position()
            if not found:
                pad_lost_count += 1
                if pad_lost_count > 10:
                    print(f"[WARNING] Pad lost for too long at layer {i+1}, aborting landing")
                    send("rc 0 0 0 0")
                    return False
                send("rc 0 0 0 0")
                time.sleep(LAND_ALIGNMENT_DELAY)
                continue
            pad_lost_count = 0
            err_x, err_y = padx, pady
            dyn_thresh = max(
                2,
                int(LAND_CONV_RADIUS * (target_alt / start_altitude))
            )
            if iteration % 10 == 0:
                print(
                    f"[DEBUG] Layer {i+1}, Iter {iteration}: "
                    f"error_x={err_x:.1f}, error_y={err_y:.1f}, dyn_thresh={dyn_thresh}px"
                )
            if is_aligned(err_x, err_y, threshold=dyn_thresh):
                stable_count += 1
                if stable_count > STABLE_COUNT_REQUIRED:
                    current_alt = get_current_altitude()
                    print(
                        f"[INFO] Aligned at layer {i+1} "
                        f"(altitude: {current_alt}cm) after {iteration} iterations"
                    )
                    break
            else:
                stable_count = 0
            send_alignment_command(err_x, err_y)
            vx = int(err_x * 0.8)
            vy = int(err_y * 0.8)
            cam = state.get('cam', 'NA')
            logger.log(padx, pady, err_x, err_y, vx, vy, 0, cam)
            time.sleep(LAND_ALIGNMENT_DELAY)
        else:
            print(
                f"[WARNING] Failed to align at layer {i+1} "
                f"within {LAND_ALIGNMENT_ITERATIONS} iterations"
            )
            return False
        descend_to_altitude(target_alt, logger)
    print("[INFO] Finalizing landing...")
    send("rc 0 0 0 0")
    logger.log(0, 0, 0, 0, 0, 0, 0, state.get('cam', 'NA'))
    send("land")
    return True

