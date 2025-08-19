import fish
import vector
import pygame


SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500

FPS = 60


pygame.init()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))


def update(player_fish, non_player_fish):
    player_fish.update()
    fish.update_all_non_player_fish(non_player_fish)


def draw(player_fish, non_player_fish):
    window.fill((0, 0, 0))

    for i in non_player_fish:
        i.draw()

    player_fish.draw()

    pygame.display.update()


def main():
    player_fish = fish.PlayerFish(window, vector.Vec2(250, 250))
    non_player_fish = fish.create_non_player_fish(window, 30, player_fish)

    clock = pygame.time.Clock()
    while True:
        clock.tick(FPS)

        update(player_fish, non_player_fish)
        draw(player_fish, non_player_fish)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                quit()


if __name__ == "__main__":
    main()