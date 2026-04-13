import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
 
 
def bullet_update(bullet):
    # moving bullets and check if out of screen
    bullet.x += bullet.dx
    bullet.y += bullet.dy
    off = bullet.radius + 10
    # add 10 for the bullet to go out of the screen before giving False state
    if (bullet.x < -off or bullet.x > SCREEN_WIDTH  + off or
            bullet.y < -off or bullet.y > SCREEN_HEIGHT + off):
        bullet.alive = False


def bullet_draw(bullet, screen):
    pygame.draw.circle(screen, bullet.color,
                       (int(bullet.x), int(bullet.y)), bullet.radius, 0)