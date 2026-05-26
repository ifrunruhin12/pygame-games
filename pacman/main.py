import pygame

pygame.init()

# ================= MAP =================

maze = [
    "###################",
    "#.................#",
    "#.####.#####.####.#",
    "#.................#",
    "#.####.#...#.####.#",
    "#.................#",
    "#.####.#####.####.#",
    "#.................#",
    "#.####.#...#.####.#",
    "#........P........#",
    "#.####.#####.####.#",
    "#.................#",
    "###################"
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

# ================= WINDOW =================

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption("Pac-Man")

clock = pygame.time.Clock()

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

# ================= GAME LOOP =================

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

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
