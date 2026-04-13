import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, ENEMY_SHOOT_COOLDOWN, ENEMY_BULLET_SPEED, RED
)

def enemy_update(enemy, bocchi_x, bocchi_y):
    # moves enemy toward bocchi using atan2, fires bullets on timer
    angle = math.atan2(bocchi_y - enemy.y, bocchi_x - enemy.x)
    enemy.x += math.cos(angle) * enemy.speed
    enemy.y += math.sin(angle) * enemy.speed
 
    if (enemy.x < -600 or enemy.x > SCREEN_WIDTH + 600 or
            enemy.y < -600 or enemy.y > SCREEN_HEIGHT + 600):
        enemy.alive = False
 
    enemy_try_shoot(enemy, bocchi_x, bocchi_y)

def enemy_try_shoot(enemy, bocchi_x, bocchi_y):
    # fires a bullet toward bocchi when cooldown reaches 0
    enemy.shoot_timer += 1
    if enemy.shoot_timer < ENEMY_SHOOT_COOLDOWN:
        return
    enemy.shoot_timer = 0
 
    from projectiles_entities.boss import _EnemyBullet
    angle = math.atan2(bocchi_y - enemy.y, bocchi_x - enemy.x)
    dx = math.cos(angle) * ENEMY_BULLET_SPEED
    dy = math.sin(angle) * ENEMY_BULLET_SPEED
    bx = enemy.x + math.cos(angle) * (enemy.radius + 6)
    by = enemy.y + math.sin(angle) * (enemy.radius + 6)
    enemy.pending_bullets.append(_EnemyBullet(bx, by, dx, dy))
 
 
def enemy_draw(enemy, screen):
    # draws the blob sprite or fallback circle, plus health bar if damaged
    if enemy.image:
        screen.blit(enemy.image, (
            int(enemy.x) - enemy.radius,
            int(enemy.y) - enemy.radius
        ))
    else:
        pygame.draw.circle(screen, RED, (int(enemy.x), int(enemy.y)), enemy.radius)
 
    if enemy.health < enemy.max_health:
        bar_width = enemy.radius * 2 #60 * 2 = 120
        bar_height = 5
        bar_x = int(enemy.x) - enemy.radius
        bar_y = int(enemy.y) - enemy.radius - 10

        #creating a health bar of color grey
        pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))
        fill = int(bar_width * enemy.health / enemy.max_health)
        # overlay the grey health bar with red 
        # example enemy got hit once = 2/3 HP
        # then fill with 120 * 2/3 = 80 taking a portion of the healthbar creating lost hp
        pygame.draw.rect(screen, RED, (bar_x, bar_y, fill, bar_height))
