#!/usr/bin/env python3
"""
Compare PID performance between old and new parameters
"""

import pandas as pd
import numpy as np

def compare_pid_performance():
    """Compare old vs new PID performance"""
    
    # Load both flight logs
    old_log = pd.read_csv('log/flight_log_20250725_155252.csv')  # Old PID
    new_log = pd.read_csv('log/flight_log_20250725_155537.csv')  # New PID
    
    print("=== PID Performance Comparison ===")
    print("Old PID: Kp=0.3, Ki=0.001, Kd=0.2")
    print("New PID: Kp=0.45, Ki=0.002, Kd=0.2")
    print()
    
    # Calculate metrics for old PID
    old_error_x = old_log['error_x'].values
    old_error_y = old_log['error_y'].values
    old_vx = old_log['vx'].values
    old_vy = old_log['vy'].values
    
    old_mean_error_x = np.mean(np.abs(old_error_x))
    old_mean_error_y = np.mean(np.abs(old_error_y))
    old_max_error_x = np.max(np.abs(old_error_x))
    old_max_error_y = np.max(np.abs(old_error_y))
    old_mean_control_x = np.mean(np.abs(old_vx))
    old_mean_control_y = np.mean(np.abs(old_vy))
    old_max_control_x = np.max(np.abs(old_vx))
    old_max_control_y = np.max(np.abs(old_vy))
    
    # Calculate metrics for new PID
    new_error_x = new_log['error_x'].values
    new_error_y = new_log['error_y'].values
    new_vx = new_log['vx'].values
    new_vy = new_log['vy'].values
    
    new_mean_error_x = np.mean(np.abs(new_error_x))
    new_mean_error_y = np.mean(np.abs(new_error_y))
    new_max_error_x = np.max(np.abs(new_error_x))
    new_max_error_y = np.max(np.abs(new_error_y))
    new_mean_control_x = np.mean(np.abs(new_vx))
    new_mean_control_y = np.mean(np.abs(new_vy))
    new_max_control_x = np.max(np.abs(new_vx))
    new_max_control_y = np.max(np.abs(new_vy))
    
    # Print comparison table
    print("Metric                    | Old PID | New PID | Improvement")
    print("-" * 60)
    print(f"Mean Error X (cm)        | {old_mean_error_x:7.2f} | {new_mean_error_x:7.2f} | {((old_mean_error_x - new_mean_error_x) / old_mean_error_x * 100):+6.1f}%")
    print(f"Mean Error Y (cm)        | {old_mean_error_y:7.2f} | {new_mean_error_y:7.2f} | {((old_mean_error_y - new_mean_error_y) / old_mean_error_y * 100):+6.1f}%")
    print(f"Max Error X (cm)         | {old_max_error_x:7.2f} | {new_max_error_x:7.2f} | {((old_max_error_x - new_max_error_x) / old_max_error_x * 100):+6.1f}%")
    print(f"Max Error Y (cm)         | {old_max_error_y:7.2f} | {new_max_error_y:7.2f} | {((old_max_error_y - new_max_error_y) / old_max_error_y * 100):+6.1f}%")
    print(f"Mean Control X           | {old_mean_control_x:7.2f} | {new_mean_control_x:7.2f} | {((new_mean_control_x - old_mean_control_x) / old_mean_control_x * 100):+6.1f}%")
    print(f"Mean Control Y           | {old_mean_control_y:7.2f} | {new_mean_control_y:7.2f} | {((new_mean_control_y - old_mean_control_y) / old_mean_control_y * 100):+6.1f}%")
    print(f"Max Control X            | {old_max_control_x:7.0f} | {new_max_control_x:7.0f} | {((new_max_control_x - old_max_control_x) / old_max_control_x * 100):+6.1f}%")
    print(f"Max Control Y            | {old_max_control_y:7.0f} | {new_max_control_y:7.0f} | {((new_max_control_y - old_max_control_y) / old_max_control_y * 100):+6.1f}%")
    
    print()
    print("=== Analysis ===")
    
    # Error improvement
    error_improvement_x = (old_mean_error_x - new_mean_error_x) / old_mean_error_x * 100
    error_improvement_y = (old_mean_error_y - new_mean_error_y) / old_mean_error_y * 100
    
    if error_improvement_x > 0 and error_improvement_y > 0:
        print("✅ Error reduction achieved!")
        print(f"   X-axis error reduced by {error_improvement_x:.1f}%")
        print(f"   Y-axis error reduced by {error_improvement_y:.1f}%")
    else:
        print("⚠️  Error increased - may need further tuning")
    
    # Control effort analysis
    control_increase_x = (new_mean_control_x - old_mean_control_x) / old_mean_control_x * 100
    control_increase_y = (new_mean_control_y - old_mean_control_y) / old_mean_control_y * 100
    
    print(f"📊 Control effort increased:")
    print(f"   X-axis: +{control_increase_x:.1f}%")
    print(f"   Y-axis: +{control_increase_y:.1f}%")
    
    if control_increase_x < 100 and control_increase_y < 100:
        print("✅ Control effort increase is reasonable")
    else:
        print("⚠️  Control effort increased significantly")
    
    # Overall assessment
    print()
    print("=== Overall Assessment ===")
    
    if error_improvement_x > 5 and error_improvement_y > 5:
        print("🎉 Excellent improvement! The new PID parameters are working better.")
        print("   The increased control effort is justified by the error reduction.")
    elif error_improvement_x > 0 and error_improvement_y > 0:
        print("👍 Good improvement! The new parameters show better performance.")
        print("   Consider fine-tuning further for optimal results.")
    else:
        print("🤔 Mixed results. Consider different tuning approach:")
        print("   - Try different Kp values")
        print("   - Adjust Ki for steady-state error")
        print("   - Fine-tune Kd for damping")

if __name__ == "__main__":
    compare_pid_performance() 