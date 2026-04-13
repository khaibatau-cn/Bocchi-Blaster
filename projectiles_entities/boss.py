import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_RADIUS, BOSS_HEALTH_P1, BOSS_HEALTH_P2, BOSS_HEALTH_P3,
    PURPLE
)
 
class Boss:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = BOSS_RADIUS + 20
        self.radius = BOSS_RADIUS
 
        self.health_p1 = BOSS_HEALTH_P1
        self.health_p2 = BOSS_HEALTH_P2
        self.health_p3 = BOSS_HEALTH_P3
        self.health =self.health_p1 + self.health_p2 + self.health_p3
        self.max_health = self.health
        self.phase = 1
        self.alive = True
 
        self.move_timer = 0
        self.move_speed = 2
 
        self.pending_bullets = []
        self.shoot_timer = 0
 
        self.p2_threshold = self.health_p2 + self.health_p3
        self.p3_threshold = self.health_p3
        self.pulse = 0
 
 
class _EnemyBullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.radius = 8
        self.alive = True
        self.color = PURPLE