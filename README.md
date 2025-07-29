
# Tello Precision Landing and Visual Navigation

This project implements a modular, real-time control system for the **DJI Tello EDU drone** to enable **autonomous takeoff, mission pad detection, PID-based orbiting, and precision landing**. The system includes visualization tools, telemetry logging, and offline analysis for tuning and debugging.

---

## ✈️ Features

- **Autonomous Takeoff & Landing** using mission pad detection
- **PID Velocity Control** for stable, smooth orbiting behavior
- **Visual Feedback Loop** using OpenCV overlays and ArUco marker detection
- **Failsafe Hover & Timeout Logic** when mission pad is lost
- **Bottom Camera Switching** for landing precision
- **Flight Logging** of telemetry and control commands
- **Plotting Utilities** to visualize trajectory, error, and control output post-flight

---

## 📁 Project Structure

```bash
.
├── main.py                  # Entry point: coordinates flight, logic, and camera
├── config.py                # Settings for mission pads, thresholds, drone IP, etc.
├── logger.py                # CSV logger for real-time telemetry
├── control/
│   ├── drone_interface.py   # Tello SDK command sender
│   ├── pid_controller.py    # Real PID control loop implementation
│   └── precision_landing.py # Logic for multistage descent and center alignment
├── vision/
│   ├── pad_tracker.py       # ArUco marker detection and center estimation
│   └── video_overlay.py     # Live OpenCV display with telemetry overlay
├── analysis/
│   └── analyze_flight.py    # Post-flight plotting of error/velocity vs. time
├── log/                     # Flight logs (telemetry)
├── plots/                   # Generated trajectory/error plots
├── requirements.txt         # Dependencies
└── Makefile                 # Easy setup and run commands
```

---

## 🔧 Techniques and Tools Used

### 🧠 Control

- **Real PID Controller** with tunable `Kp`, `Ki`, `Kd` parameters
- **Velocity RC Commands** (`rc x y z yaw`) based on error signal
- **Failsafe**: If pad lost, drone hovers for timeout then lands

### 📷 Vision & Overlay

- **OpenCV + PyAV** to decode and stream Tello’s video feed
- **ArUco marker detection** to locate mission pad center
- **Bottom Camera Mode**: Activated during descent for better visibility
- **Overlay Telemetry**: Shows error, velocity, and camera mode on video

### 📊 Logging & Analysis

- **CSV-based logging** (`logger.py`)
- **Post-flight plots** (`analyze_flight.py`) for error, velocity, and path
- **Saved to `./plots/`** with timestamps

---

## ▶️ Getting Started

1. **Install dependencies**
   ```bash
   make setup
   ```

2. **Activate virtual environment**
   ```bash
   source tello-venv/bin/activate
   ```

3. **Start the program**
   ```bash
   make run
   ```

---

## 🛠️ Requirements

- Linux system (Ubuntu 20.04+)
- Python 3.8+
- DJI Tello EDU drone
- Mission pad(s)
- Stable indoor test environment

---

## 📈 Example Output

- Real-time OpenCV window with overlays
- Autonomously circles and lands on mission pad
- `log/flight_log_*.csv` — telemetry with error & velocity
- `plots/flight_summary_*.png` — post-flight plots

---

## 📌 Future Improvements

- LQR control or adaptive PID tuning
- SLAM or vision-based obstacle avoidance
- ROS integration
- Precision landing using AprilTag + depth

---

## 👨‍💻 Author

Jeremy Chen – MSECE Student @ Georgia Tech  
Summer 2025 Embedded Vision Internship, CTI One

---

## 📄 License

MIT License
