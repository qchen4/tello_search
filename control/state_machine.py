from enum import Enum, auto

class DroneState(Enum):
    INIT = auto()
    HOVER = auto()
    PID_SEARCH = auto()
    AUTO_SEARCH = auto()
    MULTI_LAND = auto()
    PAD_FOLLOW = auto()
    MANUAL = auto()
    EMERGENCY = auto()
    RECOVERY = auto()
    SAFE_MODE = auto()

