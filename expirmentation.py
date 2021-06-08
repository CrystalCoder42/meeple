import pygame

WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

if __name__ == '__main__':
    carry_on = True
    clock = pygame.time.Clock()
    pygame.init()
    screen = pygame.display.set_mode((700, 700))
    screen.fill(WHITE)
    pygame.display.set_caption("My First Game")

    while carry_on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                carry_on = False
        screen.fill(WHITE)
        # pygame.draw.ellipse(screen, RED, [55, 200, 100, 70], 0)
        pygame.draw.ellipse(screen, RED, [20, 20, 250, 100], 2)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()
