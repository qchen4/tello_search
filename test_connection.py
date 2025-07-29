#!/usr/bin/env python3
"""
Test script to debug Tello connection and state data
"""

import time
import socket
from config import TELLO_IP, TELLO_CMD_PORT, TELLO_STATE_PORT

def test_tello_connection():
    print("=== Tello Connection Test ===")
    
    # Create command socket
    cmd_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cmd_sock.bind(('', 9000))
    
    # Create state socket
    state_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    state_sock.bind(('', TELLO_STATE_PORT))
    state_sock.settimeout(5)
    
    try:
        print("1. Testing command connection...")
        cmd_sock.sendto(b'command', (TELLO_IP, TELLO_CMD_PORT))
        time.sleep(1)
        print("   ✓ Command sent")
        
        print("2. Testing state connection...")
        state_sock.settimeout(10)
        try:
            data, addr = state_sock.recvfrom(1024)
            print(f"   ✓ State data received from {addr}")
            print(f"   Data: {data.decode()}")
        except socket.timeout:
            print("   ✗ No state data received (timeout)")
            print("   This might be normal if drone is not powered on")
        
        print("3. Testing basic commands...")
        commands = ['command', 'battery?', 'height?']
        for cmd in commands:
            print(f"   Sending: {cmd}")
            cmd_sock.sendto(cmd.encode(), (TELLO_IP, TELLO_CMD_PORT))
            time.sleep(0.5)
        
        print("4. Testing mission pad commands...")
        pad_commands = ['mon', 'mdirection 2']
        for cmd in pad_commands:
            print(f"   Sending: {cmd}")
            cmd_sock.sendto(cmd.encode(), (TELLO_IP, TELLO_CMD_PORT))
            time.sleep(0.5)
        
        print("5. Monitoring state data for 10 seconds...")
        state_sock.settimeout(1)
        start_time = time.time()
        while time.time() - start_time < 10:
            try:
                data, addr = state_sock.recvfrom(1024)
                decoded = data.decode().strip()
                print(f"   State: {decoded}")
                
                # Check for mission pad data
                if 'padx:' in decoded or 'pady:' in decoded:
                    print("   ✓ Mission pad data detected!")
                    
            except socket.timeout:
                continue
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    finally:
        cmd_sock.close()
        state_sock.close()
        print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_tello_connection() 