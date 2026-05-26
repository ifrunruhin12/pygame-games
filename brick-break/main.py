import pygame
import math

pygame.init()

# ================= SETTINGS =================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 760
FPS = 60

# Paddle
PADDLE_WIDTH = 120
PADDLE_HEIGHT = 20
PADDLE_SPEED = 8

# Ball
BALL_RADIUS = 12
BALL_SPEED = 7

# Bricks
BRICK_WIDTH = 100
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_PADDING = 10

BRICK_OFFSET_TOP = 50

BRICK_OFFSET_LEFT = (
    SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))
) // 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# ================= WINDOW =================

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.display.set_caption("Brick Breaker")

clock = pygame.time.Clock()

# ================= PADDLE =================

paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = SCREEN_HEIGHT - 50

# ================= BALL =================

ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2

ball_speed_x = 5
ball_speed_y = -5

# ================= BRICKS =================

bricks = []

for row in range(BRICK_ROWS):

    for col in range(BRICK_COLS):

        brick_x = (
            BRICK_OFFSET_LEFT
            + col * (BRICK_WIDTH + BRICK_PADDING)
        )

        brick_y = (
            BRICK_OFFSET_TOP
            + row * (BRICK_HEIGHT + BRICK_PADDING)
        )

        brick = pygame.Rect(
            brick_x,
            brick_y,
            BRICK_WIDTH,
            BRICK_HEIGHT
        )

        bricks.append(brick)

# ================= SCORE =================

score = 0

# ================= GAME LOOP =================

running = True

while running:

    # ---------- EVENTS ----------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # ---------- INPUT ----------

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        paddle_x -= PADDLE_SPEED

    if keys[pygame.K_RIGHT]:
        paddle_x += PADDLE_SPEED

    # ---------- PADDLE BOUNDARIES ----------

    if paddle_x < 0:
        paddle_x = 0

    if paddle_x + PADDLE_WIDTH > SCREEN_WIDTH:
        paddle_x = SCREEN_WIDTH - PADDLE_WIDTH

    # ---------- BALL MOVEMENT ----------

    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # ---------- WALL COLLISION ----------

    if ball_x - BALL_RADIUS <= 0:
        ball_x = BALL_RADIUS
        ball_speed_x *= -1

    if ball_x + BALL_RADIUS >= SCREEN_WIDTH:
        ball_x = SCREEN_WIDTH - BALL_RADIUS
        ball_speed_x *= -1

    if ball_y - BALL_RADIUS <= 0:
        ball_y = BALL_RADIUS
        ball_speed_y *= -1

    # ---------- LOSE CONDITION ----------

    if ball_y - BALL_RADIUS > SCREEN_HEIGHT:

        print("GAME OVER 💀")
        print("FINAL SCORE:", score)

        running = False

    # ---------- RECTS ----------

    paddle_rect = pygame.Rect(
        paddle_x,
        paddle_y,
        PADDLE_WIDTH,
        PADDLE_HEIGHT
    )

    ball_rect = pygame.Rect(
        ball_x - BALL_RADIUS,
        ball_y - BALL_RADIUS,
        BALL_RADIUS * 2,
        BALL_RADIUS * 2
    )

    # ---------- PADDLE COLLISION ----------

    if (
        paddle_rect.colliderect(ball_rect)
        and ball_speed_y > 0
    ):

        # Prevent sticking
        ball_y = paddle_y - BALL_RADIUS

        # Bounce upward
        ball_speed_y *= -1

        # Paddle influence
        paddle_center = paddle_x + PADDLE_WIDTH / 2

        distance_from_center = ball_x - paddle_center

        influence = distance_from_center / 10

        ball_speed_x += influence

        # Prevent boring vertical loops
        if abs(ball_speed_x) < 2:

            if ball_speed_x >= 0:
                ball_speed_x = 2
            else:
                ball_speed_x = -2

        # Normalize speed
        speed = math.sqrt(
            ball_speed_x ** 2 + ball_speed_y ** 2
        )

        ball_speed_x = (
            ball_speed_x / speed
        ) * BALL_SPEED

        ball_speed_y = (
            ball_speed_y / speed
        ) * BALL_SPEED

    # ---------- BRICK COLLISION ----------

    for brick in bricks:

        if brick.colliderect(ball_rect):

            # Determine collision side

            overlap_left = ball_rect.right - brick.left
            overlap_right = brick.right - ball_rect.left

            overlap_top = ball_rect.bottom - brick.top
            overlap_bottom = brick.bottom - ball_rect.top

            min_overlap = min(
                overlap_left,
                overlap_right,
                overlap_top,
                overlap_bottom
            )

            # Horizontal collision
            if (
                min_overlap == overlap_left
                or min_overlap == overlap_right
            ):
                ball_speed_x *= -1

            # Vertical collision
            else:
                ball_speed_y *= -1

            bricks.remove(brick)

            score += 1

            # Slight speed increase
            ball_speed_x *= 1.01
            ball_speed_y *= 1.01

            break

    # ---------- WIN CONDITION ----------

    if len(bricks) == 0:

        print("YOU WIN 🔥")
        print("FINAL SCORE:", score)

        running = False

    # ---------- DRAW ----------

    screen.fill(BLACK)

    # Paddle
    pygame.draw.rect(
        screen,
        WHITE,
        paddle_rect
    )

    # Ball
    pygame.draw.circle(
        screen,
        WHITE,
        (int(ball_x), int(ball_y)),
        BALL_RADIUS
    )

    # Bricks
    for brick in bricks:

        pygame.draw.rect(
            screen,
            RED,
            brick
        )

    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
