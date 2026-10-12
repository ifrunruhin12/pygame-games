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
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 640
HEADER_HEIGHT = 60
GRID_HEIGHT = SCREEN_HEIGHT - HEADER_HEIGHT
CELL_SIZE = 20

COLS = SCREEN_WIDTH // CELL_SIZE
ROWS = GRID_HEIGHT // CELL_SIZE

BASE_FPS = 10

# Colors
COLOR_BG = (14, 18, 28)
COLOR_GRID = (20, 26, 40)
COLOR_SNAKE_HEAD = (46, 204, 113)
COLOR_SNAKE_BODY = (39, 174, 96)
COLOR_FOOD = (231, 76, 60)
COLOR_FOOD_LEAF = (46, 204, 113)

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


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
        speed = random.uniform(1.5, 4.5)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.randint(15, 25)
        self.max_life = self.life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            sz = max(1, int(3 * (self.life / self.max_life)))
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), sz)


def spawn_food(snake):
    while True:
        gx = random.randint(0, COLS - 1)
        gy = random.randint(0, ROWS - 1)
        food_pos = (gx, gy)
        if food_pos not in snake:
            return food_pos


def draw_snake_head(surface, gx, gy, direction):
    px = gx * CELL_SIZE
    py = gy * CELL_SIZE + HEADER_HEIGHT

    # Base head
    head_rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(surface, COLOR_SNAKE_HEAD, head_rect, border_radius=6)

    # Eyes based on direction
    cx = px + CELL_SIZE // 2
    cy = py + CELL_SIZE // 2

    eye_offsets = []
    if direction == RIGHT:
        eye_offsets = [(cx + 4, cy - 4), (cx + 4, cy + 4)]
        pupil_ox, pupil_oy = 1, 0
    elif direction == LEFT:
        eye_offsets = [(cx - 4, cy - 4), (cx - 4, cy + 4)]
        pupil_ox, pupil_oy = -1, 0
    elif direction == UP:
        eye_offsets = [(cx - 4, cy - 4), (cx + 4, cy - 4)]
        pupil_ox, pupil_oy = 0, -1
    else:  # DOWN
        eye_offsets = [(cx - 4, cy + 4), (cx + 4, cy + 4)]
        pupil_ox, pupil_oy = 0, 1

    for ex, ey in eye_offsets:
        pygame.draw.circle(surface, (255, 255, 255), (ex, ey), 3)
        pygame.draw.circle(surface, (10, 10, 20), (ex + pupil_ox, ey + pupil_oy), 1)


