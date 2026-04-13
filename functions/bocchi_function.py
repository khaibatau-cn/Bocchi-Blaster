import pygame
import random
from settings import (
    PLAYER_SPEED, SHOOT_COOLDOWN, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, INVINCIBLE_DURATION
)

def bocchi_input_handle(bocchi):
    # reads keyboard inputs and sets velocity of bocchi object
    keys = pygame.key.get_pressed()
    bocchi.vel_x = 0
    bocchi.vel_y = 0

    if keys[pygame.K_LEFT]  or keys[pygame.K_a]: bocchi.vel_x = -bocchi.speed # moving left -x
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: bocchi.vel_x =  bocchi.speed # moving right +x
    if keys[pygame.K_UP]    or keys[pygame.K_w]: bocchi.vel_y = -bocchi.speed # moving up -y
    if keys[pygame.K_DOWN]  or keys[pygame.K_s]: bocchi.vel_y =  bocchi.speed # moving down +y

def power_timer(bocchi):
    # ticks Kita and Ryo buff timers down
    # Example: when buff is collected -> set timer of that buf to 100
    # timer will tick down 100 -> 0 if is 0 then restore default stats
    if hasattr(bocchi, "kita_timer") and bocchi.kita_timer > 0:
        bocchi.kita_timer -= 1
        if bocchi.kita_timer <= 0:
            bocchi.speed = PLAYER_SPEED
            bocchi.shoot_cooldown_base = SHOOT_COOLDOWN

    if hasattr(bocchi, "ryo_timer") and bocchi.ryo_timer > 0:
        bocchi.ryo_timer -= 1
        if bocchi.ryo_timer <= 0:
            pass

def bocchi_update(bocchi):
    # moves Bocchi, clamps to screen, sync rectangle for clamping, ticks shoot cooldown
    bocchi_input_handle(bocchi)
    power_timer(bocchi)

    # moving Bocchi
    # getting vel_x and vel_y from input_handle() and add to x, y pos of bocchi to update pos
    bocchi.x = bocchi.x + bocchi.vel_x
    bocchi.y = bocchi.y + bocchi.vel_y

    # clamping
    # since bocchi actual shape drawn is a rectangle so half the width and height
    # otherwise half of bocchi image will be hidden by the screen edge
    half_widght = bocchi.width  // 2
    half_height = bocchi.height // 2
    bocchi.x = max(half_widght, min(bocchi.x, SCREEN_WIDTH  - half_widght))
    bocchi.y = max(half_height, min(bocchi.y, SCREEN_HEIGHT - half_height))
    # bocchi.x after limitng will be max(24, min(self.x, 1076))
    # bocchi.y after limitng will be max(32, min(self.x, 718)

    # sync the rect
    bocchi.rect.centerx = int(bocchi.x)
    bocchi.rect.centery  = int(bocchi.y)
    
    # same functioning as power timer
    # set cooldown to a value and count down until 0
    if bocchi.cooldown > 0:
        bocchi.cooldown -= 1
    
    # invincibility after hit check
    if bocchi.invincible:
        bocchi.invincible_timer -= 1
        if bocchi.invincible_timer <= 0:
            bocchi.invincible = False

def bocchi_take_hit(bocchi, damage=1):
    # applies damage if not invincible, starts invincibility window
    if bocchi.invincible:
        return
    bocchi.health = max(0, bocchi.health - damage)
    bocchi.invincible = True
    bocchi.invincible_timer = INVINCIBLE_DURATION
    if bocchi.hit_sounds:
        random.choice(bocchi.hit_sounds).play()

def play_lose_sound(bocchi):
    if bocchi.lose_sounds:
        random.choice(bocchi.lose_sounds).play()

def play_win_sounds(bocchi):
    if bocchi.win_sound:
        bocchi.win_sound.play()

def can_shoot(bocchi):
    return bocchi.cooldown == 0
 
def reset_cooldown(bocchi):
    bocchi.cooldown = bocchi.shoot_cooldown_base

def bocchi_draw(bocchi, screen, debug=False):
    # link check: skip this frame if in invisible blink window
    if bocchi.invincible and (bocchi.invincible_timer // 6) % 2 == 1:
        return
    # if invincible == True means just got hit img = bocchi hit image
    if bocchi.invincible:
        img = bocchi.hit_image 
    else:
        img = bocchi.image
    screen.blit(img, bocchi.rect)
    # debug overlays when debug=True
    if debug:
        pygame.draw.circle(screen, WHITE,
                           (int(bocchi.x), int(bocchi.y)), bocchi.radius, 1)
        font_tiny = pygame.font.SysFont(None, 22)
        text = font_tiny.render(f"{int(bocchi.x)}, {int(bocchi.y)}", True, WHITE)
        screen.blit(text, (bocchi.x - 20, bocchi.y - 70))
 