import pygame
import random
from settings import (
    PLAYER_SPEED, PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_HEALTH, PLAYER_MAX_HEALTH,
    PLAYER_RADIUS, SHOOT_COOLDOWN, INVINCIBLE_DURATION,
    SCREEN_WIDTH, SCREEN_HEIGHT, PINK, WHITE
)

class Bocchi:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.radius = PLAYER_RADIUS
        self.health = PLAYER_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.shoot_cooldown_base = SHOOT_COOLDOWN
        self.invincible = False
        self.invincible_timer = 0
        self.cooldown = 0
        self.kita_timer = 0
        self.ryo_timer = 0
        self.vel_x = 0
        self.vel_y = 0

        raw = pygame.image.load("./images/bocchi_nor.png").convert_alpha()
        self.image = pygame.transform.scale(raw, (self.width, self.height))
        self.image.set_colorkey((255, 255, 255))

        # pygame.Rect(x, y, width, height)
        # pygame.Rect(x-24, y-32, 48, 64)
        self.rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width, self.height
        )
 
        try:
            hit_raw = pygame.image.load("./images/bocchi_hit.png").convert_alpha()
            self.hit_image = pygame.transform.scale(hit_raw, (self.width, self.height))
            self.hit_image.set_colorkey((255, 255, 255))
        except Exception:
            self.hit_image = self.image
 
        self.hit_sounds = []
        for hit_sound in ["bocchi_hit1.mp3", "bocchi_hit2.mp3", "bocchi_hit3.mp3"]:
            try:
                sound = pygame.mixer.Sound(f"./soundsfx/{hit_sound}")
                sound.set_volume(0.5)
                self.hit_sounds.append(sound)
            except Exception:
                pass
 
        self.lose_sounds = []
        for lose_sound in ["bocchi_lose1.mp3", "bocchi_lose2.mp3", "bocchi_lose3.mp3"]:
            try:
                sound = pygame.mixer.Sound(f"./soundsfx/{lose_sound}")
                sound.set_volume(0.5)
                self.lose_sounds.append(sound)
            except Exception:
                pass
 
        try:
            self.win_sound = pygame.mixer.Sound("./soundsfx/win.mp3")
            self.win_sound.set_volume(0.4)
        except Exception:
            self.win_sound = None