from hashlib import md5
from enum import Enum


# Fg color enums (ANSI color codes)
# Precalculated available color list is also provided
# AuxFG for special purposes

class FG(Enum):
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    # For further possible usage
    # LIGHT_GRAY = 37
    # LIGHT_YELLOW = 93
    # LIGHT_BLUE = 94
    # LIGHT_MAGENTA = 95
    # LIGHT_CYAN = 96


class AuxFG(Enum):
    RED = 31
    LIGHT_GREEN = 92


color_list = list(FG)


# Functions

def colorize(text: str, fg: FG | AuxFG, bold: bool = False):
    style_parts = []
    if fg:
        style_parts.append(str(fg.value))
    if bold:
        style_parts.append("1")
    return f"\x1b[{';'.join(style_parts)}m{text}\x1b[0m" if fg else text


def get_color_for(data: bytes):
    return color_list[int(md5(data).hexdigest(), 16) % len(color_list)]
