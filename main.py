import fish
import vector
import pygame


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def main():
    f = fish.PlayerFish(window, vector.Vec2(250, 250))

    clock = pygame.time.Clock()
    while True:
        clock.tick(120)
        f.update()

        window.fill((0, 0, 0))
        f.draw()
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()


main()