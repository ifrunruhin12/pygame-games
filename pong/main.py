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
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 600
FPS = 60

HEADER_HEIGHT = 65
PLAYFIELD_TOP = HEADER_HEIGHT
PLAYFIELD_BOTTOM = SCREEN_HEIGHT - 15

# Paddle Settings
PADDLE_WIDTH = 16
PADDLE_HEIGHT = 92
PADDLE_SPEED = 8.5
PADDLE_INSET = 40

# Ball Settings
BALL_SIZE = 14
BALL_INITIAL_SPEED = 7.0
BALL_SPEED_RAMP = 1.045
BALL_MAX_SPEED = 16.5

WINNING_SCORE = 7

# Colors
COLOR_BG = (12, 14, 24)
COLOR_NET = (40, 50, 80)
COLOR_PADDLE_P1 = (0, 220, 255)
COLOR_PADDLE_P2 = (255, 80, 100)
COLOR_BALL = (255, 255, 255)
COLOR_BALL_GLOW = (180, 225, 255)
COLOR_TEXT = (255, 255, 255)


def draw_hud_text(surface, text, x, y, size=22, color=COLOR_TEXT, align="topleft"):
    if common_ui:
        return common_ui.draw_text(surface, str(text), x, y, size=size, color=color, align=align)
    try:
        font = pygame.font.Font(None, size)
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        setattr(rect, align, (x, y))
        surface.blit(surf, rect)
        return rect
    except Exception:
        return pygame.Rect(x, y, len(str(text)) * 10, size)


class Particle:
    def __init__(self, x, y, color, speed_range=(2.0, 5.5)):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(*speed_range)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(14, 26)
        self.max_life = self.life
        self.size = random.uniform(2.0, 4.0)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            sz = max(1, int(self.size * (self.life / self.max_life)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), sz)


class Paddle:
    def __init__(self, x, is_ai=False, color=COLOR_PADDLE_P1):
        self.x = x
        self.y = (PLAYFIELD_TOP + PLAYFIELD_BOTTOM) // 2 - PADDLE_HEIGHT // 2
        self.color = color
        self.is_ai = is_ai
        self.vy = 0.0
        self.prev_y = self.y
        self.ai_target_offset = 0.0
        self.ai_timer = 0

    @property
    def rect(self):
        return pygame.Rect(self.x, int(self.y), PADDLE_WIDTH, PADDLE_HEIGHT)

    def move(self, dy):
        self.y += dy
        self.clamp()

    def clamp(self):
        if self.y < PLAYFIELD_TOP + 5:
            self.y = PLAYFIELD_TOP + 5
        elif self.y + PADDLE_HEIGHT > PLAYFIELD_BOTTOM - 5:
            self.y = PLAYFIELD_BOTTOM - 5 - PADDLE_HEIGHT

    def update_velocity(self):
        self.vy = self.y - self.prev_y
        self.prev_y = self.y

    def update_ai(self, ball):
        self.ai_timer += 1
        # Periodically adjust human-like offset
        if self.ai_timer % 30 == 0:
            self.ai_target_offset = random.uniform(-PADDLE_HEIGHT * 0.35, PADDLE_HEIGHT * 0.35)

        paddle_center = self.y + PADDLE_HEIGHT / 2
        # Only track if ball is moving toward AI's half
        if ball.vx > 0:
            target_y = ball.y + self.ai_target_offset
            diff = target_y - paddle_center
            if abs(diff) > 8:
                ai_speed = min(PADDLE_SPEED * 0.88, abs(diff) * 0.25)
                dy = ai_speed if diff > 0 else -ai_speed
                self.move(dy)
        else:
            # Idle return toward playfield center
            playfield_center = (PLAYFIELD_TOP + PLAYFIELD_BOTTOM) / 2
            diff = playfield_center - paddle_center
            if abs(diff) > 15:
                dy = (PADDLE_SPEED * 0.4) if diff > 0 else -(PADDLE_SPEED * 0.4)
                self.move(dy)

    def draw(self, surface):
        r = self.rect
        # Outer paddle body
        pygame.draw.rect(surface, self.color, r, border_radius=5)
        # Inner sleek accent
        inner_rect = pygame.Rect(r.x + 3, r.y + 4, r.width - 6, r.height - 8)
        pygame.draw.rect(surface, (255, 255, 255), inner_rect, border_radius=3)


