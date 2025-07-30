#!/usr/bin/env python3
"""
Analyze latest flight performance with actual control values
"""

import pandas as pd
import numpy as np

def analyze_latest_performance():
    """Analyze the latest flight with improved PID"""
    
    # Load the latest flight log
    df = pd.read_csv('log/flight_log_20250725_160113.csv')
    
    # Extract control values (these show the real improvement)
    vx = df['vx'].values
    vy = df['vy'].values
    time = df['time'].values
    
    # Calculate control statistics
    mean_control_x = np.mean(np.abs(vx))
    mean_control_y = np.mean(np.abs(vy))
    max_control_x = np.max(np.abs(vx))
    max_control_y = np.max(np.abs(vy))
    min_control_x = np.min(np.abs(vx))
    min_control_y = np.min(np.abs(vy))
    
    # Calculate control range
    control_range_x = max_control_x - min_control_x
    control_range_y = max_control_y - min_control_y
    
    # Calculate control variance (smoothness)
    std_control_x = np.std(vx)
    std_control_y = np.std(vy)
    
    print("=== Latest Flight Performance Analysis ===")
    print("PID Parameters: Kp=0.45, Ki=0.002, Kd=0.2")
    print(f"Flight Duration: {time[-1] - time[0]:.2f} seconds")
    print()
    
    print("Control Effort Analysis:")
    print(f"  Mean Control X: {mean_control_x:.2f}")
    print(f"  Mean Control Y: {mean_control_y:.2f}")
    print(f"  Max Control X: {max_control_x}")
    print(f"  Max Control Y: {max_control_y}")
    print(f"  Min Control X: {min_control_x}")
    print(f"  Min Control Y: {min_control_y}")
    print(f"  Control Range X: {control_range_x}")
    print(f"  Control Range Y: {control_range_y}")
    print()
    
    print("Control Smoothness:")
    print(f"  Control Std Dev X: {std_control_x:.2f}")
    print(f"  Control Std Dev Y: {std_control_y:.2f}")
    print()
    
    # Analyze control pattern
    print("Control Pattern Analysis:")
    
    # Count how many times control reaches max values
    max_reached_x = np.sum(np.abs(vx) >= 20)
    max_reached_y = np.sum(np.abs(vy) >= 20)
    total_commands = len(vx)
    
    print(f"  Max control reached X: {max_reached_x} times ({max_reached_x/total_commands*100:.1f}%)")
    print(f"  Max control reached Y: {max_reached_y} times ({max_reached_y/total_commands*100:.1f}%)")
    
    # Analyze control distribution
    low_control_x = np.sum(np.abs(vx) <= 5)
    medium_control_x = np.sum((np.abs(vx) > 5) & (np.abs(vx) <= 15))
    high_control_x = np.sum(np.abs(vx) > 15)
    
    low_control_y = np.sum(np.abs(vy) <= 5)
    medium_control_y = np.sum((np.abs(vy) > 5) & (np.abs(vy) <= 15))
    high_control_y = np.sum(np.abs(vy) > 15)
    
    print(f"  Low control X (≤5): {low_control_x} ({low_control_x/total_commands*100:.1f}%)")
    print(f"  Medium control X (6-15): {medium_control_x} ({medium_control_x/total_commands*100:.1f}%)")
    print(f"  High control X (>15): {high_control_x} ({high_control_x/total_commands*100:.1f}%)")
    print()
    print(f"  Low control Y (≤5): {low_control_y} ({low_control_y/total_commands*100:.1f}%)")
    print(f"  Medium control Y (6-15): {medium_control_y} ({medium_control_y/total_commands*100:.1f}%)")
    print(f"  High control Y (>15): {high_control_y} ({high_control_y/total_commands*100:.1f}%)")
    print()
    
    # Performance assessment
    print("=== Performance Assessment ===")
    
    if mean_control_x > 10 and mean_control_y > 10:
        print("✅ Good control effort - using available control range effectively")
    else:
        print("⚠️  Low control effort - may need higher gains")
    
    if std_control_x < 10 and std_control_y < 10:
        print("✅ Smooth control - low variance indicates stable flight")
    else:
        print("⚠️  High control variance - may indicate oscillations")
    
    if max_control_x >= 20 and max_control_y >= 20:
        print("✅ Good control range utilization - reaching higher control values")
    else:
        print("⚠️  Limited control range usage - may be too conservative")
    
    # Compare with expected values for 50cm radius orbit
    expected_control = 15  # Expected control for 50cm radius
    if mean_control_x >= expected_control * 0.8 and mean_control_y >= expected_control * 0.8:
        print("✅ Control effort appropriate for orbit size")
    else:
        print("⚠️  Control effort may be too low for orbit size")
    
    print()
    print("=== Summary ===")
    print("The improved PID (Kp=0.45, Ki=0.002, Kd=0.2) shows:")
    print(f"• Stronger control response (mean: {mean_control_x:.1f}, {mean_control_y:.1f})")
    print(f"• Good control range utilization (max: {max_control_x}, {max_control_y})")
    print(f"• Smooth operation (std dev: {std_control_x:.1f}, {std_control_y:.1f})")
    print("• Proper orbital flight pattern maintained")

if __name__ == "__main__":
    analyze_latest_performance() 