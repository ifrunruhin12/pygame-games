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
RED = (255, 0, 0)

# ================= WINDOW =================

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Pac-Man")

clock = pygame.time.Clock()

# ================= DIRECTIONS =================

directions = [
    (0, -1),   # UP
    (0, 1),    # DOWN
    (-1, 0),   # LEFT
    (1, 0)     # RIGHT
]

# ================= PLAYER =================

player_x = 0
player_y = 0

for row_index, row in enumerate(maze):

    for col_index, tile in enumerate(row):

        if tile == "P":

            player_x = col_index * TILE_SIZE
            player_y = row_index * TILE_SIZE

# ================= PLAYER MOVEMENT =================

player_speed = 4

move_x = 0
move_y = 0

# ================= GHOST =================

ghost_x = 9 * TILE_SIZE
ghost_y = 5 * TILE_SIZE

ghost_speed = 2

ghost_direction = random.choice(directions)

# ================= SCORE =================

score = 0

# ================= GAME LOOP =================

running = True

while running:

    # ================= EVENTS =================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ================= INPUT =================

    keys = pygame.key.get_pressed()

    move_x = 0
    move_y = 0

    if keys[pygame.K_LEFT]:
        move_x = -player_speed

    elif keys[pygame.K_RIGHT]:
        move_x = player_speed

    elif keys[pygame.K_UP]:
        move_y = -player_speed

    elif keys[pygame.K_DOWN]:
        move_y = player_speed

    # ================= PLAYER MOVEMENT =================

    next_x = player_x + move_x
    next_y = player_y + move_y

    grid_x = (
        next_x + TILE_SIZE // 2
    ) // TILE_SIZE

    grid_y = (
        next_y + TILE_SIZE // 2
    ) // TILE_SIZE

    if maze[grid_y][grid_x] != "#":

        player_x = next_x
        player_y = next_y

    # ================= PLAYER TILE =================

    player_grid_x = (
        player_x + TILE_SIZE // 2
    ) // TILE_SIZE

    player_grid_y = (
        player_y + TILE_SIZE // 2
    ) // TILE_SIZE

    # ================= PELLET CHECK =================

    if maze[player_grid_y][player_grid_x] == ".":

        maze[player_grid_y][player_grid_x] = " "

        score += 1

        print("Score:", score)

    # ================= GHOST MOVEMENT =================

    ghost_grid_x = (
        ghost_x + TILE_SIZE // 2
    ) // TILE_SIZE

    ghost_grid_y = (
        ghost_y + TILE_SIZE // 2
    ) // TILE_SIZE

    # Ghost center
    ghost_center_x = ghost_x + TILE_SIZE // 2
    ghost_center_y = ghost_y + TILE_SIZE // 2

    tile_center_x = (
        ghost_grid_x * TILE_SIZE
        + TILE_SIZE // 2
    )

    tile_center_y = (
        ghost_grid_y * TILE_SIZE
        + TILE_SIZE // 2
    )

    # Check if ghost is aligned to tile center
    at_center = (
        abs(ghost_center_x - tile_center_x) < 2
        and
        abs(ghost_center_y - tile_center_y) < 2
    )

    # ================= AI DECISION =================

    if at_center:

        valid_directions = []

        for direction in directions:

            dx = direction[0]
            dy = direction[1]

            next_grid_x = ghost_grid_x + dx
            next_grid_y = ghost_grid_y + dy

            # Boundary check
            if (
                0 <= next_grid_x < len(maze[0])
                and
                0 <= next_grid_y < len(maze)
            ):

                # Wall check
                if maze[next_grid_y][next_grid_x] != "#":

                    valid_directions.append(direction)

        # Prevent instant reverse
        opposite_direction = (
            -ghost_direction[0],
            -ghost_direction[1]
        )

        if (
            opposite_direction in valid_directions
            and
            len(valid_directions) > 1
        ):

            valid_directions.remove(opposite_direction)

        # ================= CHASE AI =================

        best_direction = ghost_direction

        shortest_distance = float("inf")

        for direction in valid_directions:

            dx = direction[0]
            dy = direction[1]

            test_x = ghost_grid_x + dx
            test_y = ghost_grid_y + dy

            # Manhattan Distance
            distance = (
                abs(test_x - player_grid_x)
                +
                abs(test_y - player_grid_y)
            )

            if distance < shortest_distance:

                shortest_distance = distance

                best_direction = direction

        ghost_direction = best_direction

    # ================= MOVE GHOST =================

    ghost_x += ghost_direction[0] * ghost_speed
    ghost_y += ghost_direction[1] * ghost_speed

    # ================= COLLISION =================

    player_rect = pygame.Rect(
        player_x,
        player_y,
        TILE_SIZE,
        TILE_SIZE
    )

    ghost_rect = pygame.Rect(
        ghost_x,
        ghost_y,
        TILE_SIZE,
        TILE_SIZE
    )

    if player_rect.colliderect(ghost_rect):

        print("GAME OVER!")

        running = False

    # ================= DRAW =================

    screen.fill(BLACK)

    # ---------- DRAW MAZE ----------

    for row_index, row in enumerate(maze):

        for col_index, tile in enumerate(row):

            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE

            # WALLS
            if tile == "#":

                pygame.draw.rect(
                    screen,
                    BLUE,
                    (
                        x,
                        y,
                        TILE_SIZE,
                        TILE_SIZE
                    )
                )

            # PELLETS
            elif tile == ".":

                pygame.draw.circle(
                    screen,
                    WHITE,
                    (
                        x + TILE_SIZE // 2,
                        y + TILE_SIZE // 2
                    ),
                    4
                )

    # ---------- DRAW PLAYER ----------

    pygame.draw.circle(
        screen,
        YELLOW,
        (
            player_x + TILE_SIZE // 2,
            player_y + TILE_SIZE // 2
        ),
        TILE_SIZE // 2 - 2
    )

    # ---------- DRAW GHOST ----------

    pygame.draw.circle(
        screen,
        RED,
        (
            ghost_x + TILE_SIZE // 2,
            ghost_y + TILE_SIZE // 2
        ),
        TILE_SIZE // 2 - 2
    )

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
