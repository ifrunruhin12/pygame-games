import pygame
import random

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

CELL_SIZE = 20

BLACK = (0, 0, 0)
RED = (255, 0, 0)

FPS = 10

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

def snake_game():
    pygame.display.set_caption("Snake Game")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    clock = pygame.time.Clock()

    snake = [
        [100, 100],
        [80, 100],
        [60, 100]
    ]

    food = [
        random.randrange(0, SCREEN_WIDTH, CELL_SIZE),
        random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)
    ]

    direction = RIGHT

    running = True



    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_UP and direction != DOWN:
                    direction = UP
                elif event.key == pygame.K_DOWN and direction != UP:
                    direction = DOWN
                elif event.key == pygame.K_LEFT and direction != RIGHT:
                    direction = LEFT
                elif event.key == pygame.K_RIGHT and direction != LEFT:
                    direction = RIGHT

        head_x = snake[0][0]
        head_y = snake[0][1]

        head_x += direction[0] * CELL_SIZE
        head_y += direction[1] * CELL_SIZE

        new_head = [head_x, head_y]
        snake.insert(0, new_head)

        if snake[0] == food:
            food = [random.randrange(0, SCREEN_WIDTH, CELL_SIZE),
                    random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)]
        else:
            snake.pop()

        screen.fill(BLACK)


        for segment in snake:
            pygame.draw.rect(
                screen,
                RED,
                (segment[0], segment[1], CELL_SIZE, CELL_SIZE)
            )
        pygame.draw.rect(
            screen,
            (0, 255, 0),
            (food[0], food[1], CELL_SIZE, CELL_SIZE)
        )

        if (head_x < 0 or head_x >= SCREEN_WIDTH or head_y < 0 or head_y >= SCREEN_HEIGHT or new_head in snake[1:]):
            game_over(screen)
            running = False

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()

def game_over(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))

    screen.blit(overlay, (0, 0))

    pygame.display.flip()
    pygame.time.wait(2000)

def main():
    snake_game()


if __name__ == '__main__':
    main()
