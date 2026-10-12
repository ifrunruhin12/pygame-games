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

# ================= SETTINGS =================
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Paddle
PADDLE_WIDTH = 130
PADDLE_HEIGHT = 18
PADDLE_SPEED = 9

# Ball
BALL_RADIUS = 10
BALL_INITIAL_SPEED = 7.5

# Bricks
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_PADDING = 8
BRICK_HEIGHT = 26
BRICK_OFFSET_TOP = 80
BRICK_WIDTH = (SCREEN_WIDTH - 80 - (BRICK_COLS - 1) * BRICK_PADDING) // BRICK_COLS
BRICK_OFFSET_LEFT = (SCREEN_WIDTH - (BRICK_COLS * BRICK_WIDTH + (BRICK_COLS - 1) * BRICK_PADDING)) // 2

# Row Colors (Retro Arcade Palette)
ROW_COLORS = [
    ((235, 60, 60), (255, 120, 120)),   # Red
    ((245, 135, 30), (255, 180, 80)),   # Orange
    ((245, 205, 35), (255, 235, 110)),  # Yellow
    ((45, 205, 95), (115, 240, 150)),   # Green
    ((35, 180, 245), (120, 225, 255)),  # Cyan
]

COLOR_BG = (12, 14, 24)
COLOR_PADDLE = (220, 235, 255)
COLOR_PADDLE_ACCENT = (0, 180, 255)
COLOR_BALL = (255, 255, 255)


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
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(18, 32)
        self.max_life = self.life
        self.size = random.uniform(2.5, 4.5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15  # subtle gravity
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            alpha_ratio = self.life / self.max_life
            sz = max(1, int(self.size * alpha_ratio))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), sz)


class Brick:
    def __init__(self, rect, base_color, highlight_color, points):
        self.rect = rect
        self.base_color = base_color
        self.highlight_color = highlight_color
        self.points = points

    def draw(self, surface):
        # Outer body
        pygame.draw.rect(surface, self.base_color, self.rect, border_radius=4)
        # Top-left highlight bevel
        hi_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width - 4, 3)
        pygame.draw.rect(surface, self.highlight_color, hi_rect, border_radius=2)
        # Dark subtle border
        pygame.draw.rect(surface, (10, 10, 20), self.rect, width=1, border_radius=4)


def create_brick_field():
    bricks = []
    for row in range(BRICK_ROWS):
        base_col, hi_col = ROW_COLORS[row % len(ROW_COLORS)]
        pts = (BRICK_ROWS - row) * 10
        for col in range(BRICK_COLS):
            bx = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
            by = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
            rect = pygame.Rect(bx, by, BRICK_WIDTH, BRICK_HEIGHT)
            bricks.append(Brick(rect, base_col, hi_col, pts))
    return bricks


