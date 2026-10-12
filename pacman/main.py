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

# ================= CONSTANTS & CONFIG =================
TILE_SIZE = 32

MAZE_LAYOUT = [
    "###################",
    "#........#........#",
    "#o##.###.#.###.##o#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.### # ###.####",
    "   #.#   B   #.#   ",
    "####.# ##-## #.####",
    "T   .  #IKC#  .   T",
    "####.# ##### #.####",
    "   #.#       #.#   ",
    "####.#.#####.#.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o.#.....P.....#.o#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]

COLS = len(MAZE_LAYOUT[0])
ROWS = len(MAZE_LAYOUT)
HEADER_HEIGHT = 48
FOOTER_HEIGHT = 40
SCREEN_WIDTH = COLS * TILE_SIZE
SCREEN_HEIGHT = ROWS * TILE_SIZE + HEADER_HEIGHT + FOOTER_HEIGHT

FPS = 60

# Colors
COLOR_BG = (10, 10, 18)
COLOR_WALL = (33, 33, 222)
COLOR_WALL_INNER = (0, 0, 130)
COLOR_GATE = (255, 184, 255)
COLOR_PELLET = (255, 183, 174)
COLOR_ENERGIZER = (255, 255, 255)
COLOR_PACMAN = (255, 255, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_FRIGHTENED = (36, 36, 255)
COLOR_FRIGHTENED_FLASH = (240, 240, 255)

# Directions
DIR_NONE = (0, 0)
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)
ALL_DIRECTIONS = [DIR_UP, DIR_LEFT, DIR_DOWN, DIR_RIGHT]


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


class Maze:
    def __init__(self, layout):
        self.grid = [list(row) for row in layout]
        self.pellet_count = 0
        for row in self.grid:
            for cell in row:
                if cell in [".", "o"]:
                    self.pellet_count += 1

    def is_walkable(self, gx, gy, can_cross_gate=False):
        # Tunnel row wrap-around
        if gy == 10 and (gx < 0 or gx >= COLS):
            return True
        if gx < 0 or gx >= COLS or gy < 0 or gy >= ROWS:
            return False
        tile = self.grid[gy][gx]
        if tile == "#":
            return False
        if tile == "-":
            return can_cross_gate
        return True

    def draw(self, surface, offset_y, pulse_timer):
        for r, row in enumerate(self.grid):
            for c, cell in enumerate(row):
                x = c * TILE_SIZE
                y = r * TILE_SIZE + offset_y

                if cell == "#":
                    rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
                    pygame.draw.rect(surface, COLOR_WALL, rect)
                    inner_rect = pygame.Rect(x + 3, y + 3, TILE_SIZE - 6, TILE_SIZE - 6)
                    pygame.draw.rect(surface, COLOR_WALL_INNER, inner_rect, border_radius=4)

                elif cell == "-":
                    pygame.draw.rect(surface, COLOR_GATE, (x, y + TILE_SIZE // 2 - 3, TILE_SIZE, 6), border_radius=2)

                elif cell == ".":
                    pygame.draw.circle(surface, COLOR_PELLET, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), 3)

                elif cell == "o":
                    pulse_radius = 6 + int(math.sin(pulse_timer * 6) * 2.5)
                    pygame.draw.circle(surface, COLOR_ENERGIZER, (x + TILE_SIZE // 2, y + TILE_SIZE // 2), pulse_radius)


class Pacman:
    def __init__(self, start_gx, start_gy):
        self.spawn_gx = start_gx
        self.spawn_gy = start_gy
        self.reset()

    def reset(self):
        self.gx = self.spawn_gx
        self.gy = self.spawn_gy
        self.dir_x, self.dir_y = DIR_LEFT
        self.buffered_dir = DIR_LEFT
        self.offset = 0.0
        self.speed = 3.6
        self.is_moving = True

        self.mouth_angle = 45
        self.mouth_speed = 6
        self.mouth_opening = True
        self.is_alive = True
        self.death_anim_frame = 0

    @property
    def pixel_x(self):
        return self.gx * TILE_SIZE + TILE_SIZE // 2 + self.dir_x * self.offset

    @property
    def pixel_y(self):
        return self.gy * TILE_SIZE + TILE_SIZE // 2 + self.dir_y * self.offset

    def request_direction(self, new_dir):
        # 1. Instant 180-degree reversal
        if new_dir[0] == -self.dir_x and new_dir[1] == -self.dir_y and self.is_moving:
            self.gx = (self.gx + self.dir_x) % COLS
            self.gy = self.gy + self.dir_y
            self.dir_x, self.dir_y = new_dir
            self.offset = max(0.0, TILE_SIZE - self.offset)
            self.buffered_dir = new_dir
            return

        self.buffered_dir = new_dir

        # If currently stopped at a wall, check if requested turn is walkable right now
        if not self.is_moving:
            if Maze(MAZE_LAYOUT).is_walkable(self.gx + new_dir[0], self.gy + new_dir[1]):
                self.dir_x, self.dir_y = new_dir
                self.is_moving = True

    def update(self, maze):
        if not self.is_alive:
            self.death_anim_frame += 1
            return

        # Animate mouth chomp
        if self.is_moving:
            if self.mouth_opening:
                self.mouth_angle += self.mouth_speed
                if self.mouth_angle >= 45:
                    self.mouth_angle = 45
                    self.mouth_opening = False
            else:
                self.mouth_angle -= self.mouth_speed
                if self.mouth_angle <= 2:
                    self.mouth_angle = 2
                    self.mouth_opening = True

        # Check if stopped and player wants to move
        if not self.is_moving:
            if self.buffered_dir != DIR_NONE:
                if maze.is_walkable(self.gx + self.buffered_dir[0], self.gy + self.buffered_dir[1]):
                    self.dir_x, self.dir_y = self.buffered_dir
                    self.is_moving = True
                    self.offset = 0.0

        if not self.is_moving:
            return

        # Advance along corridor
        self.offset += self.speed

        # Reached or passed the next tile center
        if self.offset >= TILE_SIZE:
            # Advance to next tile
            self.gx += self.dir_x
            self.gy += self.dir_y
            self.offset -= TILE_SIZE

            # Tunnel wrap-around at row 10
            if self.gy == 10:
                self.gx = self.gx % COLS

            # Check buffered turn at intersection
            turned = False
            if self.buffered_dir != (self.dir_x, self.dir_y):
                bx, by = self.buffered_dir
                if maze.is_walkable(self.gx + bx, self.gy + by):
                    self.dir_x, self.dir_y = bx, by
                    turned = True

            # If not turned, check if path forward is walkable
            if not turned:
                if not maze.is_walkable(self.gx + self.dir_x, self.gy + self.dir_y):
                    # Wall reached: stop cleanly at tile center
                    self.offset = 0.0
                    self.is_moving = False

    def draw(self, surface, offset_y):
        cx = int(self.pixel_x)
        cy = int(self.pixel_y + offset_y)
        radius = TILE_SIZE // 2 - 2

        if not self.is_alive:
            # Death animation
            max_frames = 40
            progress = min(1.0, self.death_anim_frame / max_frames)
            wedge = int(progress * 180)
            if wedge < 180:
                pygame.draw.circle(surface, COLOR_PACMAN, (cx, cy), radius)
                p1 = (cx, cy)
                p2 = (cx + radius * 1.5 * math.cos(math.radians(90 - wedge)),
                      cy - radius * 1.5 * math.sin(math.radians(90 - wedge)))
                p3 = (cx + radius * 1.5 * math.cos(math.radians(90 + wedge)),
                      cy - radius * 1.5 * math.sin(math.radians(90 + wedge)))
                pygame.draw.polygon(surface, COLOR_BG, [p1, p2, (cx, cy - radius * 2), p3])
            return

        # Determine mouth orientation
        if (self.dir_x, self.dir_y) == DIR_RIGHT:
            base_angle = 0
        elif (self.dir_x, self.dir_y) == DIR_DOWN:
            base_angle = 270
        elif (self.dir_x, self.dir_y) == DIR_LEFT:
            base_angle = 180
        elif (self.dir_x, self.dir_y) == DIR_UP:
            base_angle = 90
        else:
            base_angle = 0

        mouth = self.mouth_angle
        if mouth <= 3 or not self.is_moving:
            pygame.draw.circle(surface, COLOR_PACMAN, (cx, cy), radius)
        else:
            points = [(cx, cy)]
            step = 6
            start_deg = int(base_angle + mouth)
            end_deg = int(base_angle + 360 - mouth)
            for deg in range(start_deg, end_deg + 1, step):
                rad = math.radians(deg)
                px = cx + radius * math.cos(rad)
                py = cy - radius * math.sin(rad)
                points.append((px, py))
            points.append((cx, cy))
            if len(points) >= 3:
                pygame.draw.polygon(surface, COLOR_PACMAN, points)


class Ghost:
    def __init__(self, name, color, home_tile, scatter_corner, release_delay_sec=0.0):
        self.name = name
        self.color = color
        self.home_tile = home_tile
        self.scatter_corner = scatter_corner
        self.release_delay_sec = release_delay_sec
        self.reset()

    def reset(self):
        self.gx, self.gy = self.home_tile
        self.dir_x, self.dir_y = DIR_UP
        self.offset = 0.0
        self.speed = 3.0
        self.anim_timer = 0
        self.release_timer = self.release_delay_sec

        # Blinky starts outside, others start inside
        if self.name == "Blinky":
            self.state = "NORMAL"
        else:
            self.state = "IN_HOUSE"

    @property
    def pixel_x(self):
        if self.state == "IN_HOUSE":
            return self.gx * TILE_SIZE + TILE_SIZE // 2
        return self.gx * TILE_SIZE + TILE_SIZE // 2 + self.dir_x * self.offset

    @property
    def pixel_y(self):
        if self.state == "IN_HOUSE":
            # Smooth bobbing in house
            bob = math.sin(self.anim_timer * 0.1) * 4.0
            return self.gy * TILE_SIZE + TILE_SIZE // 2 + bob
        return self.gy * TILE_SIZE + TILE_SIZE // 2 + self.dir_y * self.offset

    def update(self, pacman, blinky_gx, blinky_gy, maze, dt):
        self.anim_timer += 1

        # 1. State: IN_HOUSE waiting to be released
        if self.state == "IN_HOUSE":
            self.release_timer -= dt
            if self.release_timer <= 0:
                self.state = "EXITING_HOUSE"
                self.offset = 0.0
            return

        # 2. State: EXITING_HOUSE (navigate up through gate to row 8)
        if self.state == "EXITING_HOUSE":
            # Target row 8, column 9 (outside gate)
            target_x = 9 * TILE_SIZE + TILE_SIZE // 2
            target_y = 8 * TILE_SIZE + TILE_SIZE // 2

            cur_px = self.gx * TILE_SIZE + TILE_SIZE // 2 + self.dir_x * self.offset
            cur_py = self.gy * TILE_SIZE + TILE_SIZE // 2 + self.dir_y * self.offset

            # Move horizontally to column 9 first
            if abs(cur_px - target_x) > 2.0:
                step = 2.5 if cur_px < target_x else -2.5
                self.dir_x = 1 if step > 0 else -1
                self.dir_y = 0
                self.offset += abs(step)
                if self.offset >= TILE_SIZE:
                    self.gx += self.dir_x
                    self.offset -= TILE_SIZE
            else:
                # Aligned with column 9, move straight up through gate
                self.gx = 9
                self.dir_x = 0
                self.dir_y = -1
                self.offset += 2.5
                if self.offset >= TILE_SIZE:
                    self.gy += self.dir_y
                    self.offset -= TILE_SIZE

                # Check if arrived at row 8
                if self.gy <= 8:
                    self.gy = 8
                    self.offset = 0.0
                    self.dir_x = -1
                    self.dir_y = 0
                    self.state = "NORMAL"
            return

        # Current speeds for normal, frightened, and eaten
        if self.state == "EATEN_EYES":
            move_speed = 5.5
        elif self.state == "FRIGHTENED":
            move_speed = 1.8
        else:
            move_speed = 3.0

        # Advance along corridor
        self.offset += move_speed

        if self.offset >= TILE_SIZE:
            # Reached next tile!
            self.gx += self.dir_x
            self.gy += self.dir_y
            self.offset -= TILE_SIZE

            # Tunnel wrap-around at row 10
            if self.gy == 10:
                self.gx = self.gx % COLS

            # Check if eaten eyes reached ghost house entrance (row 8 col 9 or row 9 col 9)
            if self.state == "EATEN_EYES":
                if self.gx == 9 and self.gy in [8, 9, 10]:
                    if self.gy == 10:
                        # Revive!
                        self.state = "EXITING_HOUSE"
                        self.offset = 0.0
                        return
                    else:
                        # Pass downward through gate
                        self.dir_x, self.dir_y = DIR_DOWN
                        return

            # Choose next direction at intersection
            can_cross = (self.state == "EATEN_EYES")
            valid_dirs = []
            opp = (-self.dir_x, -self.dir_y)

            for d in ALL_DIRECTIONS:
                nx = self.gx + d[0]
                ny = self.gy + d[1]
                if maze.is_walkable(nx, ny, can_cross_gate=can_cross):
                    if d != opp:
                        valid_dirs.append(d)

            # Dead end check
            if not valid_dirs:
                if maze.is_walkable(self.gx + opp[0], self.gy + opp[1], can_cross_gate=can_cross):
                    valid_dirs.append(opp)
                else:
                    valid_dirs.append(DIR_NONE)

            # Target tile determination
            if self.state == "FRIGHTENED":
                self.dir_x, self.dir_y = random.choice(valid_dirs)
            else:
                target_gx, target_gy = self.get_target_tile(pacman, blinky_gx, blinky_gy)
                best_dir = valid_dirs[0]
                best_dist = float("inf")
                for d in valid_dirs:
                    cand_gx = self.gx + d[0]
                    cand_gy = self.gy + d[1]
                    dist = (cand_gx - target_gx) ** 2 + (cand_gy - target_gy) ** 2
                    if dist < best_dist:
                        best_dist = dist
                        best_dir = d
                self.dir_x, self.dir_y = best_dir

    def get_target_tile(self, pacman, blinky_gx, blinky_gy):
        if self.state == "EATEN_EYES":
            # Return to row 8 column 9 (above gate)
            return 9, 8

        pgx, pgy = pacman.gx, pacman.gy

        if self.name == "Blinky":
            # Shadow (Red): Direct chase
            return pgx, pgy

        elif self.name == "Pinky":
            # Speedy (Pink): Ambush 4 tiles ahead of Pac-Man
            return pgx + pacman.dir_x * 4, pgy + pacman.dir_y * 4

        elif self.name == "Inky":
            # Bashful (Cyan): Flank using Pac-Man & Blinky vector
            lead_x = pgx + pacman.dir_x * 2
            lead_y = pgy + pacman.dir_y * 2
            tx = lead_x + (lead_x - blinky_gx)
            ty = lead_y + (lead_y - blinky_gy)
            return tx, ty

        elif self.name == "Clyde":
            # Pokey (Orange): Chases when far (> 6 tiles), retreats to corner when close
            dist = math.hypot(self.gx - pgx, self.gy - pgy)
            if dist > 6:
                return pgx, pgy
            else:
                return self.scatter_corner

        return pgx, pgy

    def draw(self, surface, offset_y, frightened_time_left):
        cx = int(self.pixel_x)
        cy = int(self.pixel_y + offset_y)
        r = TILE_SIZE // 2 - 2

        # 1. EATEN STATE: Eyes only
        if self.state == "EATEN_EYES":
            self._draw_eyes(surface, cx, cy, r)
            return

        # 2. FRIGHTENED STATE
        body_color = self.color
        if self.state == "FRIGHTENED":
            if frightened_time_left < 2.0 and (int(frightened_time_left * 5) % 2 == 0):
                body_color = COLOR_FRIGHTENED_FLASH
            else:
                body_color = COLOR_FRIGHTENED

        # Head dome
        pygame.draw.circle(surface, body_color, (cx, cy - 2), r)
        # Torso
        pygame.draw.rect(surface, body_color, (cx - r, cy - 2, r * 2, r + 2))

        # Wavy bottom skirt
        body_bottom = cy + r
        anim_offset = (self.anim_timer // 8) % 2
        scallop_w = (r * 2) / 3
        feet_points = []
        for i in range(3):
            sx = cx - r + i * scallop_w
            mx = sx + scallop_w / 2
            ex = sx + scallop_w
            depth = 3 if ((i + anim_offset) % 2 == 0) else -2
            feet_points.append((mx, body_bottom + depth))
            feet_points.append((ex, body_bottom))
        pygame.draw.polygon(surface, body_color, [(cx - r, cy), (cx + r, cy), (cx + r, body_bottom)] + feet_points[::-1] + [(cx - r, body_bottom)])

        # Eyes & mouth
        if self.state == "FRIGHTENED":
            eye_col = (255, 180, 180) if body_color == COLOR_FRIGHTENED else (255, 0, 0)
            pygame.draw.circle(surface, eye_col, (cx - 5, cy - 4), 2)
            pygame.draw.circle(surface, eye_col, (cx + 5, cy - 4), 2)
            pygame.draw.line(surface, eye_col, (cx - 6, cy + 4), (cx - 2, cy + 2), 2)
            pygame.draw.line(surface, eye_col, (cx - 2, cy + 2), (cx + 2, cy + 4), 2)
            pygame.draw.line(surface, eye_col, (cx + 2, cy + 4), (cx + 6, cy + 2), 2)
        else:
            self._draw_eyes(surface, cx, cy, r)

    def _draw_eyes(self, surface, cx, cy, r):
        eye_ox = self.dir_x * 3
        eye_oy = self.dir_y * 3
        pygame.draw.ellipse(surface, (255, 255, 255), (cx - 8 + eye_ox, cy - 8 + eye_oy, 7, 9))
        pygame.draw.ellipse(surface, (255, 255, 255), (cx + 1 + eye_ox, cy - 8 + eye_oy, 7, 9))

        pupil_ox = self.dir_x * 2
        pupil_oy = self.dir_y * 2
        pygame.draw.circle(surface, (30, 30, 200), (cx - 5 + eye_ox + pupil_ox, cy - 4 + eye_oy + pupil_oy), 2)
        pygame.draw.circle(surface, (30, 30, 200), (cx + 4 + eye_ox + pupil_ox, cy - 4 + eye_oy + pupil_oy), 2)


class FloatingScore:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.life = 45

    def update(self):
        self.life -= 1
        self.y -= 0.6

    def draw(self, surface):
        draw_hud_text(surface, self.text, int(self.x), int(self.y), size=18, color=(0, 255, 255), align="center")


def run_pacman():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Arcade")
    clock = pygame.time.Clock()

    hs_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "highscore.json")
    high_score = common_ui.load_high_score(hs_file, 1000) if common_ui else 1000

    def init_game_level():
        maze = Maze(MAZE_LAYOUT)
        pacman = Pacman(9, 16)
        ghosts = [
            Ghost("Blinky", (255, 0, 0), (9, 8), (COLS - 2, 0), release_delay_sec=0.0),
            Ghost("Pinky", (255, 184, 255), (9, 10), (1, 0), release_delay_sec=1.5),
            Ghost("Inky", (0, 255, 255), (8, 10), (COLS - 1, ROWS - 1), release_delay_sec=3.5),
            Ghost("Clyde", (255, 184, 82), (10, 10), (0, ROWS - 1), release_delay_sec=6.0),
        ]
        return maze, pacman, ghosts

    score = 0
    lives = 3
    level = 1
    state = "READY"  # READY, PLAYING, PAUSED, PACMAN_DYING, GAME_OVER, VICTORY
    ready_timer = 90
    frightened_timer = 0.0
    frightened_combo = 0
    pulse_timer = 0.0
    floating_scores = []

    maze, pacman, ghosts = init_game_level()

    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        pulse_timer += dt

        # ================= EVENT HANDLING =================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_p and state in ["PLAYING", "PAUSED"]:
                    state = "PAUSED" if state == "PLAYING" else "PLAYING"

                if state == "PLAYING":
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        pacman.request_direction(DIR_UP)
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        pacman.request_direction(DIR_DOWN)
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        pacman.request_direction(DIR_LEFT)
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        pacman.request_direction(DIR_RIGHT)

                elif state in ["GAME_OVER", "VICTORY"]:
                    if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_r]:
                        if state == "GAME_OVER":
                            score = 0
                            lives = 3
                            level = 1
                        else:
                            level += 1
                        maze, pacman, ghosts = init_game_level()
                        state = "READY"
                        ready_timer = 90

        # ================= UPDATE LOGIC =================
        if state == "READY":
            ready_timer -= 1
            if ready_timer <= 0:
                state = "PLAYING"

        elif state == "PLAYING":
            # Update frightened timer
            if frightened_timer > 0:
                frightened_timer -= dt
                if frightened_timer <= 0:
                    frightened_timer = 0.0
                    for g in ghosts:
                        if g.state == "FRIGHTENED":
                            g.state = "NORMAL"

            # Update Pacman
            pacman.update(maze)

            # Pellet & Energizer collection
            cur_gx = pacman.gx
            cur_gy = pacman.gy
            if 0 <= cur_gx < COLS and 0 <= cur_gy < ROWS:
                cell = maze.grid[cur_gy][cur_gx]
                if cell == ".":
                    maze.grid[cur_gy][cur_gx] = " "
                    score += 10
                    maze.pellet_count -= 1
                elif cell == "o":
                    maze.grid[cur_gy][cur_gx] = " "
                    score += 50
                    maze.pellet_count -= 1
                    frightened_timer = 7.0
                    frightened_combo = 0
                    for g in ghosts:
                        if g.state not in ["EATEN_EYES", "IN_HOUSE", "EXITING_HOUSE"]:
                            g.state = "FRIGHTENED"

            # Check Victory
            if maze.pellet_count <= 0:
                state = "VICTORY"
                score += 1000
                if score > high_score:
                    high_score = score
                    if common_ui:
                        common_ui.save_high_score(hs_file, high_score)

            # Update Ghosts
            blinky_gx = ghosts[0].gx
            blinky_gy = ghosts[0].gy
            for g in ghosts:
                g.update(pacman, blinky_gx, blinky_gy, maze, dt)

                # Check collision with Pac-Man
                dist = math.hypot(pacman.pixel_x - g.pixel_x, pacman.pixel_y - g.pixel_y)
                if dist < TILE_SIZE * 0.75:
                    if g.state == "FRIGHTENED":
                        # Pacman eats ghost
                        g.state = "EATEN_EYES"
                        frightened_combo += 1
                        pts = int(200 * (2 ** min(3, frightened_combo - 1)))
                        score += pts
                        floating_scores.append(FloatingScore(f"+{pts}", g.pixel_x, g.pixel_y + HEADER_HEIGHT))
                    elif g.state == "NORMAL":
                        # Pacman caught!
                        pacman.is_alive = False
                        state = "PACMAN_DYING"
                        break

            # Update floating score text
            for fs in floating_scores[:]:
                fs.update()
                if fs.life <= 0:
                    floating_scores.remove(fs)

            # High score update
            if score > high_score:
                high_score = score
                if common_ui:
                    common_ui.save_high_score(hs_file, high_score)

        elif state == "PACMAN_DYING":
            pacman.update(maze)
            if pacman.death_anim_frame > 50:
                lives -= 1
                if lives <= 0:
                    state = "GAME_OVER"
                    if common_ui:
                        common_ui.save_high_score(hs_file, high_score)
                else:
                    pacman.reset()
                    for g in ghosts:
                        g.reset()
                    state = "READY"
                    ready_timer = 90

        # ================= DRAWING =================
        screen.fill(COLOR_BG)

        # 1. Top HUD
        draw_hud_text(screen, "1UP", 40, 10, size=20, color=(255, 100, 100))
        draw_hud_text(screen, f"{int(score):06d}", 40, 26, size=22, color=COLOR_TEXT)

        draw_hud_text(screen, "HIGH SCORE", SCREEN_WIDTH // 2, 10, size=20, color=(255, 200, 0), align="midtop")
        draw_hud_text(screen, f"{int(high_score):06d}", SCREEN_WIDTH // 2, 26, size=22, color=COLOR_TEXT, align="midtop")

        draw_hud_text(screen, f"LVL {level}", SCREEN_WIDTH - 40, 18, size=22, color=(100, 255, 100), align="topright")

        # 2. Maze
        maze.draw(screen, HEADER_HEIGHT, pulse_timer)

        # 3. Pacman & Ghosts
        pacman.draw(screen, HEADER_HEIGHT)
        for g in ghosts:
            g.draw(screen, HEADER_HEIGHT, frightened_timer)

        # Floating bonus scores
        for fs in floating_scores:
            fs.draw(screen)

        # 4. Bottom HUD
        footer_y = HEADER_HEIGHT + ROWS * TILE_SIZE + 10
        for i in range(lives):
            lx = 30 + i * 26
            ly = footer_y + 12
            pygame.draw.circle(screen, COLOR_PACMAN, (lx, ly), 9)
            pygame.draw.polygon(screen, COLOR_BG, [(lx, ly), (lx + 10, ly - 6), (lx + 10, ly + 6)])

        draw_hud_text(screen, "PAUSE: P | QUIT: ESC", SCREEN_WIDTH - 20, footer_y + 4, size=18, color=(140, 150, 180), align="topright")

        # 5. Overlays
        if state == "READY":
            draw_hud_text(screen, "READY!", SCREEN_WIDTH // 2, HEADER_HEIGHT + 11 * TILE_SIZE + 16,
                          size=28, color=(255, 255, 0), align="center")

        elif state == "PAUSED":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            draw_hud_text(screen, "GAME PAUSED", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20,
                          size=36, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Press [P] to Resume", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25,
                          size=22, color=(0, 220, 255), align="center")

        elif state == "GAME_OVER":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((10, 5, 20, 220))
            screen.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 130, 380, 260)
            if common_ui:
                common_ui.draw_panel(screen, panel_rect, border_color=(255, 60, 60), bg_color=(25, 10, 25, 230))

            draw_hud_text(screen, "GAME OVER", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 90,
                          size=42, color=(255, 50, 50), align="center")
            draw_hud_text(screen, f"Final Score: {int(score)}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35,
                          size=26, color=(255, 255, 255), align="center")
            draw_hud_text(screen, f"High Score: {int(high_score)}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                          size=22, color=(255, 215, 0), align="center")
            draw_hud_text(screen, "Press [ENTER] to Play Again", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          size=22, color=(0, 255, 180), align="center")
            draw_hud_text(screen, "Press [ESC] to Exit", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80,
                          size=18, color=(160, 160, 160), align="center")

        elif state == "VICTORY":
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 20, 10, 210))
            screen.blit(overlay, (0, 0))

            panel_rect = pygame.Rect(SCREEN_WIDTH // 2 - 190, SCREEN_HEIGHT // 2 - 120, 380, 240)
            if common_ui:
                common_ui.draw_panel(screen, panel_rect, border_color=(0, 255, 150), bg_color=(10, 30, 20, 230))

            draw_hud_text(screen, "STAGE CLEARED!", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80,
                          size=36, color=(0, 255, 160), align="center")
            draw_hud_text(screen, "Bonus: +1000 PTS", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 35,
                          size=24, color=(255, 255, 0), align="center")
            draw_hud_text(screen, f"Current Score: {int(score)}", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
                          size=22, color=(255, 255, 255), align="center")
            draw_hud_text(screen, "Press [ENTER] for Next Level", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
                          size=22, color=(0, 230, 255), align="center")

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_pacman()
