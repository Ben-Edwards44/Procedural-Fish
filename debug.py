import boid
import vector
import pygame


FPS = 120


pygame.init()
window = pygame.display.set_mode((500, 500))


def boid_debug():
    boids = [boid.Boid(vector.rand_vec(0, 500), 500, 500) for _ in range(40)]
    boid.set_all_boids(boids)

    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)
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


if __name__ == "__main__":
    boid_debug()