def run_brick_breaker():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Brick Breaker Arcade")
    clock = pygame.time.Clock()

    hs_file = os.path.join(os.path.dirname(__file__), "highscore.json")
    high_score = common_ui.load_high_score(hs_file, 500) if common_ui else 500

    score = 0
    lives = 3
    level = 1

    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
    paddle_y = SCREEN_HEIGHT - 45

    ball_x = paddle_x + PADDLE_WIDTH // 2
    ball_y = paddle_y - BALL_RADIUS - 1
    ball_vx = 0
    ball_vy = 0
    ball_speed = BALL_INITIAL_SPEED

    bricks = create_brick_field()
    particles = []
    ball_trail = []

    state = "SERVE"  # SERVE, PLAYING, PAUSED, GAME_OVER, VICTORY
    running = True

    while running:
        clock.tick(FPS)

        # ================= EVENTS =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_p and state in ["PLAYING", "PAUSED"]:
                    state = "PAUSED" if state == "PLAYING" else "PLAYING"

                elif event.key in [pygame.K_SPACE, pygame.K_UP] and state == "SERVE":
                    # Launch ball with slight random angle
                    launch_angle = random.uniform(-0.4, 0.4)
                    ball_vx = ball_speed * math.sin(launch_angle)
                    ball_vy = -ball_speed * math.cos(launch_angle)
                    state = "PLAYING"

                elif event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r] and state in ["GAME_OVER", "VICTORY"]:
                    if state == "GAME_OVER":
                        score = 0
                        lives = 3
                        level = 1
                    else:
                        level += 1
                        ball_speed = min(11.0, BALL_INITIAL_SPEED + (level - 1) * 0.5)

                    bricks = create_brick_field()
                    paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
                    ball_x = paddle_x + PADDLE_WIDTH // 2
                    ball_y = paddle_y - BALL_RADIUS - 1
                    ball_vx = 0
                    ball_vy = 0
                    state = "SERVE"

        # ================= PADDLE INPUT =================
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            paddle_x -= PADDLE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            paddle_x += PADDLE_SPEED

        # Keep paddle in bounds
        if paddle_x < 20:
            paddle_x = 20
        elif paddle_x + PADDLE_WIDTH > SCREEN_WIDTH - 20:
            paddle_x = SCREEN_WIDTH - 20 - PADDLE_WIDTH

        paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)

        # ================= BALL & GAME LOGIC =================
        if state == "SERVE":
            ball_x = paddle_x + PADDLE_WIDTH // 2
            ball_y = paddle_y - BALL_RADIUS - 1
            ball_trail.clear()

        elif state == "PLAYING":
            # Add to trail
            ball_trail.append((ball_x, ball_y))
            if len(ball_trail) > 8:
                ball_trail.pop(0)

            # Move ball
            ball_x += ball_vx
            ball_y += ball_vy

            # Wall Collisions
            if ball_x - BALL_RADIUS <= 15:
                ball_x = 15 + BALL_RADIUS
                ball_vx = abs(ball_vx)
            elif ball_x + BALL_RADIUS >= SCREEN_WIDTH - 15:
                ball_x = SCREEN_WIDTH - 15 - BALL_RADIUS
                ball_vx = -abs(ball_vx)

            if ball_y - BALL_RADIUS <= 60:  # Top border below HUD
                ball_y = 60 + BALL_RADIUS
                ball_vy = abs(ball_vy)

            # Ball drops below screen (Life lost)
            if ball_y - BALL_RADIUS > SCREEN_HEIGHT:
                lives -= 1
                if lives <= 0:
                    state = "GAME_OVER"
                    if score > high_score:
                        high_score = score
                        if common_ui:
                            common_ui.save_high_score(hs_file, high_score)
                else:
                    state = "SERVE"
                    ball_trail.clear()

            # Paddle Collision
            ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
            if paddle_rect.colliderect(ball_rect) and ball_vy > 0:
                ball_y = paddle_y - BALL_RADIUS
                # Deflection angle based on impact distance from center
                hit_offset = (ball_x - (paddle_x + PADDLE_WIDTH / 2)) / (PADDLE_WIDTH / 2)
                hit_offset = max(-0.95, min(0.95, hit_offset))
                bounce_angle = hit_offset * (math.pi / 3)  # Max 60 deg deflection

                curr_speed = math.hypot(ball_vx, ball_vy)
                ball_vx = curr_speed * math.sin(bounce_angle)
                ball_vy = -curr_speed * math.cos(bounce_angle)

                # Emit paddle hit dust
                for _ in range(5):
                    particles.append(Particle(ball_x, paddle_y, (180, 220, 255)))

            # Brick Collision
            for brick in bricks:
                if brick.rect.colliderect(ball_rect):
                    # Collision side analysis
                    overlap_left = ball_rect.right - brick.rect.left
                    overlap_right = brick.rect.right - ball_rect.left
                    overlap_top = ball_rect.bottom - brick.rect.top
                    overlap_bottom = brick.rect.bottom - ball_rect.top

                    min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                    if min_overlap in [overlap_left, overlap_right]:
                        ball_vx = -ball_vx
                    else:
                        ball_vy = -ball_vy

                    # Break brick
                    score += brick.points
                    for _ in range(12):
                        particles.append(Particle(brick.rect.centerx, brick.rect.centery, brick.base_color))
                    bricks.remove(brick)

                    # Update high score
                    if score > high_score:
                        high_score = score
                        if common_ui:
                            common_ui.save_high_score(hs_file, high_score)

                    # Win check
                    if not bricks:
                        state = "VICTORY"
                        score += 500  # Round bonus
                        if score > high_score:
                            high_score = score
                            if common_ui:
                                common_ui.save_high_score(hs_file, high_score)
                    break

        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ================= DRAWING =================
        screen.fill(COLOR_BG)

        # Border walls
        pygame.draw.rect(screen, (30, 35, 60), (10, 55, SCREEN_WIDTH - 20, SCREEN_HEIGHT - 60), width=4, border_radius=6)

        # Top HUD Bar
        draw_hud_text(screen, "SCORE", 35, 12, size=18, color=(160, 180, 220))
        draw_hud_text(screen, f"{score:05d}", 35, 28, size=24, color=(255, 255, 255))

        draw_hud_text(screen, "HIGH SCORE", SCREEN_WIDTH // 2, 12, size=18, color=(255, 200, 50), align="midtop")
        draw_hud_text(screen, f"{high_score:05d}", SCREEN_WIDTH // 2, 28, size=24, color=(255, 255, 255), align="midtop")

        draw_hud_text(screen, f"LVL {level}", SCREEN_WIDTH - 160, 20, size=20, color=(50, 220, 120), align="midtop")

        # Lives Indicator (mini paddles)
        for i in range(lives):
            lx = SCREEN_WIDTH - 100 + i * 26
            ly = 26
            pygame.draw.rect(screen, COLOR_PADDLE_ACCENT, (lx, ly, 20, 6), border_radius=2)

        # Draw Bricks
        for b in bricks:
            b.draw(screen)

        # Draw Particles
        for p in particles:
            p.draw(screen)

        # Draw Ball Trail
        for i, (tx, ty) in enumerate(ball_trail):
            alpha = (i + 1) / len(ball_trail)
            tr = max(2, int(BALL_RADIUS * 0.6 * alpha))
            pygame.draw.circle(screen, (80, 160, 255), (int(tx), int(ty)), tr)

        # Draw Paddle
        pygame.draw.rect(screen, COLOR_PADDLE, paddle_rect, border_radius=6)
        # Paddle center highlight
        pygame.draw.rect(screen, COLOR_PADDLE_ACCENT,
                         (paddle_x + PADDLE_WIDTH // 2 - 12, paddle_y + 3, 24, PADDLE_HEIGHT - 6),
                         border_radius=3)

        # Draw Ball
        pygame.draw.circle(screen, COLOR_BALL, (int(ball_x), int(ball_y)), BALL_RADIUS)
        pygame.draw.circle(screen, (160, 220, 255), (int(ball_x - 3), int(ball_y - 3)), BALL_RADIUS // 3)

        # Overlays
        if state == "SERVE":
            draw_hud_text(screen, "PRESS [SPACE] TO LAUNCH BALL", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                          size=22, color=(0, 230, 255), align="center")
            draw_hud_text(screen, "Controls: [A/D] or [Left/Right] to Move Paddle",
                          SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 115,
                          size=17, color=(160, 175, 205), align="center")

        elif state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_hud_text(screen, "PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                          size=40, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Press [P] to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25,
                          size=22, color=(0, 220, 255), align="center")

        elif state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 5, 20, 220))
            screen.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 130, 400, 260)
            if common_ui:
                common_ui.draw_panel(screen, panel_rect, border_color=(255, 60, 60), bg_color=(25, 10, 25, 230))

            draw_hud_text(screen, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90,
                          size=44, color=(255, 60, 60), align="center")
            draw_hud_text(screen, f"Final Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35,
                          size=26, color=(255, 255, 255), align="center")
            draw_hud_text(screen, f"High Score: {high_score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                          size=22, color=(255, 215, 0), align="center")
            draw_hud_text(screen, "Press [ENTER] or [SPACE] to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          size=20, color=(0, 255, 180), align="center")
            draw_hud_text(screen, "Press [ESC] to Quit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                          size=17, color=(160, 160, 160), align="center")

        elif state == "VICTORY":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 210))
            screen.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 - 120, 400, 240)
            if common_ui:
                common_ui.draw_panel(screen, panel_rect, border_color=(0, 255, 150), bg_color=(10, 30, 20, 230))

            draw_hud_text(screen, "STAGE CLEARED!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                          size=38, color=(0, 255, 160), align="center")
            draw_hud_text(screen, "Bonus: +500 PTS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35,
                          size=24, color=(255, 255, 0), align="center")
            draw_hud_text(screen, f"Current Score: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                          size=22, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Press [ENTER] for Next Level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          size=20, color=(0, 230, 255), align="center")

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_brick_breaker()
