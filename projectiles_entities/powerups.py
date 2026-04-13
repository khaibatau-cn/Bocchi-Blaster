import random
from settings import SCREEN_HEIGHT, YELLOW, DARK_BLUE, RED
 
class PowerUp:
    TYPES = ["nijika", "ryo", "kita"]
    COLORS = {
        "nijika": YELLOW,
        "ryo":    DARK_BLUE,
        "kita":   RED
    }
    LABELS = {"nijika": "N", "ryo": "R", "kita": "K"}
 
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.kind = random.choice(self.TYPES)
        self.radius = 14
        self.speed = 1.0
        self.alive = True
        self.timer = 480   # 8 seconds at 60fps