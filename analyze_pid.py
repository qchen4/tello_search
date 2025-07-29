#!/usr/bin/env python3
"""
PID Analysis and Tuning Tool
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def analyze_pid_performance(log_path):
    """Analyze PID performance from flight log"""
    
    # Load data
    df = pd.read_csv(log_path)
    
    # Calculate performance metrics
    error_x = df['error_x'].values
    error_y = df['error_y'].values
    vx = df['vx'].values
    vy = df['vy'].values
    time = df['time'].values
    
    # Calculate error statistics
    mean_error_x = np.mean(np.abs(error_x))
    mean_error_y = np.mean(np.abs(error_y))
    max_error_x = np.max(np.abs(error_x))
    max_error_y = np.max(np.abs(error_y))
    std_error_x = np.std(error_x)
    std_error_y = np.std(error_y)
    
    # Calculate control effort
    mean_control_x = np.mean(np.abs(vx))
    mean_control_y = np.mean(np.abs(vy))
    max_control_x = np.max(np.abs(vx))
    max_control_y = np.max(np.abs(vy))
    
    # Calculate settling time (time to reach within 5% of target)
    target_radius = 50  # cm
    settling_threshold = target_radius * 0.05  # 5% of target radius
    
    # Find when error magnitude drops below threshold
    error_magnitude = np.sqrt(error_x**2 + error_y**2)
    settled_indices = np.where(error_magnitude < settling_threshold)[0]
    
    if len(settled_indices) > 0:
        settling_time = time[settled_indices[0]] - time[0]
    else:
        settling_time = float('inf')
    
    # Calculate overshoot
    max_error_magnitude = np.max(error_magnitude)
    overshoot_percent = ((max_error_magnitude - target_radius) / target_radius) * 100
    
    # Print analysis results
    print("=== PID Performance Analysis ===")
    print(f"Flight Duration: {time[-1] - time[0]:.2f} seconds")
    print(f"Target Radius: {target_radius} cm")
    print()
    
    print("Error Analysis:")
    print(f"  Mean Error X: {mean_error_x:.2f} cm")
    print(f"  Mean Error Y: {mean_error_y:.2f} cm")
    print(f"  Max Error X: {max_error_x:.2f} cm")
    print(f"  Max Error Y: {max_error_y:.2f} cm")
    print(f"  Error Std Dev X: {std_error_x:.2f} cm")
    print(f"  Error Std Dev Y: {std_error_y:.2f} cm")
    print()
    
    print("Control Effort:")
    print(f"  Mean Control X: {mean_control_x:.2f}")
    print(f"  Mean Control Y: {mean_control_y:.2f}")
    print(f"  Max Control X: {max_control_x}")
    print(f"  Max Control Y: {max_control_y}")
    print()
    
    print("Performance Metrics:")
    print(f"  Settling Time: {settling_time:.2f} seconds")
    print(f"  Overshoot: {overshoot_percent:.1f}%")
    print()
    
    # PID Tuning Recommendations
    print("=== PID Tuning Recommendations ===")
    
    if settling_time > 5.0:
        print("⚠️  Slow settling time detected")
        print("   → Increase Kp to improve response speed")
        print("   → Current Kp might be too conservative")
    
    if overshoot_percent > 20:
        print("⚠️  High overshoot detected")
        print("   → Increase Kd to reduce overshoot")
        print("   → Consider reducing Kp slightly")
    
    if mean_error_x > 10 or mean_error_y > 10:
        print("⚠️  High steady-state error detected")
        print("   → Increase Ki to reduce steady-state error")
        print("   → Current Ki might be too low")
    
    if max_control_x > 80 or max_control_y > 80:
        print("⚠️  High control effort detected")
        print("   → Consider reducing Kp to avoid saturation")
        print("   → Current gains might be too aggressive")
    
    if std_error_x < 5 and std_error_y < 5:
        print("✅ Good stability - low error variance")
    
    # Suggested PID values
    print("\n=== Suggested PID Values ===")
    current_kp = 0.3
    current_ki = 0.001
    current_kd = 0.2
    
    # Calculate suggested values based on performance
    suggested_kp = current_kp
    suggested_ki = current_ki
    suggested_kd = current_kd
    
    if settling_time > 5.0:
        suggested_kp = min(current_kp * 1.5, 0.8)
    
    if overshoot_percent > 20:
        suggested_kd = min(current_kd * 1.3, 0.4)
    
    if mean_error_x > 10 or mean_error_y > 10:
        suggested_ki = min(current_ki * 2.0, 0.005)
    
    print(f"Current:  Kp={current_kp}, Ki={current_ki}, Kd={current_kd}")
    print(f"Suggested: Kp={suggested_kp:.3f}, Ki={suggested_ki:.3f}, Kd={suggested_kd:.3f}")
    
    # Create detailed plots
    create_pid_plots(df, log_path)
    
    return {
        'settling_time': settling_time,
        'overshoot': overshoot_percent,
        'mean_error': (mean_error_x + mean_error_y) / 2,
        'suggested_kp': suggested_kp,
        'suggested_ki': suggested_ki,
        'suggested_kd': suggested_kd
    }

def create_pid_plots(df, log_path):
    """Create detailed PID analysis plots"""
    
    # Create plots directory
    plot_dir = os.path.join(os.path.dirname(log_path), "plots")
    os.makedirs(plot_dir, exist_ok=True)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    time = df['time'].values
    error_x = df['error_x'].values
    error_y = df['error_y'].values
    vx = df['vx'].values
    vy = df['vy'].values
    
    # Plot 1: Error over time
    axes[0, 0].plot(time, error_x, label='Error X', color='red')
    axes[0, 0].plot(time, error_y, label='Error Y', color='blue')
    axes[0, 0].set_xlabel('Time (s)')
    axes[0, 0].set_ylabel('Error (cm)')
    axes[0, 0].set_title('PID Error Over Time')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Plot 2: Control effort over time
    axes[0, 1].plot(time, vx, label='Control X', color='red')
    axes[0, 1].plot(time, vy, label='Control Y', color='blue')
    axes[0, 1].set_xlabel('Time (s)')
    axes[0, 1].set_ylabel('Control Output')
    axes[0, 1].set_title('Control Effort Over Time')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # Plot 3: Error magnitude
    error_magnitude = np.sqrt(error_x**2 + error_y**2)
    axes[1, 0].plot(time, error_magnitude, color='green')
    axes[1, 0].axhline(y=50, color='red', linestyle='--', label='Target Radius')
    axes[1, 0].set_xlabel('Time (s)')
    axes[1, 0].set_ylabel('Error Magnitude (cm)')
    axes[1, 0].set_title('Error Magnitude Over Time')
    axes[1, 0].legend()
    axes[1, 0].grid(True)
    
    # Plot 4: Phase plot (error vs control)
    axes[1, 1].scatter(error_x, vx, alpha=0.6, label='X-axis', color='red')
    axes[1, 1].scatter(error_y, vy, alpha=0.6, label='Y-axis', color='blue')
    axes[1, 1].set_xlabel('Error (cm)')
    axes[1, 1].set_ylabel('Control Output')
    axes[1, 1].set_title('Error vs Control (Phase Plot)')
    axes[1, 1].legend()
    axes[1, 1].grid(True)
    
    plt.tight_layout()
    
    # Save plot
    base_name = os.path.splitext(os.path.basename(log_path))[0]
    output_path = os.path.join(plot_dir, f"{base_name}_pid_analysis.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"[INFO] PID analysis plot saved to {output_path}")
    plt.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_pid.py path/to/flight_log.csv")
        sys.exit(1)
    
    log_path = sys.argv[1]
    if not os.path.exists(log_path):
        print(f"Log file not found: {log_path}")
        sys.exit(1)
    
    analyze_pid_performance(log_path) 