# video_overlay.py - Show video stream and overlay PID status using PyAV

import av
import cv2
import threading
import numpy as np
from config import VIDEO_STREAM_URL
from control.drone_interface import send, state

latest_data = {
    'padx': 0,
    'pady': 0,
    'ex': 0,
    'ey': 0,
    'vx': 0,
    'vy': 0,
    'battery': 0,
    'state': '',
    'pad': False,
}

use_bottom_camera = True

def draw_overlay(padx, pady, error_x, error_y, vx, vy, battery, state, pad_found):
    latest_data.update({
        'padx': padx,
        'pady': pady,
        'ex': error_x,
        'ey': error_y,
        'vx': vx,
        'vy': vy,
        'battery': battery,
        'state': state,
        'pad': pad_found,
    })

def toggle_camera():
    global use_bottom_camera
    use_bottom_camera = not use_bottom_camera
    send(f"downvision {1 if use_bottom_camera else 0}")
    print(f"[INFO] Switched to {'bottom' if use_bottom_camera else 'front'} camera")

def get_battery_color(battery_level):
    """Get color based on battery level"""
    if battery_level >= 50:
        return (0, 255, 0)  # Green
    elif battery_level >= 20:
        return (0, 255, 255)  # Yellow
    else:
        return (0, 0, 255)  # Red

def get_telemetry_data():
    """Get current telemetry data from drone state"""
    try:
        battery = latest_data.get('battery') or int(state.get('bat', 0))
        height = int(state.get('h', 0))
        tof = int(state.get('tof', 0))
        temp = int(state.get('temph', 0))
        return battery, height, tof, temp
    except (ValueError, TypeError):
        return 0, 0, 0, 0

def _video_thread():
    container = None
    try:
        container = av.open(VIDEO_STREAM_URL)
        stream = container.streams.video[0]
        stream.thread_type = 'AUTO'
        
        for frame in container.decode(stream):
            try:
                img = frame.to_ndarray(format="bgr24")
                h, w, _ = img.shape
                cx, cy = w // 2 + latest_data['padx'], h // 2 + latest_data['pady']

                # Ensure coordinates are within image bounds
                cx = max(0, min(w-1, cx))
                cy = max(0, min(h-1, cy))

                # Draw mission pad indicator
                cv2.circle(img, (cx, cy), 10, (0, 255, 0), 2)
                
                # Get telemetry data
                battery, height, tof, temp = get_telemetry_data()
                
                # Draw PID information (top left)
                cv2.putText(img, f"ErrX: {latest_data['ex']:.1f}  ErrY: {latest_data['ey']:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                cv2.putText(img, f"VX: {latest_data['vx']}  VY: {latest_data['vy']}", (10, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                cv2.putText(img, f"Camera: {'Bottom' if use_bottom_camera else 'Front'}", (10, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 255), 2)
                cv2.putText(img, f"State: {latest_data['state']}", (10, 105),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                # Draw telemetry information (top right)
                battery_color = get_battery_color(battery)
                cv2.putText(img, f"Battery: {battery}%", (w - 200, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, battery_color, 2)
                cv2.putText(img, f"Height: {height}cm", (w - 200, 55),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(img, f"ToF: {tof}cm", (w - 200, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(img, f"Temp: {temp}°C", (w - 200, 105),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                pad_text = "YES" if latest_data['pad'] else "NO"
                cv2.putText(img, f"Pad: {pad_text}", (w - 200, 130),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Draw battery bar (bottom of screen)
                bar_width = 200
                bar_height = 20
                bar_x = 10
                bar_y = h - 40
                
                # Background bar
                cv2.rectangle(img, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (50, 50, 50), -1)
                
                # Battery level bar
                battery_width = int((battery / 100.0) * bar_width)
                cv2.rectangle(img, (bar_x, bar_y), (bar_x + battery_width, bar_y + bar_height), battery_color, -1)
                
                # Battery percentage text
                cv2.putText(img, f"{battery}%", (bar_x + bar_width + 10, bar_y + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, battery_color, 2)
                
                # Draw status indicators
                if battery < 20:
                    cv2.putText(img, "LOW BATTERY!", (w//2 - 100, h - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

                cv2.imshow("Tello Stream", img)
                key = cv2.waitKey(1)
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    toggle_camera()
                    
            except Exception as e:
                print(f"[ERROR] Video frame processing error: {e}")
                continue
                
    except Exception as e:
        print(f"[ERROR] Video stream error: {e}")
    finally:
        if container:
            try:
                container.close()
            except:
                pass
        cv2.destroyAllWindows()

def start_video_thread():
    thread = threading.Thread(target=_video_thread, daemon=True)
    thread.start()


