# config.py - Centralized parameters and constants

# Test mode - set to True to bypass mission pad detection for testing
TEST_MODE = True

# PID Controller Parameters
Kp = 0.35  # Reduced from 0.45 for less aggressive control
Ki = 0.003  # Increased from 0.002 for better steady-state error reduction
Kd = 0.25  # Increased from 0.2 for better damping and oscillation reduction

# Target radius for orbit (in cm)
radius_target = 50

# Flight timing (in seconds)
ORBIT_DURATION = 20
MAX_PAD_LOSS_TIME = 15.0

# Landing control
LAND_THRESHOLD = 5
STABLE_COUNT_REQUIRED = 5
LAND_ALTITUDES = [50, 35, 20, 10]
LAND_CONV_RADIUS = 20

# Landing alignment parameters
LAND_ALIGNMENT_ITERATIONS = 100  # Max iterations per altitude layer
LAND_ALIGNMENT_DELAY = 0.1  # Seconds between alignment checks
LAND_DESCENT_DISTANCE = 15  # cm to descend per layer
LAND_DESCENT_DELAY = 2  # Seconds to wait after descent

# Pad detection timeout
PAD_DETECTION_TIMEOUT = 30  # Seconds to wait for initial pad detection

# Tello network
TELLO_IP = '192.168.10.1'
TELLO_CMD_PORT = 8889
TELLO_STATE_PORT = 8890

# Video stream URL
VIDEO_STREAM_URL = 'udp://@0.0.0.0:11111'

# Logging
LOG_FOLDER = 'log'

