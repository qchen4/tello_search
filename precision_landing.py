# precision_landing.py - Modular layered descent landing

from drone_interface import send, state
from pad_tracker import get_pad_position
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

def is_aligned(error_x, error_y, threshold=LAND_CONV_RADIUS):
    """
    Return True if the 2‑D centering error is within the given threshold.
    Uses Euclidean distance for a single combined check.
    """
    return math.hypot(error_x, error_y) < threshold

def send_alignment_command(error_x, error_y):
    """
    Send an RC velocity command to reduce the pad‑centering error.
    Scales the correction by 0.8× and clamps to ±20cm/s.
    """
    vx = max(-20, min(20, int(error_x * 0.8)))
    vy = max(-20, min(20, int(error_y * 0.8)))
    send(f"rc {vx} {vy} 0 0")

def get_current_altitude():
    """Get current altitude (cm) from drone state, defaulting to 0 on error."""
    try:
        return int(state.get('h', 0))
    except (ValueError, TypeError):
        return 0

def descend_to_altitude(target_altitude, logger):
    """
    Descend to a specific altitude using a relative 'go' command.
    Falls back to a fixed-distance descent if altitude reading fails.
    """
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
    send(f"go 0 0 -{descent_needed} 20")
    # log the descent command as well
    cam = state.get('cam', 'NA')
    logger.log(
        0,   # padx
        0,   # pady
        0,   # error_x
        0,   # error_y
        0,   # vx
        0,   # vy
        -descent_needed,  # vz
        cam
    )



    time.sleep(LAND_DESCENT_DELAY)

    new_alt = get_current_altitude()
    print(f"[INFO] New altitude: {new_alt}cm")

def precision_land(logger):
    """
    Perform a multi‐layer precision landing:
      1. At each height in LAND_ALTITUDES, align to the pad center with a
         dynamically shrinking threshold.
      2. Descend to the next layer.
      3. After all layers, cut throttle and land.
    """
    print("[INFO] Starting precision landing")
    start_altitude = get_current_altitude()
    print(f"[INFO] Starting altitude: {start_altitude}cm")

    for i, target_alt in enumerate(LAND_ALTITUDES):
        print(f"[INFO] Aligning at layer {i+1} (target: {target_alt}cm)")
        stable_count = 0
        pad_lost_count = 0

        for iteration in range(LAND_ALIGNMENT_ITERATIONS):
            found, padx, pady = get_pad_position()
            if not found:
                pad_lost_count += 1
                if pad_lost_count > 10:  # abort if pad is lost too long
                    print(f"[WARNING] Pad lost for too long at layer {i+1}, aborting landing")
                    send("rc 0 0 0 0")
                    return False
                send("rc 0 0 0 0")
                time.sleep(LAND_ALIGNMENT_DELAY)
                continue

            pad_lost_count = 0
            err_x, err_y = padx, pady

            # Compute a shrinking threshold: from LAND_CONV_RADIUS → 2px as we descend
            dyn_thresh = max(
                2,
                int(LAND_CONV_RADIUS * (target_alt / start_altitude))
            )

            # Fixed debug print every 10 iters
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

        # Descend down to this layer’s altitude before the next alignment
        descend_to_altitude(target_alt, logger)

    # All layers done, now finalize the landing
    print("[INFO] Finalizing landing...")
    send("rc 0 0 0 0")
    logger.log(0, 0, 0, 0, 0, 0, 0, state.get('cam', 'NA'))
    send("land")
    return True

