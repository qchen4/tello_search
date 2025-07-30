# config.py - concise parameters and constants

# Modes
TEST_MODE = True  # bypass pad detection for testing

# PID controller gains:
#   Kp (Proportional): response to current error magnitude
#   Ki (Integral): addresses accumulated past errors to eliminate steady-state offset
#   Kd (Derivative): predicts and dampens future error to reduce overshoot
Kp = 0.45     # proportional gain
Ki = 0.0005   # integral gain
Kd = 0.25     # derivative gain

# Orbit settings
RADIUS_TARGET     = 50   # cm: desired distance from pad center
ORBIT_DURATION    = 20   # s: duration to maintain orbit before landing
MAX_PAD_LOSS_TIME = 15   # s: max time to attempt pad detection before abort

# Landing control
# LAND_CONV_RADIUS: pixel radius within which descent begins
# STABLE_COUNT_REQUIRED: consecutive aligned frames needed per layer
# LAND_ALTITUDES: altitude layers (cm) for staged alignment
# LAND_ALIGNMENT_ITER: max alignment attempts per layer
# LAND_ALIGNMENT_DELAY: wait between alignment attempts (s)
# LAND_DESCENT_DIST: descent step size per layer (cm)
# LAND_DESCENT_DELAY: wait after descent command (s)
LAND_CONV_RADIUS      = 6
STABLE_COUNT_REQUIRED = 5
LAND_ALTITUDES        = [100, 70, 40, 10]
LAND_ALIGNMENT_ITER   = 200
LAND_ALIGNMENT_DELAY  = 0.1
LAND_DESCENT_DIST     = 15
LAND_DESCENT_DELAY    = 2

# Pad detection timeout
PAD_DETECTION_TIMEOUT = 30  # s to wait for initial pad detection

# Network & video
TELLO_IP         = '192.168.10.1'
TELLO_CMD_PORT   = 8889
TELLO_STATE_PORT = 8890
VIDEO_STREAM_URL = 'udp://@0.0.0.0:11111'

# Logging
LOG_FOLDER = 'log'

