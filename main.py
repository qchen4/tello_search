# main.py - Entry point for the Tello orbit + precision landing mission

from config import ORBIT_DURATION, MAX_PAD_LOSS_TIME, PAD_DETECTION_TIMEOUT
from control.drone_interface import initialize_drone, send, start_state_reader, stop_state_reader, cleanup_sockets
from vision.pad_tracker import wait_for_pad_origin, get_pad_position
from control.pid_controller import PIDController
from control.precision_landing import precision_land
from logger import FlightLogger
from vision.video_overlay import start_video_thread, draw_overlay
import time
import signal
import threading
import sys

# Global
pid = PIDController()
logger = None


def emergency_land(sig, frame):
    print("\n[EMERGENCY] Emergency landing initiated!")
    try:
        send("rc 0 0 0 0")
        send("land")
    except:
        pass
    
    if logger:
        logger.close()
    
    stop_state_reader()
    cleanup_sockets()
    print("[EMERGENCY] Emergency landing complete")
    sys.exit(0)


def orbit_phase():
    global pid
    pad_loss_start = None
    start_time = time.time()
    
    while time.time() - start_time < ORBIT_DURATION:
        try:
            pad_detected, padx, pady = get_pad_position()
            now = time.time()

            if not pad_detected:
                if pad_loss_start is None:
                    pad_loss_start = now
                elif now - pad_loss_start > MAX_PAD_LOSS_TIME:
                    print(f"[WARNING] Pad lost for {MAX_PAD_LOSS_TIME} seconds, emergency landing")
                    send("rc 0 0 0 0")
                    send("land")
                    return False
                else:
                    send("rc 0 0 0 0")
                    continue
            else:
                pad_loss_start = None

            vx, vy = pid.update(padx, pady)
            draw_overlay(padx, pady, pid.error_x, pid.error_y, vx, vy)
            logger.log_step(padx, pady, pid.error_x, pid.error_y, vx, vy)
            send(f"rc {vx} {vy} 0 0")
            time.sleep(0.05)
            
        except Exception as e:
            print(f"[ERROR] Error in orbit phase: {e}")
            send("rc 0 0 0 0")
            time.sleep(0.1)

    return True


def main():
    global logger
    try:
        signal.signal(signal.SIGINT, emergency_land)
        signal.signal(signal.SIGTERM, emergency_land)

        print("[INFO] Starting Tello autonomous mission...")
        
        start_state_reader()
        start_video_thread()
        
        print("[INFO] Initializing drone...")
        initialize_drone()
        
        print("[INFO] Waiting for mission pad...")
        try:
            wait_for_pad_origin()
        except TimeoutError as e:
            print(f"[ERROR] {e}")
            emergency_land(None, None)

        logger = FlightLogger()
        logger.start()

        print("[INFO] Moving to orbit position...")
        send("go 0 50 70 20")
        time.sleep(2)

        print("[INFO] Starting orbital phase...")
        if orbit_phase():
            print("[INFO] Orbital phase complete, starting precision landing...")
            if precision_land(logger):
                print("[SUCCESS] Mission completed successfully!")
            else:
                print("[WARNING] Precision landing failed")
        else:
            print("[WARNING] Orbital phase failed")
            
    except Exception as e:
        print(f"[ERROR] Unexpected error in main: {e}")
        logger.error(f"Unexpected error in main: {e}")
        emergency_land(None, None)
    finally:
        if logger:
            logger.close()
        stop_state_reader()
        cleanup_sockets()
        print("[INFO] Mission cleanup complete")


if __name__ == "__main__":
    main()

