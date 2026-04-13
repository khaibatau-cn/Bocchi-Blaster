import pygame
import math
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, PINK, PINK2, RED, YELLOW, GRAY, DARK_BLUE,
    WAVES_PER_STAGE, KITA_DURATION, RYO_DURATION
)

def draw_hud(screen, bocchi, score, stage, wave, waves_per_stage, font_small):
    # health
    heart_size = 22
    for i in range(bocchi.max_health):
        x = 14 + i * (heart_size + 6)
        y = 14
        if i < bocchi.health:
            _draw_heart(screen, x, y, heart_size, PINK2)
        else:
            _draw_heart(screen, x, y, heart_size, GRAY)

    # score
    score_surf = font_small.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surf, (SCREEN_WIDTH // 2 - score_surf.get_width() // 2, 14))

    # stage / wave
    stage_surf = font_small.render(f"Stage {stage}  Wave {wave}/{waves_per_stage}", True, YELLOW)
    screen.blit(stage_surf, (SCREEN_WIDTH - stage_surf.get_width() - 14, 14))

    # buff timers
    # Shows active powerup timers in the bottom-left corner.
    # Each bar is a pill: colored fill shrinks as the buff drains.
    _draw_buff_timers(screen, bocchi, font_small)


def _draw_buff_timers(screen, bocchi, font):
    # Layout: stacked pills in the bottom-left, above the floor
    pill_w = 190
    pill_h = 22
    pad = 7 # gap between pills
    start_x = 14
    start_y = SCREEN_HEIGHT - 14  # stack upward

    active_buffs = []

    # Kita: speed + fire-rate (RED tint)
    if bocchi.kita_timer > 0:
        secs = math.ceil(bocchi.kita_timer / 60)
        frac = bocchi.kita_timer / KITA_DURATION
        active_buffs.append(("Kita Aura", frac, secs, RED))

    # Ryo: triple shot (DARK_BLUE tint)
    if bocchi.ryo_timer > 0:
        secs = math.ceil(bocchi.ryo_timer / 60)
        frac = bocchi.ryo_timer / RYO_DURATION
        active_buffs.append(("Ryo Tuff", frac, secs, DARK_BLUE))

    # draw from bottom upward
    for i, (label, frac, secs, color) in enumerate(active_buffs):
        y = start_y - (i + 1) * (pill_h + pad)

        # background track
        pygame.draw.rect(screen, (50, 50, 50),
                         (start_x, y, pill_w, pill_h), border_radius=6)
        # colored fill — shrinks as timer drains
        fill_w = max(4, int(pill_w * frac))
        pygame.draw.rect(screen, color,
                         (start_x, y, fill_w, pill_h), border_radius=6)
        # border
        pygame.draw.rect(screen, WHITE,
                         (start_x, y, pill_w, pill_h), 1, border_radius=6)

        # label + seconds remaining
        text = font.render(f"{label}  {secs}s", True, WHITE)
        tx = start_x + 8
        ty = y + (pill_h - text.get_height()) // 2
        screen.blit(text, (tx, ty))


def _draw_heart(screen, x, y, size, color):
    r = size // 4
    pygame.draw.circle(screen, color, (x + r,         y + r), r)
    pygame.draw.circle(screen, color, (x + size - r,  y + r), r)
    points = [
        (x,             y + r),
        (x + size,      y + r),
        (x + size // 2, y + size)
    ]
    pygame.draw.polygon(screen, color, points)

