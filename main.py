import fish
import boid
import vector
import pygame


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500


pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def boid_test():
    boids = [boid.Boid(vector.rand_vec(0, 500), 50) for _ in range(40)]
    boid.set_all_boids(boids)

    while True:
        boid.update_all_boids(boids)

        window.fill((0, 0, 0))
        for i in boids:
            if i.pos.x < 0:
                i.pos.x = 500
            elif i.pos.x > 500:
                i.pos.x = 0

            if i.pos.y < 0:
                i.pos.y = 500
            elif i.pos.y > 500:
                i.pos.y = 0

            pygame.draw.circle(window, (255, 255, 255), i.pos.get_int_pos(), 4)
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()


def main():
    boid_test()

    f = fish.PlayerFish(window, vector.Vec2(250, 250))

    while True:
        f.update()

        window.fill((0, 0, 0))
        f.draw()
        pygame.display.update()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()


main()