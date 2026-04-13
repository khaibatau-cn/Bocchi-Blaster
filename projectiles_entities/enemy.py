import pygame
import random
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_HEALTH, ENEMY_RADIUS, ENEMY_SPEED, RED
)
 
class Enemy:
    def __init__(self, stage=1):
        # stage=1 is the default — higher stages increase speed and health
        self.speed = ENEMY_SPEED + (stage - 1) * 0.4
        self.radius = ENEMY_RADIUS
        self.health = ENEMY_HEALTH + (stage - 1)
        self.max_health = self.health
        self.alive = True
        self.shoot_timer = 0
        self.pending_bullets = []
 
        # spawn from a random edge of the screen
        side = random.choice(["top", "bottom", "left", "right"])
        if side == "top":
            self.x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
            self.y = -ENEMY_RADIUS
        elif side == "bottom":
            self.x = random.randint(ENEMY_RADIUS, SCREEN_WIDTH - ENEMY_RADIUS)
            self.y = SCREEN_HEIGHT + ENEMY_RADIUS
        elif side == "left":
            self.x = -ENEMY_RADIUS
            self.y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
        elif side == "right":
            self.x = SCREEN_WIDTH + ENEMY_RADIUS
            self.y = random.randint(ENEMY_RADIUS, SCREEN_HEIGHT - ENEMY_RADIUS)
 
        try:
            img = pygame.image.load("./images/blob.png").convert_alpha()
            size = ENEMY_RADIUS * 2
            self.image = pygame.transform.scale(img, (size, size))
            self.image.set_colorkey((255, 255, 255))
        except Exception:
            self.image = None