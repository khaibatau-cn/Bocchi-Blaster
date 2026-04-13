from settings import BULLET_RADIUS, BULLET_SPEED, YELLOW
 
class Bullet:
    def __init__(self, x, y, dx, dy, color=None):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.speed = BULLET_SPEED
        self.radius = BULLET_RADIUS
        self.color = color if color is not None else YELLOW
        self.alive = True