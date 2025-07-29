#!/usr/bin/env python3
"""
Test script specifically for mission pad detection
"""

import time
import socket
from config import TELLO_IP, TELLO_CMD_PORT, TELLO_STATE_PORT

def test_pad_detection():
    print("=== Mission Pad Detection Test ===")
    print("Make sure you have a mission pad visible to the drone's bottom camera!")
    
    # Create command socket
    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_sock.bind(('', 9000))
    
    # Create state socket
    state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    state_sock.bind(('', TELLO_STATE_PORT))
    state_sock.settimeout(1)
    
    try:
        print("1. Initializing drone...")
        cmd_sock.sendto(b'command', (TELLO_IP, TELLO_CMD_PORT))
        time.sleep(1)
        
        print("2. Enabling mission pad detection...")
        cmd_sock.sendto(b'mon', (TELLO_IP, TELLO_CMD_PORT))
        time.sleep(1)
        
        print("3. Setting mission pad direction to downward...")
        cmd_sock.sendto(b'mdirection 2', (TELLO_IP, TELLO_CMD_PORT))
        time.sleep(1)
        
        print("4. Monitoring for mission pad data...")
        print("   (This will run for 30 seconds)")
        
        start_time = time.time()
        pad_detected = False
        
        while time.time() - start_time < 30:
            try:
                data, addr = state_sock.recvfrom(1024)
                decoded = data.decode().strip()
                
                # Parse state data
                state = {}
                parts = decoded.split(';')
                for item in parts:
                    if ':' in item:
                        k, v = item.split(':')
                        state[k] = v
                
                # Check for mission pad data
                if 'padx' in state and 'pady' in state:
                    padx = state['padx']
                    pady = state['pady']
                    if padx != '0' or pady != '0':  # Non-zero values indicate detection
                        print(f"   ✓ Mission pad detected! padx={padx}, pady={pady}")
                        pad_detected = True
                        break
                    else:
                        print(f"   - Mission pad in view but at center (padx={padx}, pady={pady})")
                else:
                    # Show other available data
                    if 'mid' in state:
                        print(f"   - Mission pad ID: {state['mid']}")
                    if 'x' in state and 'y' in state:
                        print(f"   - Drone position: x={state['x']}, y={state['y']}")
                    if 'h' in state:
                        print(f"   - Height: {state['h']}cm")
                        
            except socket.timeout:
                elapsed = time.time() - start_time
                if elapsed % 5 < 1:  # Print every 5 seconds
                    print(f"   Waiting... ({elapsed:.1f}s elapsed)")
                continue
        
        if pad_detected:
            print("\n✓ SUCCESS: Mission pad detection is working!")
        else:
            print("\n✗ FAILED: No mission pad detected")
            print("\nTroubleshooting tips:")
            print("1. Make sure you have a physical mission pad")
            print("2. Ensure the pad is visible to the drone's bottom camera")
            print("3. Check that the drone is at appropriate height (30-100cm)")
            print("4. Verify good lighting conditions")
            print("5. Try moving the pad around slowly")
            print("6. Check if the mission pad is damaged or dirty")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        cmd_sock.close()
        state_sock.close()
        print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_pad_detection() 