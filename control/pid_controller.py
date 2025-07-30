# pid_controller.py - PID logic module

from config import Kp, Ki, Kd, radius_target
import math
import time
from pad_tracker import origin_x, origin_y

class PIDController:
    def __init__(self):
        self.vx_integral = 0
        self.vy_integral = 0
        self.last_error_x = 0
        self.last_error_y = 0
        self.error_x = 0
        self.error_y = 0
        self.start_time = time.time()
        self.integral_reset_time = time.time()

    def update(self, padx, pady):
        t = time.time() - self.start_time
        desired_x = origin_x + radius_target * math.cos(t)
        desired_y = origin_y + radius_target * math.sin(t)

        self.error_x = desired_x - padx
        self.error_y = desired_y - pady
        dx = self.error_x - self.last_error_x
        dy = self.error_y - self.last_error_y

        # Reset integral every 10 seconds to prevent windup
        if time.time() - self.integral_reset_time > 10:
            self.vx_integral = 0
            self.vy_integral = 0
            self.integral_reset_time = time.time()

        self.vx_integral += self.error_x
        self.vy_integral += self.error_y

        # Limit integral windup
        self.vx_integral = max(-1000, min(1000, self.vx_integral))
        self.vy_integral = max(-1000, min(1000, self.vy_integral))

        vx = int(Kp * self.error_x + Ki * self.vx_integral + Kd * dx)
        vy = int(Kp * self.error_y + Ki * self.vy_integral + Kd * dy)

        vx = max(-100, min(100, vx))
        vy = max(-100, min(100, vy))

        self.last_error_x = self.error_x
        self.last_error_y = self.error_y
        return vx, vy

