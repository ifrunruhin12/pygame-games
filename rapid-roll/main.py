import os
import sys
import math
import random
import pygame

# Allow importing common_ui from parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    import common_ui
except ImportError:
    common_ui = None

pygame.init()

# ================= CONFIGURATION =================
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 720
FPS = 60

# Spikes Zone
TOP_SPIKES_HEIGHT = 36

# Ball Settings
BALL_RADIUS = 13
BALL_ACCEL = 0.65
BALL_FRICTION = 0.88
BALL_ICE_FRICTION = 0.98
BALL_MAX_SPEED = 5.5
GRAVITY = 0.42
MAX_FALL_SPEED = 10.5

# Platforms Settings
BASE_SCROLL_SPEED = 2.2
PLATFORM_WIDTH_MIN = 85
PLATFORM_WIDTH_MAX = 120
PLATFORM_HEIGHT = 16
PLATFORM_SPACING = 110

# Colors (Modern Arcade Palette)
COLOR_BG = (14, 16, 26)
COLOR_BG_GRID = (22, 26, 42)
COLOR_TOP_SPIKES = (230, 50, 50)
COLOR_TOP_SPIKES_DARK = (150, 25, 25)

COLOR_BALL = (235, 60, 60)
COLOR_BALL_STRIPE = (255, 160, 160)
COLOR_BALL_HIGHLIGHT = (255, 220, 220)

COLOR_PLAT_NORMAL = (70, 80, 110)
COLOR_PLAT_NORMAL_RIM = (0, 215, 255)
COLOR_PLAT_SPIKE = (190, 40, 40)
COLOR_PLAT_SPRING = (255, 180, 30)
COLOR_PLAT_MOVING = (150, 60, 230)
COLOR_PLAT_CRUMBLE = (180, 130, 80)
COLOR_PLAT_ICE = (140, 220, 255)


def draw_hud_text(surface, text, x, y, size=22, color=(255, 255, 255), align="topleft"):
    if common_ui:
        return common_ui.draw_text(surface, text, x, y, size=size, color=color, align=align)
    try:
        font = pygame.font.Font(None, size)
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        setattr(rect, align, (x, y))
        surface.blit(surf, rect)
        return rect
    except Exception:
        return pygame.Rect(x, y, len(text) * 10, size)


class Particle:
    def __init__(self, x, y, color, size_range=(2, 5), speed_range=(1.5, 4.5)):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.size = random.uniform(*size_range)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            sz = max(1, int(self.size * (self.life / self.max_life)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), sz)


class FloatingPopup:
    def __init__(self, text, x, y, color=(255, 255, 0)):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 40

    def update(self):
        self.y -= 0.8
        self.life -= 1

    def draw(self, surface):
        draw_hud_text(surface, self.text, int(self.x), int(self.y), size=18, color=self.color, align="center")


class Pickup:
    def __init__(self, x, y, item_type):
        self.x = x
        self.y = y
        self.item_type = item_type  # "HEART" or "GEM"
        self.timer = random.uniform(0, 10)
        self.collected = False

    def update(self, scroll_speed):
        self.y -= scroll_speed
        self.timer += 0.05

    def draw(self, surface):
        bob = math.sin(self.timer * 4) * 3
        cx = int(self.x)
        cy = int(self.y + bob)

        if self.item_type == "HEART":
            # Red heart shape
            r = 6
            pygame.draw.circle(surface, (255, 50, 80), (cx - 4, cy - 3), r)
            pygame.draw.circle(surface, (255, 50, 80), (cx + 4, cy - 3), r)
            pygame.draw.polygon(surface, (255, 50, 80), [(cx - 9, cy - 2), (cx + 9, cy - 2), (cx, cy + 9)])
            pygame.draw.circle(surface, (255, 180, 200), (cx - 4, cy - 4), 2)
        else:
            # Gold Gem
            pts = [(cx, cy - 8), (cx + 7, cy), (cx, cy + 8), (cx - 7, cy)]
            pygame.draw.polygon(surface, (255, 215, 0), pts)
            pygame.draw.polygon(surface, (255, 255, 200), [(cx, cy - 5), (cx + 4, cy), (cx, cy + 5), (cx - 4, cy)])


