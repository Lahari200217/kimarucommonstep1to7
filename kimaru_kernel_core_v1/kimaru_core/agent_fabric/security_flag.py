from enum import Enum
class SecurityFlag(str, Enum):
    GREEN_INTERNAL = "GREEN"
    YELLOW_INTRA = "YELLOW"
    RED_EXTERNAL = "RED"