def draw_apple(surface, gx, gy, pulse_timer):
    cx = gx * CELL_SIZE + CELL_SIZE // 2
    cy = gy * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2

    # Pulsing glow
    pulse = math.sin(pulse_timer * 6) * 1.5
    r = int(CELL_SIZE // 2 - 2 + pulse)

    # Apple body
    pygame.draw.circle(surface, COLOR_FOOD, (cx, cy), r)
    pygame.draw.circle(surface, (255, 140, 130), (cx - 2, cy - 2), max(1, r // 3))

    # Leaf
    pygame.draw.ellipse(surface, COLOR_FOOD_LEAF, (cx, cy - r - 2, 4, 3))


def run_snake():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Retro Snake Arcade")
    clock = pygame.time.Clock()

    hs_file = os.path.join(os.path.dirname(__file__), "highscore.json")
    high_score = common_ui.load_high_score(hs_file, 10) if common_ui else 10

    def init_game():
        start_x = COLS // 2
        start_y = ROWS // 2
        s = [(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)]
        f = spawn_food(s)
        return s, f

    snake, food = init_game()
    direction = RIGHT
    next_direction = RIGHT
    score = 0
    particles = []
    pulse_timer = 0

    state = "START"  # START, PLAYING, PAUSED, GAME_OVER
    running = True

    while running:
        dt = clock.tick(BASE_FPS + min(8, score // 3)) / 1000.0
        pulse_timer += dt

        # ================= EVENTS =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_p and state in ["PLAYING", "PAUSED"]:
                    state = "PAUSED" if state == "PLAYING" else "PLAYING"

                elif state == "START":
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d]:
                        state = "PLAYING"
                        if event.key in [pygame.K_UP, pygame.K_w]:
                            next_direction = UP
                        elif event.key in [pygame.K_DOWN, pygame.K_s]:
                            next_direction = DOWN
                        elif event.key in [pygame.K_LEFT, pygame.K_a]:
                            next_direction = LEFT
                        elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                            next_direction = RIGHT

                elif state == "PLAYING":
                    if (event.key == pygame.K_UP or event.key == pygame.K_w) and direction != DOWN:
                        next_direction = UP
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and direction != UP:
                        next_direction = DOWN
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and direction != RIGHT:
                        next_direction = LEFT
                    elif (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and direction != LEFT:
                        next_direction = RIGHT

                elif state == "GAME_OVER":
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r]:
                        snake, food = init_game()
                        direction = RIGHT
                        next_direction = RIGHT
                        score = 0
                        state = "PLAYING"

        # ================= GAME UPDATE =================
        if state == "PLAYING":
            direction = next_direction

            head_x, head_y = snake[0]
            new_head = (head_x + direction[0], head_y + direction[1])

            # Wall collision
            if new_head[0] < 0 or new_head[0] >= COLS or new_head[1] < 0 or new_head[1] >= ROWS:
                state = "GAME_OVER"
                if score > high_score:
                    high_score = score
                    if common_ui:
                        common_ui.save_high_score(hs_file, high_score)

            # Self collision
            elif new_head in snake:
                state = "GAME_OVER"
                if score > high_score:
                    high_score = score
                    if common_ui:
                        common_ui.save_high_score(hs_file, high_score)

            else:
                snake.insert(0, new_head)

                # Food eaten
                if new_head == food:
                    score += 1
                    food_px = food[0] * CELL_SIZE + CELL_SIZE // 2
                    food_py = food[1] * CELL_SIZE + HEADER_HEIGHT + CELL_SIZE // 2
                    for _ in range(12):
                        particles.append(Particle(food_px, food_py, COLOR_FOOD))

                    food = spawn_food(snake)
                    if score > high_score:
                        high_score = score
                        if common_ui:
                            common_ui.save_high_score(hs_file, high_score)
                else:
                    snake.pop()

        # Update particles
        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        # ================= DRAWING =================
        screen.fill(COLOR_BG)

        # Draw grid lines in playfield
        for r in range(ROWS + 1):
            y = HEADER_HEIGHT + r * CELL_SIZE
            pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1)
        for c in range(COLS + 1):
            x = c * CELL_SIZE
            pygame.draw.line(screen, COLOR_GRID, (x, HEADER_HEIGHT), (x, SCREEN_HEIGHT), 1)

        # Top HUD Bar
        pygame.draw.rect(screen, (20, 25, 38), (0, 0, SCREEN_WIDTH, HEADER_HEIGHT))
        pygame.draw.line(screen, (40, 50, 75), (0, HEADER_HEIGHT), (SCREEN_WIDTH, HEADER_HEIGHT), 2)

        draw_hud_text(screen, "SCORE", 30, 10, size=16, color=(160, 180, 210))
        draw_hud_text(screen, f"{score:03d}", 30, 28, size=24, color=(255, 255, 255))

        draw_hud_text(screen, "HIGH SCORE", SCREEN_WIDTH // 2, 10, size=16, color=(255, 200, 50), align="midtop")
        draw_hud_text(screen, f"{high_score:03d}", SCREEN_WIDTH // 2, 28, size=24, color=(255, 255, 255), align="midtop")

        draw_hud_text(screen, f"LENGTH: {len(snake)}", SCREEN_WIDTH - 30, 20, size=20, color=(46, 204, 113), align="topright")

        # Draw Food
        draw_apple(screen, food[0], food[1], pulse_timer)

        # Draw Snake Body
        for i, segment in enumerate(snake[1:], start=1):
            px = segment[0] * CELL_SIZE
            py = segment[1] * CELL_SIZE + HEADER_HEIGHT
            # Color gradient down tail
            ratio = max(0.5, 1.0 - (i / len(snake)) * 0.4)
            seg_col = (int(COLOR_SNAKE_BODY[0] * ratio), int(COLOR_SNAKE_BODY[1] * ratio), int(COLOR_SNAKE_BODY[2] * ratio))
            pygame.draw.rect(screen, seg_col, (px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2), border_radius=4)

        # Draw Snake Head
        draw_snake_head(screen, snake[0][0], snake[0][1], direction)

        # Draw Particles
        for p in particles:
            p.draw(screen)

        # Overlays
        if state == "START":
            overlay = pygame.Surface((SCREEN_WIDTH, GRID_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 15, 25, 180))
            screen.blit(overlay, (0, HEADER_HEIGHT))

            draw_hud_text(screen, "RETRO SNAKE", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
                          size=42, color=(46, 204, 113), align="center")
            draw_hud_text(screen, "Press [SPACE] or [ARROW KEYS] to Start", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10,
                          size=22, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Use WASD or Arrow Keys to Turn | P to Pause", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45,
                          size=17, color=(160, 180, 200), align="center")

        elif state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_hud_text(screen, "GAME PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                          size=38, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Press [P] to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25,
                          size=22, color=(0, 220, 255), align="center")

        elif state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 5, 20, 220))
            screen.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 - 120, 360, 240)
            if common_ui:
                common_ui.draw_panel(screen, panel_rect, border_color=(255, 60, 60), bg_color=(25, 10, 25, 230))

            draw_hud_text(screen, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                          size=40, color=(255, 60, 60), align="center")
            draw_hud_text(screen, f"Apples Eaten: {score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30,
                          size=24, color=(255, 255, 255), align="center")
            draw_hud_text(screen, f"High Score: {high_score}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 5,
                          size=20, color=(255, 215, 0), align="center")
            draw_hud_text(screen, "Press [ENTER] to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          size=20, color=(0, 255, 180), align="center")
            draw_hud_text(screen, "Press [ESC] to Exit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                          size=16, color=(160, 160, 160), align="center")

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_snake()
