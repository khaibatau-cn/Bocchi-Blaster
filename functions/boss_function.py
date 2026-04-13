import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    BOSS_RADIUS,
    RED, WHITE, PINK, PINK2, PURPLE, YELLOW, ORANGE
)
 
 
def boss_update(boss, bocchi_x, bocchi_y):
    # moves boss taking bocchix, y as parameters, updates boss phases, 
    # shootings and pulsings
    boss_update_phase(boss)
    boss_move(boss, bocchi_x, bocchi_y)
    boss_shoot(boss, bocchi_x, bocchi_y)
    boss.pulse = (boss.pulse + 3) % 360
 
def boss_update_phase(boss):
    # if boss.health reached the fixed threshold activate phase 3 and 2
    if boss.health <= boss.p3_threshold and boss.phase < 3:
        boss.phase = 3
        boss.move_speed = 4
    elif boss.health <= boss.p2_threshold and boss.phase < 2:
        boss.phase = 2
        boss.move_speed = 3
 
 
def boss_move(boss, bocchi_x, bocchi_y):
    angle = math.atan2(bocchi_y - boss.y, bocchi_x - boss.x)
    boss.x += math.cos(angle) * boss.move_speed
    boss.y += math.sin(angle) * boss.move_speed
    boss.y = max(BOSS_RADIUS, min(boss.y, SCREEN_HEIGHT // 3))
 

def boss_shoot(boss, bocchi_x, bocchi_y):
    # shoot rate increase as boss phases
    rate = {1: 90, 2: 60, 3: 35}[boss.phase]
    boss.shoot_timer += 1
    if boss.shoot_timer >= rate:
        boss.shoot_timer = 0
        boss_fire_at(boss, bocchi_x, bocchi_y)
        if boss.phase >= 2:
            boss_fire_spread(boss)

 
def boss_fire_at(boss, bocchi_x, bocchi_y):
    from projectiles_entities.boss import _EnemyBullet
    angle = math.atan2(bocchi_y - boss.y, bocchi_x - boss.x)
    speed = 4 + boss.phase
    bx = boss.x + math.cos(angle) * (boss.radius + 8)
    by = boss.y + math.sin(angle) * (boss.radius + 8)
    boss.pending_bullets.append(
        _EnemyBullet(bx, by, math.cos(angle) * speed, math.sin(angle) * speed)
    )
 
 
def boss_fire_spread(boss):
    from projectiles_entities.boss import _EnemyBullet
    for angle in [math.pi / 4, 3 * math.pi / 4]:
        # angle in 45 deg and 135 deg
        # loop twice, shooting two discrete shots
        speed = 3
        bx = boss.x + math.cos(angle) * (boss.radius + 8)
        by = boss.y + math.sin(angle) * (boss.radius + 8)
        boss.pending_bullets.append(
            _EnemyBullet(bx, by, math.cos(angle) * speed, math.sin(angle) * speed)
        )
 
 
def boss_take_hit(boss, damage=5):
    boss.health = max(0, boss.health - damage)
    if boss.health <= 0:
        boss.alive = False
 
 
def boss_draw(boss, screen):
    colors = {1: PINK, 2: ORANGE, 3: RED}
    color = colors[boss.phase]
 
    if boss.phase == 3:
        pulse_r = boss.radius + int(6 * abs(math.sin(math.radians(boss.pulse))))
        pygame.draw.circle(screen, PURPLE, (int(boss.x), int(boss.y)), pulse_r, 3)
 
    pygame.draw.circle(screen, color, (int(boss.x), int(boss.y)), boss.radius)
    pygame.draw.circle(screen, WHITE, (int(boss.x), int(boss.y)), boss.radius, 2)
 
    ex, ey = int(boss.x), int(boss.y)
    if boss.phase < 3:
        pygame.draw.line(screen, (60, 20, 60), (ex-20, ey-10), (ex-10, ey-18), 3)
        pygame.draw.line(screen, (60, 20, 60), (ex+10, ey-18), (ex+20, ey-10), 3)
    else:
        pygame.draw.circle(screen, RED, (ex-14, ey-10), 5)
        pygame.draw.circle(screen, RED, (ex+14, ey-10), 5)
 
    pygame.draw.arc(screen, (60, 20, 60),
                    (ex-15, ey+5, 30, 15), math.pi, 2*math.pi, 3)
 
    font = pygame.font.SysFont(None, 22)
    label = font.render(f"Anxiety  Phase {boss.phase}", True, WHITE)
    screen.blit(label, (ex - label.get_width() // 2, int(boss.y) - boss.radius - 36))
 
    bar_w = 200
    bar_h = 12
    bar_x = SCREEN_WIDTH // 2 - bar_w // 2
    bar_y = int(boss.y) + boss.radius + 10
    pygame.draw.rect(screen, (80, 80, 80), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    fill = int(bar_w * boss.health / boss.max_health)
    hp_color = {1: PINK, 2: ORANGE, 3: RED}[boss.phase]
    pygame.draw.rect(screen, hp_color, (bar_x, bar_y, fill, bar_h), border_radius=4)
    pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=4)
 
 
#  _EnemyBullet functions 

def enemy_bullet_update(eb):
    eb.x += eb.dx
    eb.y += eb.dy
    if (eb.x < -20 or eb.x > SCREEN_WIDTH + 20 or
            eb.y < -20 or eb.y > SCREEN_HEIGHT + 20):
        eb.alive = False
 

def enemy_bullet_draw(eb, screen):
    pygame.draw.circle(screen, PURPLE, (int(eb.x), int(eb.y)), eb.radius)
    pygame.draw.circle(screen, WHITE,  (int(eb.x), int(eb.y)), eb.radius, 1)