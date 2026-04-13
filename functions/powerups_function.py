import pygame
from settings import SCREEN_HEIGHT, WHITE
 
 
def powerup_update(powerup):
    powerup.y += powerup.speed
    powerup.timer -= 1

    # when moving out of the screen or alive time ran out = unalive powerup
    if powerup.timer <= 0 or powerup.y > SCREEN_HEIGHT + powerup.radius:
        powerup.alive = False
 
 
def powerup_draw(powerup, screen):
    color = powerup.COLORS[powerup.kind]
    pygame.draw.circle(screen, color, (int(powerup.x), int(powerup.y)), powerup.radius)
    pygame.draw.circle(screen, WHITE, (int(powerup.x), int(powerup.y)), powerup.radius, 2)
 
    font = pygame.font.SysFont(None, 20)
    surf = font.render(powerup.LABELS[powerup.kind], True, WHITE)
    screen.blit(surf, (
        int(powerup.x) - surf.get_width()  // 2,
        int(powerup.y) - surf.get_height() // 2
    ))
 