class Platform:
    def __init__(self, x, y, width, p_type="NORMAL"):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)
        self.p_type = p_type  # NORMAL, SPIKE, SPRING, MOVING, CRUMBLE, ICE
        self.landed = False
        self.crumble_timer = 0
        self.crumble_active = False
        self.crumble_destroyed = False
        self.vx = 2.0 if p_type == "MOVING" else 0.0
        self.pickup = None

        # Random pickup chance on normal, spring, ice platforms
        if p_type in ["NORMAL", "SPRING", "ICE"] and random.random() < 0.28:
            ptype = "HEART" if random.random() < 0.25 else "GEM"
            self.pickup = Pickup(self.rect.centerx, self.rect.top - 12, ptype)

    def update(self, scroll_speed):
        self.rect.y -= scroll_speed

        if self.pickup:
            self.pickup.update(scroll_speed)

        # Moving platform horizontal oscillation
        if self.p_type == "MOVING":
            self.rect.x += self.vx
            if self.rect.left <= 20:
                self.rect.left = 20
                self.vx = abs(self.vx)
            elif self.rect.right >= SCREEN_WIDTH - 20:
                self.rect.right = SCREEN_WIDTH - 20
                self.vx = -abs(self.vx)

            if self.pickup:
                self.pickup.x = self.rect.centerx

        # Crumble timing
        if self.crumble_active:
            self.crumble_timer += 1
            if self.crumble_timer > 24:
                self.crumble_destroyed = True

    def draw(self, surface):
        if self.crumble_destroyed:
            return

        ox = 0
        oy = 0
        if self.crumble_active:
            # Shake effect
            ox = random.randint(-2, 2)
            oy = random.randint(-1, 1)

        draw_rect = pygame.Rect(self.rect.x + ox, self.rect.y + oy, self.rect.width, self.rect.height)

        if self.p_type == "NORMAL":
            pygame.draw.rect(surface, COLOR_PLAT_NORMAL, draw_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_PLAT_NORMAL_RIM, (draw_rect.x, draw_rect.y, draw_rect.width, 3), border_radius=2)

        elif self.p_type == "SPIKE":
            pygame.draw.rect(surface, COLOR_PLAT_SPIKE, draw_rect, border_radius=4)
            # Spikes along top surface
            spike_w = 8
            num_spikes = self.rect.width // spike_w
            for i in range(num_spikes):
                sx = draw_rect.x + i * spike_w
                pts = [(sx, draw_rect.y), (sx + spike_w // 2, draw_rect.y - 7), (sx + spike_w, draw_rect.y)]
                pygame.draw.polygon(surface, (255, 60, 60), pts)
                pygame.draw.polygon(surface, (255, 180, 180), [(sx + 2, draw_rect.y), (sx + spike_w // 2, draw_rect.y - 5), (sx + spike_w - 2, draw_rect.y)])

        elif self.p_type == "SPRING":
            pygame.draw.rect(surface, (60, 50, 40), draw_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_PLAT_SPRING, (draw_rect.x, draw_rect.y, draw_rect.width, 4), border_radius=2)
            # Center spring icon
            cx = draw_rect.centerx
            cy = draw_rect.centery
            pygame.draw.rect(surface, (255, 230, 80), (cx - 14, cy - 3, 28, 6), border_radius=2)

        elif self.p_type == "MOVING":
            pygame.draw.rect(surface, COLOR_PLAT_MOVING, draw_rect, border_radius=4)
            pygame.draw.rect(surface, (210, 130, 255), (draw_rect.x, draw_rect.y, draw_rect.width, 3), border_radius=2)
            # Directional arrows
            cx = draw_rect.centerx
            cy = draw_rect.centery
            pygame.draw.polygon(surface, (255, 255, 255), [(cx - 8, cy), (cx - 4, cy - 3), (cx - 4, cy + 3)])
            pygame.draw.polygon(surface, (255, 255, 255), [(cx + 8, cy), (cx + 4, cy - 3), (cx + 4, cy + 3)])

        elif self.p_type == "CRUMBLE":
            color = (130, 90, 50) if self.crumble_active else COLOR_PLAT_CRUMBLE
            pygame.draw.rect(surface, color, draw_rect, border_radius=4)
            # Crack lines
            pygame.draw.line(surface, (40, 30, 20), (draw_rect.x + 10, draw_rect.y + 2), (draw_rect.x + 25, draw_rect.y + 12), 2)
            pygame.draw.line(surface, (40, 30, 20), (draw_rect.right - 20, draw_rect.y + 3), (draw_rect.right - 35, draw_rect.y + 13), 2)

        elif self.p_type == "ICE":
            pygame.draw.rect(surface, (80, 150, 200), draw_rect, border_radius=4)
            pygame.draw.rect(surface, COLOR_PLAT_ICE, (draw_rect.x, draw_rect.y, draw_rect.width, 4), border_radius=2)
            # Gloss shine
            pygame.draw.line(surface, (255, 255, 255), (draw_rect.x + 8, draw_rect.y + 2), (draw_rect.right - 8, draw_rect.y + 2), 1)

        # Draw pickup if any
        if self.pickup and not self.pickup.collected:
            self.pickup.draw(surface)


class Ball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.rotation_angle = 0.0
        self.invulnerable_frames = 0
        self.on_platform = None
        self.on_ice = False

    def update(self, keys, current_scroll_speed):
        # Horizontal acceleration
        accel = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            accel -= BALL_ACCEL
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            accel += BALL_ACCEL

        self.vx += accel
        friction = BALL_ICE_FRICTION if self.on_ice else BALL_FRICTION
        self.vx *= friction

        # Speed clamp
        self.vx = max(-BALL_MAX_SPEED, min(BALL_MAX_SPEED, self.vx))

        # Rotate ball visually proportional to roll speed
        self.rotation_angle += self.vx * 0.15

        # Apply horizontal velocity
        self.x += self.vx

        # Screen boundaries
        if self.x - BALL_RADIUS < 15:
            self.x = 15 + BALL_RADIUS
            self.vx = 0
        elif self.x + BALL_RADIUS > SCREEN_WIDTH - 15:
            self.x = SCREEN_WIDTH - 15 - BALL_RADIUS
            self.vx = 0

        # Vertical physics
        if self.on_platform and not self.on_platform.crumble_destroyed:
            # Riding platform
            self.vy = -current_scroll_speed
            self.y = self.on_platform.rect.top - BALL_RADIUS

            # Check if walked off platform horizontally
            if self.x < self.on_platform.rect.left - BALL_RADIUS or self.x > self.on_platform.rect.right + BALL_RADIUS:
                self.on_platform = None
                self.on_ice = False
                self.vy = 0.0
        else:
            self.on_platform = None
            self.on_ice = False
            self.vy += GRAVITY
            self.vy = min(MAX_FALL_SPEED, self.vy)
            self.y += self.vy

        if self.invulnerable_frames > 0:
            self.invulnerable_frames -= 1

    def draw(self, surface):
        # Blinking during invulnerability
        if self.invulnerable_frames > 0 and (self.invulnerable_frames // 4) % 2 == 0:
            return

        cx = int(self.x)
        cy = int(self.y)

        # Base sphere
        pygame.draw.circle(surface, COLOR_BALL, (cx, cy), BALL_RADIUS)

        # Rolling stripe / equator
        cos_a = math.cos(self.rotation_angle)
        sin_a = math.sin(self.rotation_angle)
        sx = cx + int(BALL_RADIUS * 0.7 * cos_a)
        sy = cy + int(BALL_RADIUS * 0.7 * sin_a)
        pygame.draw.circle(surface, COLOR_BALL_STRIPE, (sx, sy), 4)

        # Specular shine
        pygame.draw.circle(surface, COLOR_BALL_HIGHLIGHT, (cx - 4, cy - 4), 3)


def draw_top_spikes(surface):
    spike_w = 12
    num_spikes = SCREEN_WIDTH // spike_w + 1
    for i in range(num_spikes):
        x = i * spike_w
        pts = [(x, 0), (x + spike_w // 2, TOP_SPIKES_HEIGHT), (x + spike_w, 0)]
        pygame.draw.polygon(surface, COLOR_TOP_SPIKES, pts)
        pygame.draw.polygon(surface, (255, 120, 120), [(x + 2, 0), (x + spike_w // 2, TOP_SPIKES_HEIGHT - 4), (x + spike_w - 2, 0)])


def generate_platform(y_pos, force_normal=False):
    width = random.randint(PLATFORM_WIDTH_MIN, PLATFORM_WIDTH_MAX)
    x = random.randint(25, SCREEN_WIDTH - width - 25)

    if force_normal:
        p_type = "NORMAL"
    else:
        # Weighted platform type selection
        weights = [
            ("NORMAL", 0.40),
            ("SPIKE", 0.18),
            ("SPRING", 0.14),
            ("MOVING", 0.12),
            ("CRUMBLE", 0.08),
            ("ICE", 0.08),
        ]
        r = random.random()
        cumulative = 0.0
        p_type = "NORMAL"
        for pt, w in weights:
            cumulative += w
            if r <= cumulative:
                p_type = pt
                break

    return Platform(x, y_pos, width, p_type)


def run_rapid_roll():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Rapid Roll Arcade")
    clock = pygame.time.Clock()

    hs_file = os.path.join(os.path.dirname(__file__), "highscore.json")
    high_score = common_ui.load_high_score(hs_file, 500) if common_ui else 500

    def init_game():
        ball = Ball(SCREEN_WIDTH // 2, 280)
        platforms = []
        # Initial safe starting platform directly under ball
        platforms.append(Platform(SCREEN_WIDTH // 2 - 50, 320, 100, "NORMAL"))

        # Spawn initial ladder of platforms
        cur_y = 320 + PLATFORM_SPACING
        while cur_y < SCREEN_HEIGHT + 100:
            platforms.append(generate_platform(cur_y))
            cur_y += PLATFORM_SPACING

        return ball, platforms

    ball, platforms = init_game()
    score = 0
    distance_traveled = 0.0
    lives = 3
    scroll_speed = BASE_SCROLL_SPEED
    screen_shake = 0
    particles = []
    popups = []

    state = "TITLE"  # TITLE, PLAYING, PAUSED, GAME_OVER
    running = True

    while running:
        clock.tick(FPS)

        # ================= EVENT HANDLING =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_p and state in ["PLAYING", "PAUSED"]:
                    state = "PAUSED" if state == "PLAYING" else "PLAYING"

                elif state == "TITLE":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP, pygame.K_w]:
                        state = "PLAYING"

                elif state == "GAME_OVER":
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r]:
                        ball, platforms = init_game()
                        score = 0
                        distance_traveled = 0.0
                        lives = 3
                        scroll_speed = BASE_SCROLL_SPEED
                        state = "PLAYING"

        keys = pygame.key.get_pressed()

        # ================= GAME UPDATE =================
        if state == "PLAYING":
            # Progressive difficulty curve
            scroll_speed = min(4.8, BASE_SCROLL_SPEED + (score // 300) * 0.25)
            distance_traveled += scroll_speed
            score = int(distance_traveled / 5)

            if score > high_score:
                high_score = score
                if common_ui:
                    common_ui.save_high_score(hs_file, high_score)

            # Update Ball
            ball.update(keys, scroll_speed)

            # Platform movement and generation
            for plat in platforms:
                plat.update(scroll_speed)

            # Clean platforms that scrolled off the top
            platforms = [p for p in platforms if p.rect.bottom > 0]

            # Generate new platforms at bottom
            if platforms:
                lowest_y = max(p.rect.y for p in platforms)
                if lowest_y < SCREEN_HEIGHT + 30:
                    new_plat = generate_platform(lowest_y + PLATFORM_SPACING)
                    platforms.append(new_plat)

            # Ball vs Platform collision
            for plat in platforms:
                if plat.crumble_destroyed:
                    continue

                # Check landing on platform
                prev_bottom = ball.y - ball.vy + BALL_RADIUS
                curr_bottom = ball.y + BALL_RADIUS

                if ball.vy >= 0 and prev_bottom <= plat.rect.top + 6 and curr_bottom >= plat.rect.top:
                    if plat.rect.left - BALL_RADIUS <= ball.x <= plat.rect.right + BALL_RADIUS:
                        # Landed!
                        ball.on_platform = plat
                        ball.y = plat.rect.top - BALL_RADIUS
                        ball.vy = 0

                        if not plat.landed:
                            plat.landed = True
                            distance_traveled += 20  # Bonus points for landing
                            # Dust particles
                            for _ in range(5):
                                particles.append(Particle(ball.x, plat.rect.top, (180, 200, 240), size_range=(1.5, 3)))

                        # Platform-specific effects
                        if plat.p_type == "SPIKE":
                            if ball.invulnerable_frames <= 0:
                                lives -= 1
                                ball.invulnerable_frames = 60
                                ball.vy = -6.0  # Hurt bounce
                                screen_shake = 12
                                popups.append(FloatingPopup("-1 LIFE", ball.x, ball.y, color=(255, 60, 60)))
                                for _ in range(12):
                                    particles.append(Particle(ball.x, ball.y, (255, 80, 80), speed_range=(2, 6)))
                                if lives <= 0:
                                    state = "GAME_OVER"

                        elif plat.p_type == "SPRING":
                            ball.on_platform = None
                            ball.vy = -12.0  # High launch!
                            popups.append(FloatingPopup("BOING!", ball.x, ball.y - 10, color=(255, 220, 50)))
                            for _ in range(8):
                                particles.append(Particle(ball.x, plat.rect.top, COLOR_PLAT_SPRING))

                        elif plat.p_type == "CRUMBLE":
                            plat.crumble_active = True

                        elif plat.p_type == "ICE":
                            ball.on_ice = True

                # Check Pickup collection
                if plat.pickup and not plat.pickup.collected:
                    dist = math.hypot(ball.x - plat.pickup.x, ball.y - plat.pickup.y)
                    if dist < BALL_RADIUS + 10:
                        plat.pickup.collected = True
                        if plat.pickup.item_type == "HEART":
                            lives = min(5, lives + 1)
                            popups.append(FloatingPopup("+1 LIFE", plat.pickup.x, plat.pickup.y, (255, 80, 120)))
                            for _ in range(10):
                                particles.append(Particle(plat.pickup.x, plat.pickup.y, (255, 80, 120)))
                        else:  # GEM
                            distance_traveled += 250  # +50 points
                            popups.append(FloatingPopup("+50 PTS", plat.pickup.x, plat.pickup.y, (255, 215, 0)))
                            for _ in range(10):
                                particles.append(Particle(plat.pickup.x, plat.pickup.y, (255, 215, 0)))

            # Ceiling Spikes Hazard Collision
            if ball.y - BALL_RADIUS <= TOP_SPIKES_HEIGHT:
                if ball.invulnerable_frames <= 0:
                    lives -= 1
                    ball.invulnerable_frames = 60
                    ball.vy = 4.0
                    ball.y = TOP_SPIKES_HEIGHT + BALL_RADIUS + 2
                    screen_shake = 14
                    popups.append(FloatingPopup("-1 LIFE", ball.x, ball.y, (255, 50, 50)))
                    for _ in range(15):
                        particles.append(Particle(ball.x, TOP_SPIKES_HEIGHT, (255, 80, 50), speed_range=(3, 7)))
                    if lives <= 0:
                        state = "GAME_OVER"

            # Pit Hazard (Fell off bottom)
            if ball.y - BALL_RADIUS > SCREEN_HEIGHT:
                lives -= 1
                screen_shake = 10
                if lives <= 0:
                    state = "GAME_OVER"
                else:
                    # Respawn on the highest safe platform visible
                    safe_plats = [p for p in platforms if p.p_type not in ["SPIKE", "CRUMBLE"] and p.rect.top > TOP_SPIKES_HEIGHT + 60 and p.rect.bottom < SCREEN_HEIGHT - 60]
                    if safe_plats:
                        target_plat = min(safe_plats, key=lambda p: p.rect.y)
                        ball.x = target_plat.rect.centerx
                        ball.y = target_plat.rect.top - BALL_RADIUS - 10
                    else:
                        ball.x = SCREEN_WIDTH // 2
                        ball.y = SCREEN_HEIGHT // 2
                    ball.vy = 0
                    ball.vx = 0
                    ball.invulnerable_frames = 90
                    popups.append(FloatingPopup("RESPAWN", ball.x, ball.y, (0, 230, 255)))

        # Update particles and popups
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        for pop in popups[:]:
            pop.update()
            if pop.life <= 0:
                popups.remove(pop)

        # ================= DRAWING =================
        render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_surf.fill(COLOR_BG)

        # Background vertical grid lines
        for gx in range(0, SCREEN_WIDTH, 40):
            pygame.draw.line(render_surf, COLOR_BG_GRID, (gx, 0), (gx, SCREEN_HEIGHT), 1)

        # Side walls
        pygame.draw.rect(render_surf, (28, 32, 52), (0, 0, 12, SCREEN_HEIGHT))
        pygame.draw.rect(render_surf, (28, 32, 52), (SCREEN_WIDTH - 12, 0, 12, SCREEN_HEIGHT))

        # Platforms
        for plat in platforms:
            plat.draw(render_surf)

        # Particles & Popups
        for p in particles:
            p.draw(render_surf)

        # Ball
        ball.draw(render_surf)

        for pop in popups:
            pop.draw(render_surf)

        # Top Ceiling Spikes
        draw_top_spikes(render_surf)

        # Top HUD Bar
        hud_bg = pygame.Surface((SCREEN_WIDTH, 34), pygame.SRCALPHA)
        hud_bg.fill((10, 12, 22, 210))
        render_surf.blit(hud_bg, (0, 0))

        # Lives (Hearts)
        for i in range(lives):
            hx = 24 + i * 18
            hy = 17
            pygame.draw.circle(render_surf, (255, 50, 80), (hx - 3, hy - 2), 4)
            pygame.draw.circle(render_surf, (255, 50, 80), (hx + 3, hy - 2), 4)
            pygame.draw.polygon(render_surf, (255, 50, 80), [(hx - 7, hy - 1), (hx + 7, hy - 1), (hx, hy + 7)])

        # Score & High Score
        draw_hud_text(render_surf, f"SCORE: {score:05d}", SCREEN_WIDTH // 2, 8, size=18, color=(255, 255, 255), align="midtop")
        draw_hud_text(render_surf, f"HI: {high_score:05d}", SCREEN_WIDTH - 20, 8, size=18, color=(255, 215, 0), align="topright")

        # Overlays
        if state == "TITLE":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 24, 210))
            render_surf.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(40, SCREEN_HEIGHT // 2 - 170, SCREEN_WIDTH - 80, 340)
            if common_ui:
                common_ui.draw_panel(render_surf, panel_rect, border_color=(255, 70, 70), bg_color=(20, 15, 30, 240))

            draw_hud_text(render_surf, "RAPID ROLL", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 130,
                          size=42, color=(255, 60, 60), align="center")
            draw_hud_text(render_surf, "NOKIA ARCADE CLASSIC", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 85,
                          size=17, color=(0, 220, 255), align="center")

            draw_hud_text(render_surf, "Roll down safely! Avoid the top ceiling spikes", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35,
                          size=16, color=(220, 225, 240), align="center")
            draw_hud_text(render_surf, "and don't fall off the bottom abyss!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 12,
                          size=16, color=(220, 225, 240), align="center")

            draw_hud_text(render_surf, "Controls: [A/D] or [Left/Right] to Roll", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30,
                          size=17, color=(255, 215, 0), align="center")
            draw_hud_text(render_surf, "Press [P] to Pause", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 55,
                          size=16, color=(160, 180, 210), align="center")

            draw_hud_text(render_surf, "PRESS [SPACE] TO START", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110,
                          size=22, color=(0, 255, 180), align="center")

        elif state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            render_surf.blit(overlay, (0, 0))
            draw_hud_text(render_surf, "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                          size=40, color=(255, 255, 255), align="center")
            draw_hud_text(render_surf, "Press [P] to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25,
                          size=20, color=(0, 220, 255), align="center")

        elif state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 5, 20, 220))
            render_surf.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(40, SCREEN_HEIGHT // 2 - 140, SCREEN_WIDTH - 80, 280)
            if common_ui:
                common_ui.draw_panel(render_surf, panel_rect, border_color=(255, 60, 60), bg_color=(25, 10, 25, 230))

            draw_hud_text(render_surf, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100,
                          size=42, color=(255, 60, 60), align="center")
            draw_hud_text(render_surf, f"Final Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 45,
                          size=24, color=(255, 255, 255), align="center")
            draw_hud_text(render_surf, f"High Score: {high_score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10,
                          size=20, color=(255, 215, 0), align="center")
            draw_hud_text(render_surf, "Press [ENTER] to Roll Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40,
                          size=20, color=(0, 255, 180), align="center")
            draw_hud_text(render_surf, "Press [ESC] to Exit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75,
                          size=16, color=(160, 160, 160), align="center")

        # Screen shake application
        ox, oy = 0, 0
        if screen_shake > 0:
            ox = random.randint(-screen_shake, screen_shake)
            oy = random.randint(-screen_shake, screen_shake)
            screen_shake -= 1

        screen.fill((0, 0, 0))
        screen.blit(render_surf, (ox, oy))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_rapid_roll()
