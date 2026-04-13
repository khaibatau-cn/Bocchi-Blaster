import pygame
import math
import random
from leaderboard import load_records, save_records, is_new_record
from settings import *
# Data classes
from projectiles_entities.bullet  import Bullet
from projectiles_entities.bocchi  import Bocchi
from projectiles_entities.enemy   import Enemy
from projectiles_entities.boss   import Boss, _EnemyBullet
from projectiles_entities.powerups import PowerUp
 # Functions
from functions.bocchi_function  import bocchi_update, bocchi_draw,bocchi_take_hit, can_shoot, reset_cooldown, play_lose_sound, play_win_sounds
from functions.enemy_function   import enemy_update, enemy_draw
from functions.boss_function    import boss_update, boss_draw, boss_take_hit, enemy_bullet_update, enemy_bullet_draw
from functions.bullet_function  import bullet_update, bullet_draw
from functions.powerups_function import powerup_update, powerup_draw
 
from hud import draw_hud

class Game:
    def __init__(self):
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock   = pygame.time.Clock()
        self.running = True
        self.state   = "menu"
        self._reset()

        self.font_big   = pygame.font.SysFont(None, 72)
        self.font_med   = pygame.font.SysFont(None, 44)
        self.font_small = pygame.font.SysFont(None, 28)
        self.font_tiny  = pygame.font.SysFont(None, 22)

        self.power_sounds = []
        for power_sound in ["kita_up.mp3", "ryo_up.mp3", "nijika_up.mp3"]:
            try:
                sound = pygame.mixer.Sound(f"./soundsfx/{power_sound}")
                sound.set_volume(0.6)
                self.power_sounds.append(sound)
            except Exception:
                pass
 
    def _reset(self):
        self.bocchi       = Bocchi(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.bullets      = []
        self.enemy_bullets = []
        self.enemies      = []
        self.boss         = None
 
        self.score           = 0
        self.stage           = 1
        self.wave            = 1
        self.enemies_killed  = 0
        self.enemies_spawned = 0
        self.spawn_timer     = 0
 
        self.wave_clear_timer  = 0
        self.wave_clearing     = False
        self.stage_clear_timer = 0
        self.stage_clearing    = False
 
        self.boss_fight = False
        self.powerups   = []
        self.records    = load_records()
        self.new_record = False
 
    # starfield background random stars for space background (sEishUn cOmplEx reference)
    # each star = [x, y, speed, size]
        self.stars = [] # a different approach
        for i in range(120):
            star = [
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT),
                random.uniform(0.5, 2.0),
                random.randint(1, 3)
            ]
            self.stars.append(star)


    # run
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Menu key handle
            if self.state == "menu" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                        self.running = False
                if event.key == pygame.K_RETURN:
                    self._reset()
                    self.state = "playing"
            # Game Over key handle
            if self.state == "game_over" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.mixer.stop()
                    self._reset()
                    self.state = "playing"
                if event.key == pygame.K_m:
                    pygame.mixer.stop()
                    self._reset()
                    self.state = "menu"
            # Winning key handle
            if self.state == "victory" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    pygame.mixer.stop()
                    self._reset()
                    self.state = "menu"
            # Press Pause key handle
            if self.state == "playing" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "paused"
            # Pausing key handle
            elif self.state == "paused" and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = "playing"
                elif event.key == pygame.K_m:
                    pygame.mixer.stop()
                    self._reset()
                    self.state = "menu"
            # Shoot key handle
            if self.state == "playing":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE] and can_shoot(self.bocchi):
                    self._spawn_bullet()

    def _spawn_bullet(self):

        # getting mouse pos to shoot at mouse direction using atan2
        mouse_x, mouse_y = pygame.mouse.get_pos()
        base_angle = math.atan2(mouse_y - self.bocchi.y, mouse_x - self.bocchi.x)

        # setting bullet speed for Kita powerup
        bullet_spd = BULLET_SPEED
        if self.bocchi.kita_timer > 0:
            bullet_spd = BULLET_SPEED * 1.5
 
        bullets_angles = [0] # default - go in a straight line
        if self.bocchi.ryo_timer > 0:
            bullets_angles = [-math.radians(15), 0, math.radians(15)] # shoots out in 2 more direction -15 deg and 15 deg

        # setting direction x, y for the 2 extended bullets and their velocity
        for offset in bullets_angles:
            angle = base_angle + offset
            dx = math.cos(angle) * bullet_spd
            dy = math.sin(angle) * bullet_spd
            self.bullets.append(Bullet(self.bocchi.x, self.bocchi.y, dx, dy))
 
        reset_cooldown(self.bocchi)

    def update(self):
        if self.state != "playing":
            return
        self._update_stars() # scroll stars
        if self.boss_fight:
            self._update_boss_fight()
        else:
            self._update_wave()
 
    def _update_stars(self):
        # stars scroll downward to give sense of moving through space
        # star [x, y, speed, size] -> s[1] = y + speed and repeat star will move upward if > heigh then = 0 and do again with random x
        for s in self.stars:
            s[1] = s[1] + s[2]
            if s[1] > SCREEN_HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, SCREEN_WIDTH)


    def _update_wave(self):
        if self.wave_clearing:
            self.wave_clear_timer -= 1
            if self.wave_clear_timer <= 0:
                self.wave_clearing = False
                self._start_next_wave()
            return

        if self.stage_clearing:
            self.stage_clear_timer -= 1
            if self.stage_clear_timer <= 0:
                self.stage_clearing = False
                self._start_next_stage()
            return

        bocchi_update(self.bocchi)
        self._spawn_enemy()
        self._update_bullets()
        self._update_enemies()
        self._update_powerups()
        self._check_collision()
        self._check_play_complete()
 
    def _check_play_complete(self):
        # check the status of enemies of wave
        # spawned enemies will be increment by 1 when spawned so if >= threshold
        # and enemies list len equal to 0 (dead enemies will be removed out of the list by Python garbage collector)
        all_spawned = self.enemies_spawned >= ENEMIES_PER_WAVE
        all_dead = len(self.enemies) == 0
        if all_spawned and all_dead:
            self._advance_wave()
 
    def _advance_wave(self):
        if self.wave >= WAVES_PER_STAGE:
            if self.stage >= TOTAL_STAGES:
                # Determining if this is the final wave/stage
                # Call boss and reset enemy_bullets list
                self.boss_fight   = True
                self.boss         = Boss()
                self.enemy_bullets = []
            else:
                self.stage_clearing    = True
                self.stage_clear_timer = 120 # giving time break each stage
        else:
            self.wave            += 1
            self.wave_clearing    = True
            self.wave_clear_timer = 90 # giving time break each wave
 
    def _start_next_wave(self):
        self.enemies_killed  = 0
        self.enemies_spawned = 0
        self.spawn_timer     = 0
        self.enemies         = []
 
    def _start_next_stage(self):
        self.stage          += 1
        self.wave            = 1
        self.enemies_killed  = 0
        self.enemies_spawned = 0
        self.spawn_timer     = 0
        self.enemies         = []
 
    def _spawn_enemy(self):
        if not self.boss_fight:
            if self.enemies_spawned >= ENEMIES_PER_WAVE:
                return
 
        spawn_rate = 120 if self.boss_fight else max(28, 60 - (self.stage - 1) * 10)
        self.spawn_timer += 1

        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            self.enemies.append(Enemy(stage=self.stage))
            if not self.boss_fight:
                self.enemies_spawned += 1
 
    def _update_bullets(self):
        for bullet in self.bullets:
            bullet_update(bullet)
        self.bullets = [b for b in self.bullets if b.alive]
 
    def _update_enemies(self):
        for enemy in self.enemies:
            enemy_update(enemy, self.bocchi.x, self.bocchi.y)
            self.enemy_bullets.extend(enemy.pending_bullets)
            enemy.pending_bullets.clear()
 
        self.enemies = [e for e in self.enemies if e.alive]
 
        for eb in self.enemy_bullets:
            enemy_bullet_update(eb)
 
    def _check_collision(self):
        # Enemies and bocchi bullets
        for e in self.enemies:
            for b in self.bullets:
                if not b.alive:
                    continue
                distance = math.hypot(b.x - e.x, b.y - e.y)
                if distance < (b.radius + e.radius):
                    b.alive = False
                    e.health -= 1
                    if e.health <= 0:
                        e.alive = False
                        self.score += 10
                        self.enemies_killed += 1
                        if random.random() < POWERUP_DROP_CHANCE:
                            self.powerups.append(PowerUp(e.x, e.y))
        # Collision bocchi and enemies
            dist_to_player = math.hypot(self.bocchi.x - e.x, self.bocchi.y - e.y)
            if dist_to_player < (self.bocchi.radius + e.radius) and not self.bocchi.invincible:
                e.alive = False
                bocchi_take_hit(self.bocchi)
                if self.bocchi.health <= 0:
                    self.state      = "game_over"
                    play_lose_sound(self.bocchi)
                    self.new_record = is_new_record(self.score)
                    self.records    = save_records(self.score, self.stage, self.wave)
        
        # Bocchi and enemies bullets
        for eb in self.enemy_bullets[:]:
            if math.hypot(eb.x - self.bocchi.x, eb.y - self.bocchi.y) < eb.radius + self.bocchi.radius:
                eb.alive = False
                bocchi_take_hit(self.bocchi)
                if self.bocchi.health <= 0:
                    self.state      = "game_over"
                    play_lose_sound(self.bocchi)
                    self.new_record = is_new_record(self.score)
                    self.records    = save_records(self.score, self.stage, self.wave)

 
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]
 
    def _update_boss_fight(self):
        if self.boss is None or not self.boss.alive:
            self.state      = "victory"
            play_win_sounds(self.bocchi)
            self.new_record = is_new_record(self.score)
            self.records    = save_records(self.score, self.stage, self.wave)
            return
 
        bocchi_update(self.bocchi)
        self._spawn_enemy()
        self._update_bullets()
        self._update_powerups()
        self._update_enemies()
        self._check_collision()
 
        boss_update(self.boss, self.bocchi.x, self.bocchi.y)
 
        self.enemy_bullets.extend(self.boss.pending_bullets)
        self.boss.pending_bullets.clear()
 
        for eb in self.enemy_bullets:
            enemy_bullet_update(eb)
        self.enemy_bullets = [eb for eb in self.enemy_bullets if eb.alive]
 
        # boss vs Bocchi's bullets
        for b in self.bullets[:]:
            if math.hypot(b.x - self.boss.x, b.y - self.boss.y) < b.radius + self.boss.radius:
                b.alive = False
                boss_take_hit(self.boss)
                self.score += 5
 
        # boss bullets vs Bocchi
        for eb in self.enemy_bullets[:]:
            if math.hypot(eb.x - self.bocchi.x, eb.y - self.bocchi.y) < eb.radius + self.bocchi.radius:
                eb.alive = False
                bocchi_take_hit(self.bocchi)
                if self.bocchi.health <= 0:
                    self.state = "game_over"
                    play_lose_sound(self.bocchi)
                    self.new_record = is_new_record(self.score)
                    self.records = save_records(self.score, self.stage, self.wave)
 
    def _update_powerups(self):
        for p in self.powerups:
            powerup_update(p)
            if math.hypot(self.bocchi.x - p.x, self.bocchi.y - p.y) < self.bocchi.radius + p.radius:
                self._apply_powerup(p.kind)
                p.alive = False
        self.powerups = [p for p in self.powerups if p.alive]

    def _apply_powerup(self, power):
        if power == "nijika":
            if self.power_sounds:
                self.power_sounds[2].stop()
                self.power_sounds[2].set_volume(0.5)
                self.power_sounds[2].play()
            self.bocchi.health = min(self.bocchi.health + 1, self.bocchi.max_health)
 
        elif power == "ryo":
            if self.power_sounds:
                self.power_sounds[1].stop()
                self.power_sounds[1].set_volume(0.5)
                self.power_sounds[1].play()
            self.bocchi.ryo_timer = RYO_DURATION
 
        elif power == "kita":
            if self.power_sounds:
                self.power_sounds[0].stop()
                self.power_sounds[0].set_volume(0.5)
                self.power_sounds[0].play()
            # direct attribute change: simplest way to apply a speed boost
            # store original speed so can restore it after the timer runs out
            self.bocchi.speed = PLAYER_SPEED * 1.3
            self.bocchi.shoot_cooldown_base = 8
            self.bocchi.kita_timer = KITA_DURATION

    # Draw
 
    def draw(self):
        self.screen.fill(DARK)
        self._draw_stars()
 
        if self.state == "menu":
            self._draw_menu()
        elif self.state == "playing":
            self._draw_game()
        elif self.state == "game_over":
            self._draw_game()
            self._draw_game_over()
        elif self.state == "victory":
            self._draw_game()
            self._draw_victory()
        elif self.state == "paused":
            self._draw_game()
            self._draw_pause()
 
        pygame.display.flip()
 
    def _draw_stars(self):
        for s in self.stars:
            brightness = min(255, 80 + int(s[2] * 80))
            color      = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(s[0]), int(s[1])), s[3])
 
    def _draw_game(self):
        bocchi_draw(self.bocchi, self.screen, debug=True)
 
        for b in self.bullets:
            bullet_draw(b, self.screen)
        for eb in self.enemy_bullets:
            enemy_bullet_draw(eb, self.screen)
        for p in self.powerups:
            powerup_draw(p, self.screen)
        for e in self.enemies:
            enemy_draw(e, self.screen)
        if self.boss_fight and self.boss:
            boss_draw(self.boss, self.screen)
 
        draw_hud(self.screen, self.bocchi, self.score,
                 self.stage, self.wave, WAVES_PER_STAGE, self.font_small)

        if self.wave_clearing:
            self._draw_centered_text("Wave Clear!", self.font_med, YELLOW, SCREEN_HEIGHT // 2)
        if self.stage_clearing:
            self._draw_centered_text(f"Stage {self.stage} Complete!", self.font_med, PINK, SCREEN_HEIGHT // 2)
 
    def _draw_menu(self):
        self._draw_centered_text("Bocchi Blaster", self.font_big,  PINK,   180)
        self._draw_centered_text("~ defeat the anxiety ~", self.font_small, PURPLE, 250)
        pygame.draw.line(self.screen, PINK2,
                         (SCREEN_WIDTH//2 - 160, 280), (SCREEN_WIDTH//2 + 160, 280), 1)
        self._draw_centered_text("ENTER  —  Start",          self.font_small, WHITE,  320)
        self._draw_centered_text("SPACE  —  Shoot",          self.font_small, WHITE,  352)
        self._draw_centered_text("WASD / Arrows  —  Move",   self.font_small, WHITE,  384)
        self._draw_centered_text("ESC  —  Pause",            self.font_small, GRAY,   416)
        pygame.draw.line(self.screen, PINK2,
                         (SCREEN_WIDTH//2 - 160, 448), (SCREEN_WIDTH//2 + 160, 448), 1)
        self._draw_centered_text(
            f"{TOTAL_STAGES} Stages  •  {WAVES_PER_STAGE} Waves each  •  Boss on Stage {TOTAL_STAGES}",
            self.font_tiny, GRAY, 470)
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.004))
        c = int(180 + 60 * pulse)
        self._draw_centered_text("Press ENTER", self.font_small, (c, c//2, c), 530)
 
    def _draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 0, 20, 180))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("Bocchi is ded of anxiety", self.font_big,  PINK,  180)
        self._draw_centered_text(f"Final Score:  {self.score}", self.font_med, WHITE, 270)
        self._draw_centered_text(f"Reached Stage {self.stage}  Wave {self.wave}",
                                 self.font_small, GRAY, 330)
        pygame.draw.line(self.screen, PINK2,
                         (SCREEN_WIDTH//2 - 140, 370), (SCREEN_WIDTH//2 + 140, 370), 1)
        self._draw_centered_text("R  —  Play again", self.font_small, YELLOW, 400)
        self._draw_centered_text("M  —  Main menu",  self.font_small, WHITE,  436)
        if self.new_record:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            c     = int(180 + 75 * pulse)
            self._draw_centered_text("NEW PERSONAL RECORD!", self.font_small, (255, c, 50), 476)
        self._draw_leaderboard(500)
 
    def _draw_victory(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 0, 30, 180))
        self.screen.blit(overlay, (0, 0))
        pulse = abs(math.sin(pygame.time.get_ticks() * 0.003))
        g = int(180 + 60 * pulse)
        self._draw_centered_text("Anxiety Defeated!", self.font_big, (255, g, 50), 170)
        self._draw_centered_text("Bocchi did it!  The band plays on.", self.font_small, WHITE, 255)
        self._draw_centered_text(f"Final Score:  {self.score}", self.font_med, YELLOW, 310)
        pygame.draw.line(self.screen, PINK2,
                         (SCREEN_WIDTH//2 - 140, 360), (SCREEN_WIDTH//2 + 140, 360), 1)
        self._draw_centered_text("M  —  Main menu", self.font_small, WHITE, 400)
        if self.new_record:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005))
            c     = int(180 + 75 * pulse)
            self._draw_centered_text("NEW PERSONAL RECORD!", self.font_small, (255, c, 50), 440)
        self._draw_leaderboard(464)
 
    def _draw_leaderboard(self, start_y):
        self._draw_centered_text("Personal Records", self.font_small, YELLOW, start_y)
        if not self.records:
            self._draw_centered_text("Let's do better next try for new Personal Record!!", self.font_tiny, GRAY, start_y + 30)
            return
        col_rank  = SCREEN_WIDTH // 2 - 220
        col_score = SCREEN_WIDTH // 2 - 80
        col_stage = SCREEN_WIDTH // 2 + 40
        col_date  = SCREEN_WIDTH // 2 + 130
        y = start_y + 28
        for label, x in [("#", col_rank), ("Score", col_score),
                         ("Stage/Wave", col_stage), ("Date", col_date)]:
            surf = self.font_tiny.render(label, True, GRAY)
            self.screen.blit(surf, (x, y))
        pygame.draw.line(self.screen, GRAY,
                         (col_rank, y + 18), (col_date + 100, y + 18), 1)
        for i, r in enumerate(self.records):
            y     = start_y + 48 + i * 22
            color = YELLOW if i == 0 else WHITE
            self.screen.blit(self.font_tiny.render(f"{i+1}.",         True, color), (col_rank,  y))
            self.screen.blit(self.font_tiny.render(str(r["score"]),   True, color), (col_score, y))
            self.screen.blit(self.font_tiny.render(f"S{r['stage']} W{r['wave']}", True, color), (col_stage, y))
            self.screen.blit(self.font_tiny.render(r["date"],         True, GRAY),  (col_date,  y))
 
    def _draw_pause(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 0, 20, 160))
        self.screen.blit(overlay, (0, 0))
        self._draw_centered_text("Paused",           self.font_big,   WHITE,  220)
        self._draw_centered_text("ESC  —  Resume",   self.font_small, YELLOW, 320)
        self._draw_centered_text("M  —  Main menu",  self.font_small, WHITE,  356)
 
    def _draw_centered_text(self, text, font, color, y):
        surf = font.render(text, True, color)
        self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))