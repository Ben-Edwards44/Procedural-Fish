import vector
import pygame


class Fish:
    def __init__(self, window, pos):
        self.window = window
        self.pos = pos

        self.head_point = HeadPoint(window, pos, 10)
        self.trail_points = self.create_trail_points()

    def create_trail_points(self):
        parent = self.head_point
        num_points = 10

        trail_points = []
        for i in range(num_points):
            offset = vector.Vec2(-(i + 1) * self.head_point.radius, 0)
            new_point = TrailPoint(self.window, self.pos + offset, self.head_point.radius, parent)
            trail_points.append(new_point)

            parent = new_point

        return trail_points
    
    def update_trail(self):
        for i in self.trail_points:
            i.update_pos()

    def draw(self):
        self.head_point.draw()

        for i in self.trail_points:
            i.draw()

    def update(self):
        self.update_head()
        self.update_trail()


class PlayerFish(Fish):
    def __init__(self, window, pos):
        super().__init__(window, pos)

    def update_head(self):
        mouse_pos = vector.Vec2(*pygame.mouse.get_pos())
        step_dir = mouse_pos - self.head_point.pos
        step = step_dir.set_mag(0.5)

        self.head_point.pos = self.head_point.pos + step


class HeadPoint:
    def __init__(self, window, pos, radius):
        self.window = window

        self.pos = pos
        self.radius = radius

    def draw(self):
        center = (int(self.pos.x), int(self.pos.y))

        pygame.draw.circle(self.window, (255, 0, 0), center, 4)


class TrailPoint(HeadPoint):
    def __init__(self, window, pos, radius, parent):
        self.parent = parent

        super().__init__(window, pos, radius)

    def update_pos(self):
        vec_to_parent = self.parent.pos - self.pos
        step_length = vec_to_parent.mag() - self.parent.radius
        step = vec_to_parent.set_mag(step_length)

        self.pos = self.pos + step

    def draw(self):
        center = (int(self.pos.x), int(self.pos.y))

        pygame.draw.circle(self.window, (0, 255, 0), center, 4)