class Ball:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = (PLAYFIELD_TOP + PLAYFIELD_BOTTOM) / 2
        self.vx = 0.0
        self.vy = 0.0
        self.speed = BALL_INITIAL_SPEED
        self.trail = []
        self.rally_count = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x - BALL_SIZE / 2), int(self.y - BALL_SIZE / 2), BALL_SIZE, BALL_SIZE)

    def serve(self, to_player):
        self.x = SCREEN_WIDTH / 2
        self.y = random.uniform(PLAYFIELD_TOP + 60, PLAYFIELD_BOTTOM - 60)
        self.speed = BALL_INITIAL_SPEED
        self.trail.clear()
        self.rally_count = 0

        # Angle between -30 and +30 degrees
        angle = random.uniform(-math.pi / 6, math.pi / 6)
        direction = 1 if to_player == 2 else -1
        self.vx = direction * self.speed * math.cos(angle)
        self.vy = self.speed * math.sin(angle)

    def update(self):
        # Update trail
        self.trail.append((self.x, self.y))
        max_trail = min(14, int(4 + (self.speed - BALL_INITIAL_SPEED) * 1.2))
        if len(self.trail) > max_trail:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        # Draw motion trail
        for i, (tx, ty) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            tr = max(2, int((BALL_SIZE / 2) * alpha * 0.8))
            speed_ratio = min(1.0, (self.speed - BALL_INITIAL_SPEED) / 8.0)
            trail_col = (
                int(100 + 155 * speed_ratio),
                int(200 - 80 * speed_ratio),
                int(255 - 150 * speed_ratio),
            )
            pygame.draw.circle(surface, trail_col, (int(tx), int(ty)), tr)

        # Draw main ball
        bx = int(self.x)
        by = int(self.y)
        pygame.draw.circle(surface, COLOR_BALL, (bx, by), BALL_SIZE // 2)
        pygame.draw.circle(surface, COLOR_BALL_GLOW, (bx, by), BALL_SIZE // 2 - 2)


def run_pong():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pong Arcade")
    clock = pygame.time.Clock()

    hs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")
    longest_rally_record = common_ui.load_high_score(hs_file, 10) if common_ui else 10

    # Game Setup
    mode = "1P"  # "1P" (vs AI) or "2P" (Local PvP)
    p1 = Paddle(PADDLE_INSET, is_ai=False, color=COLOR_PADDLE_P1)
    p2 = Paddle(SCREEN_WIDTH - PADDLE_INSET - PADDLE_WIDTH, is_ai=(mode == "1P"), color=COLOR_PADDLE_P2)
    ball = Ball()

    score_p1 = 0
    score_p2 = 0
    current_rally = 0
    match_longest_rally = 0

    state = "TITLE"  # TITLE, SERVE, PLAYING, PAUSED, MATCH_OVER
    serve_timer = 60
    server = 1
    winner = None

    particles = []
    screen_shake = 0

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
                    if event.key in [pygame.K_1, pygame.K_a]:
                        mode = "1P"
                        p2.is_ai = True
                    elif event.key in [pygame.K_2, pygame.K_m]:
                        mode = "2P"
                        p2.is_ai = False
                    elif event.key in [pygame.K_TAB, pygame.K_LEFT, pygame.K_RIGHT]:
                        mode = "2P" if mode == "1P" else "1P"
                        p2.is_ai = (mode == "1P")
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        score_p1 = 0
                        score_p2 = 0
                        current_rally = 0
                        match_longest_rally = 0
                        p2.is_ai = (mode == "1P")
                        server = random.choice([1, 2])
                        ball.serve(server)
                        state = "SERVE"
                        serve_timer = 50

                elif state == "MATCH_OVER":
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r]:
                        score_p1 = 0
                        score_p2 = 0
                        current_rally = 0
                        match_longest_rally = 0
                        server = random.choice([1, 2])
                        ball.serve(server)
                        state = "SERVE"
                        serve_timer = 50

        # ================= INPUT PROCESSING =================
        keys = pygame.key.get_pressed()

        # Player 1 controls (W / S)
        if state in ["SERVE", "PLAYING"]:
            if keys[pygame.K_w]:
                p1.move(-PADDLE_SPEED)
            if keys[pygame.K_s]:
                p1.move(PADDLE_SPEED)

            # Player 2 controls (UP / DOWN) if 2P mode
            if not p2.is_ai:
                if keys[pygame.K_UP]:
                    p2.move(-PADDLE_SPEED)
                if keys[pygame.K_DOWN]:
                    p2.move(PADDLE_SPEED)

        p1.update_velocity()
        p2.update_velocity()

        # ================= GAME LOGIC =================
        if state == "SERVE":
            serve_timer -= 1
            if serve_timer <= 0:
                state = "PLAYING"

        elif state == "PLAYING":
            # AI tracking if in 1P mode
            if p2.is_ai:
                p2.update_ai(ball)

            # Move ball
            ball.update()

            # Top & Bottom wall bounce
            if ball.y - BALL_SIZE / 2 <= PLAYFIELD_TOP:
                ball.y = PLAYFIELD_TOP + BALL_SIZE / 2
                ball.vy = abs(ball.vy)
                for _ in range(6):
                    particles.append(Particle(ball.x, PLAYFIELD_TOP, (180, 200, 240)))
            elif ball.y + BALL_SIZE / 2 >= PLAYFIELD_BOTTOM:
                ball.y = PLAYFIELD_BOTTOM - BALL_SIZE / 2
                ball.vy = -abs(ball.vy)
                for _ in range(6):
                    particles.append(Particle(ball.x, PLAYFIELD_BOTTOM, (180, 200, 240)))

            ball_r = ball.rect

            # Left Paddle (P1) Collision
            if ball.vx < 0 and ball_r.colliderect(p1.rect):
                ball.x = p1.rect.right + BALL_SIZE / 2
                # Calculate angle deflection
                offset = (ball.y - (p1.y + PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2)
                offset = max(-0.92, min(0.92, offset))
                deflect_angle = offset * (math.pi / 3)  # Max 60 deg

                ball.speed = min(BALL_MAX_SPEED, ball.speed * BALL_SPEED_RAMP)
                ball.vx = ball.speed * math.cos(deflect_angle)
                ball.vy = ball.speed * math.sin(deflect_angle) + (p1.vy * 0.25)

                current_rally += 1
                match_longest_rally = max(match_longest_rally, current_rally)
                if match_longest_rally > longest_rally_record:
                    longest_rally_record = match_longest_rally
                    if common_ui:
                        common_ui.save_high_score(hs_file, longest_rally_record)

                # Impact sparks
                for _ in range(10):
                    particles.append(Particle(p1.rect.right, ball.y, COLOR_PADDLE_P1))

            # Right Paddle (P2 / AI) Collision
            elif ball.vx > 0 and ball_r.colliderect(p2.rect):
                ball.x = p2.rect.left - BALL_SIZE / 2
                offset = (ball.y - (p2.y + PADDLE_HEIGHT / 2)) / (PADDLE_HEIGHT / 2)
                offset = max(-0.92, min(0.92, offset))
                deflect_angle = offset * (math.pi / 3)

                ball.speed = min(BALL_MAX_SPEED, ball.speed * BALL_SPEED_RAMP)
                ball.vx = -ball.speed * math.cos(deflect_angle)
                ball.vy = ball.speed * math.sin(deflect_angle) + (p2.vy * 0.25)

                current_rally += 1
                match_longest_rally = max(match_longest_rally, current_rally)
                if match_longest_rally > longest_rally_record:
                    longest_rally_record = match_longest_rally
                    if common_ui:
                        common_ui.save_high_score(hs_file, longest_rally_record)

                # Impact sparks
                for _ in range(10):
                    particles.append(Particle(p2.rect.left, ball.y, COLOR_PADDLE_P2))

            # Goal scored by P1 (ball crossed right edge)
            if ball.x > SCREEN_WIDTH + 20:
                score_p1 += 1
                current_rally = 0
                screen_shake = 10
                for _ in range(25):
                    particles.append(Particle(SCREEN_WIDTH - 20, ball.y, COLOR_PADDLE_P1, speed_range=(3, 7)))

                if score_p1 >= WINNING_SCORE:
                    winner = "PLAYER 1"
                    state = "MATCH_OVER"
                else:
                    server = 2
                    ball.serve(server)
                    state = "SERVE"
                    serve_timer = 50

            # Goal scored by P2 / AI (ball crossed left edge)
            elif ball.x < -20:
                score_p2 += 1
                current_rally = 0
                screen_shake = 10
                for _ in range(25):
                    particles.append(Particle(20, ball.y, COLOR_PADDLE_P2, speed_range=(3, 7)))

                if score_p2 >= WINNING_SCORE:
                    winner = "PLAYER 2" if mode == "2P" else "AI"
                    state = "MATCH_OVER"
                else:
                    server = 1
                    ball.serve(server)
                    state = "SERVE"
                    serve_timer = 50

        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ================= DRAWING =================
        render_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        render_surf.fill(COLOR_BG)

        # Top border line
        pygame.draw.line(render_surf, (35, 42, 68), (0, PLAYFIELD_TOP), (SCREEN_WIDTH, PLAYFIELD_TOP), 2)
        # Bottom border line
        pygame.draw.line(render_surf, (35, 42, 68), (0, PLAYFIELD_BOTTOM), (SCREEN_WIDTH, PLAYFIELD_BOTTOM), 2)

        # Center dashed dividing net
        net_x = SCREEN_WIDTH // 2
        for ny in range(PLAYFIELD_TOP + 10, PLAYFIELD_BOTTOM, 26):
            pygame.draw.rect(render_surf, COLOR_NET, (net_x - 2, ny, 4, 16), border_radius=2)

        # Draw Scoreboard in Header
        draw_hud_text(render_surf, f"{score_p1}", SCREEN_WIDTH // 2 - 70, 16, size=46, color=COLOR_PADDLE_P1, align="topright")
        draw_hud_text(render_surf, f"{score_p2}", SCREEN_WIDTH // 2 + 70, 16, size=46, color=COLOR_PADDLE_P2, align="topleft")
        draw_hud_text(render_surf, ":", SCREEN_WIDTH // 2, 16, size=42, color=(120, 140, 180), align="midtop")

        # Top corner labels
        p1_label = "PLAYER 1"
        p2_label = "PLAYER 2" if mode == "2P" else "COMPUTER"
        draw_hud_text(render_surf, p1_label, 50, 22, size=18, color=COLOR_PADDLE_P1)
        draw_hud_text(render_surf, p2_label, SCREEN_WIDTH - 50, 22, size=18, color=COLOR_PADDLE_P2, align="topright")

        # Rally & record display
        rally_label = f"RALLY: {current_rally} (RECORD: {longest_rally_record})"
        draw_hud_text(render_surf, rally_label, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 12, size=16, color=(140, 160, 200), align="midbottom")

        # Draw Paddles
        p1.draw(render_surf)
        p2.draw(render_surf)

        # Draw Ball
        ball.draw(render_surf)

        # Draw Particles
        for p in particles:
            p.draw(render_surf)

        # State Overlays
        if state == "TITLE":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 24, 220))
            render_surf.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 2 - 180, 500, 360)
            if common_ui:
                common_ui.draw_panel(render_surf, panel_rect, border_color=(0, 220, 255), bg_color=(20, 24, 40, 240))

            draw_hud_text(render_surf, "PONG ARCADE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140, size=46, color=(0, 220, 255), align="center")
            draw_hud_text(render_surf, "CLASSIC TABLE TENNIS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 95, size=18, color=(255, 215, 0), align="center")

            # Mode selector buttons
            draw_hud_text(render_surf, "SELECT GAME MODE:", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 55, size=20, color=(220, 230, 250), align="center")

            p1_active_col = (0, 255, 180) if mode == "1P" else (140, 150, 170)
            p2_active_col = (0, 255, 180) if mode == "2P" else (140, 150, 170)
            draw_hud_text(render_surf, f"[{'X' if mode == '1P' else ' '}] 1-PLAYER (vs Computer)", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, size=22, color=p1_active_col, align="center")
            draw_hud_text(render_surf, f"[{'X' if mode == '2P' else ' '}] 2-PLAYER (Local PvP)", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10, size=22, color=p2_active_col, align="center")

            draw_hud_text(render_surf, "Press [1] or [2] (or TAB) to change mode", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45, size=16, color=(160, 180, 210), align="center")

            # Controls
            draw_hud_text(render_surf, "Controls: P1 [W/S] | P2 [Up/Down] | Pause [P]", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, size=17, color=(255, 255, 255), align="center")

            draw_hud_text(render_surf, "PRESS [SPACE] TO SERVE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130, size=24, color=(0, 255, 180), align="center")

        elif state == "SERVE":
            draw_hud_text(render_surf, "READY...", SCREEN_WIDTH // 2, (PLAYFIELD_TOP + PLAYFIELD_BOTTOM) // 2 - 40, size=32, color=(255, 255, 0), align="center")

        elif state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            render_surf.blit(overlay, (0, 0))
            draw_hud_text(render_surf, "GAME PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20, size=40, color=(255, 255, 255), align="center")
            draw_hud_text(render_surf, "Press [P] to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25, size=22, color=(0, 220, 255), align="center")

        elif state == "MATCH_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 12, 24, 220))
            render_surf.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 230, SCREEN_HEIGHT // 2 - 140, 460, 280)
            win_color = COLOR_PADDLE_P1 if winner == "PLAYER 1" else COLOR_PADDLE_P2
            if common_ui:
                common_ui.draw_panel(render_surf, panel_rect, border_color=win_color, bg_color=(20, 24, 40, 240))

            draw_hud_text(render_surf, f"{winner} WINS!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 95, size=44, color=win_color, align="center")
            draw_hud_text(render_surf, f"Final Score: {score_p1} - {score_p2}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40, size=26, color=(255, 255, 255), align="center")
            draw_hud_text(render_surf, f"Longest Rally: {match_longest_rally} hits", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 5, size=20, color=(255, 215, 0), align="center")
            draw_hud_text(render_surf, "Press [ENTER] to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, size=22, color=(0, 255, 180), align="center")
            draw_hud_text(render_surf, "Press [ESC] to Exit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 82, size=16, color=(160, 160, 160), align="center")

        # Apply screen shake
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
    run_pong()
