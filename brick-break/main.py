import pygame

pygame.init()

# SETTINGS

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 760
FPS = 60

PADDLE_WIDTH = 120
PADDLE_HEIGHT = 20
PADDLE_SPEED = 8

BRICK_WIDTH = 100
BRICK_HEIGHT = 30
BRICK_ROWS = 5
BRICK_COLS = 10
BRICK_PADDING = 10
BRICK_OFFSET_TOP = 50
BRICK_OFFSET_LEFT = (SCREEN_WIDTH - (BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING))) // 2

# WINDOW

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Brick Breaker")
clock = pygame.time.Clock()

# PADDLE

paddle_x = SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2
paddle_y = SCREEN_HEIGHT - 50

# BALL

BALL_RADIUS = 12
ball_x = SCREEN_WIDTH // 2
ball_y = SCREEN_HEIGHT // 2
ball_speed_x = 5
ball_speed_y = 5

# BRICKS 
bricks = []
for row in range(BRICK_ROWS):
    for col in range(BRICK_COLS):
        brick_x = BRICK_OFFSET_LEFT + col * (BRICK_WIDTH + BRICK_PADDING)
        brick_y = BRICK_OFFSET_TOP + row * (BRICK_HEIGHT + BRICK_PADDING)
        bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))

score = 0
        
# GAME LOOP
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        paddle_x -= PADDLE_SPEED
    if keys[pygame.K_RIGHT]:
        paddle_x += PADDLE_SPEED

    if paddle_x < 0:
        paddle_x = 0
    if paddle_x + PADDLE_WIDTH > SCREEN_WIDTH:
        paddle_x = SCREEN_WIDTH - PADDLE_WIDTH

    ball_x += ball_speed_x
    ball_y += ball_speed_y


    if ball_x - BALL_RADIUS <= 0:
        ball_speed_x *= -1

    if ball_x + BALL_RADIUS >= SCREEN_WIDTH:
        ball_speed_x *= -1

    if ball_y - BALL_RADIUS <= 0:
        ball_speed_y *= -1

    if ball_y + BALL_RADIUS >= SCREEN_HEIGHT:
        print("Game Over! Your score:", score)
        running = False

    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)

    if paddle_rect.colliderect(ball_rect) and ball_speed_y > 0:
        ball_speed_y *= -1
        ball_y = paddle_y - BALL_RADIUS

    for brick in bricks:
        if brick.colliderect(ball_rect):
            bricks.remove(brick)
            ball_speed_y *= -1
            score += 1
            break
    
    if len(bricks) == 0:
        print("Congratulations! You won! Your score:", score)
        running = False

    screen.fill("black")
    pygame.draw.rect(screen, "white", (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(screen, "white", (ball_x, ball_y), BALL_RADIUS)
    for brick in bricks:
        pygame.draw.rect(screen, "red", brick)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
