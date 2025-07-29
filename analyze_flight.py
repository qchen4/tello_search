# analyze_flight.py - Plot PID error and flight trajectory

import pandas as pd
import matplotlib.pyplot as plt
import sys
import os

if len(sys.argv) != 2:
    print("Usage: python analyze_flight.py path/to/flight_log.csv")
    sys.exit(1)

log_path = sys.argv[1]
if not os.path.exists(log_path):
    print(f"Log file not found: {log_path}")
    sys.exit(1)

# Load CSV
log = pd.read_csv(log_path)

# Prepare output folder
plot_folder = os.path.join(os.path.dirname(log_path), "plots")
os.makedirs(plot_folder, exist_ok=True)

# Create side-by-side subplots
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot error over time
axes[0].plot(log['time'], log['error_x'], label='Error X')
axes[0].plot(log['time'], log['error_y'], label='Error Y')
axes[0].set_xlabel('Time (s)')
axes[0].set_ylabel('PID Error')
axes[0].set_title('PID Error Over Time')
axes[0].legend()
axes[0].grid(True)

# Plot trajectory
axes[1].plot(log['padx'], log['pady'], label='Trajectory')
axes[1].scatter([log['padx'][0]], [log['pady'][0]], c='green', label='Start')
axes[1].scatter([log['padx'].iloc[-1]], [log['pady'].iloc[-1]], c='red', label='End')
axes[1].set_xlabel('Pad X')
axes[1].set_ylabel('Pad Y')
axes[1].set_title('Flight Trajectory')
axes[1].axis('equal')
axes[1].grid(True)
axes[1].legend()

# Save combined plot
base_name = os.path.splitext(os.path.basename(log_path))[0]
output_path = os.path.join(plot_folder, f"{base_name}_analysis.png")
plt.tight_layout()
plt.savefig(output_path)
print(f"[INFO] Saved plot to {output_path}")
plt.close()
