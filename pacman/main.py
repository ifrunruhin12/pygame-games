import pygame
import random

pygame.init()

# ================= MAP =================

maze = [
    list("###################"),
    list("#.................#"),
    list("#.####.#####.####.#"),
    list("#.................#"),
    list("#.####.#...#.####.#"),
    list("#.................#"),
    list("#.####.#####.####.#"),
    list("#.................#"),
    list("#.####.#...#.####.#"),
    list("#........P........#"),
    list("#.####.#####.####.#"),
    list("#.................#"),
    list("###################")
]

# ================= SETTINGS =================

TILE_SIZE = 32
SCREEN_WIDTH = len(maze[0]) * TILE_SIZE
SCREEN_HEIGHT = len(maze) * TILE_SIZE


FPS = 60

# ================= COLORS =================

BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)

# ================= WINDOW =================

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Pac-Man")

clock = pygame.time.Clock()

# ================= DIRECTIONS =================

directions = [
    (0, -1),  # Up
    (0, 1),   # Down
    (-1, 0),  # Left
    (1, 0)    # Right
]

# ================= PLAYER =================

player_x = 0
player_y = 0

for row_index, row in enumerate(maze):

    for col_index, tile in enumerate(row):

        if tile == "P":

            player_x = col_index * TILE_SIZE
            player_y = row_index * TILE_SIZE

# ================= MOVEMENT =================

player_speed = 5

move_x = 0
move_y = 0

# ================= GHOST =================

ghost_x = 9 * TILE_SIZE
ghost_y = 5 * TILE_SIZE

ghost_speed = 2

ghost_direction = (1, 0)  # Moving right initially

# ================= GAME LOOP =================

score = 0

running = True

while running:

    # ---------- EVENTS ----------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ---------- INPUT ----------

    keys = pygame.key.get_pressed()

    move_x = 0
    move_y = 0

    if keys[pygame.K_LEFT]:
        move_x = -player_speed

    if keys[pygame.K_RIGHT]:
        move_x = player_speed

    if keys[pygame.K_UP]:
        move_y = -player_speed

    if keys[pygame.K_DOWN]:
        move_y = player_speed

    # COLLISION CHECK

    next_x = player_x + move_x
    next_y = player_y + move_y

    grid_x = (next_x + TILE_SIZE // 2) // TILE_SIZE
    grid_y = (next_y + TILE_SIZE // 2) // TILE_SIZE

    if maze[grid_y][grid_x] != "#":
        player_x = next_x
        player_y = next_y

    player_grid_x = (player_x + TILE_SIZE // 2) // TILE_SIZE
    player_grid_y = (player_y + TILE_SIZE // 2) // TILE_SIZE

    # PALLETTE CHECK
    if maze[player_grid_y][player_grid_x] == ".":
        
        maze[player_grid_y][player_grid_x] = " "
        score += 1

        print(f"Score: {score}")

    # ---------- GHOST MOVEMENT ----------

    ghost_next_x = ghost_x + ghost_direction[0] * ghost_speed
    ghost_next_y = ghost_y + ghost_direction[1] * ghost_speed

    ghost_grid_x = (ghost_next_x + TILE_SIZE // 2) // TILE_SIZE
    ghost_grid_y = (ghost_next_y + TILE_SIZE // 2) // TILE_SIZE

    # WALL CHECK

    if maze[ghost_grid_y][ghost_grid_x] != "#":

        ghost_x = ghost_next_x
        ghost_y = ghost_next_y

    else:

        ghost_direction = random.choice(directions)


    player_rect = pygame.Rect(player_x, player_y, TILE_SIZE, TILE_SIZE)
    ghost_rect = pygame.Rect(ghost_x, ghost_y, TILE_SIZE, TILE_SIZE)
    if player_rect.colliderect(ghost_rect):
        print("Game Over!")
        running = False

    # ---------- DRAW ----------

    screen.fill(BLACK)

    # DRAW MAZE

    for row_index, row in enumerate(maze):

        for col_index, tile in enumerate(row):

            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            if tile == "#":

                pygame.draw.rect(
                    screen,
                    BLUE,
                    (x, y, TILE_SIZE, TILE_SIZE)
                )

            if tile == ".":

                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    ),
                    4
                )

    # DRAW PLAYER

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            player_x + TILE_SIZE // 2,
            player_y + TILE_SIZE // 2
        ),
        TILE_SIZE // 2 - 2
    )

    # DRAW GHOST
    pygame.draw.circle(
        screen,
        (255, 0, 0),
        (
            ghost_x + TILE_SIZE // 2,
            ghost_y + TILE_SIZE // 2
        ),
        TILE_SIZE // 2 - 2
    )

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
