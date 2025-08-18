import vector
import pygame


class Fish:
    SIZES = [4, 5, 6, 7, 8, 7, 6, 5, 4]

    def __init__(self, window, pos):
        self.window = window
        self.pos = pos

        self.head_point = HeadPoint(window, pos, 10)
        self.trail_points = self.create_trail_points()

    def create_trail_points(self):
        #TODO: const num_points
        parent = self.head_point
        num_points = len(Fish.SIZES)

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

    def get_spine_vecs(self):
        spine_vecs = [self.head_point.pos - self.trail_points[0].pos]
        for i, x in enumerate(self.trail_points):
            if i == 0:
                continue

            spine_vecs.append(self.trail_points[i - 1].pos - x.pos)

        return spine_vecs
    
    def get_cw_acw_points(self, anchor, spine_vec, radius):
        scaled_vec = spine_vec.set_mag(radius)

        cw = anchor + scaled_vec.rot90(False)
        acw = anchor + scaled_vec.rot90(True)

        return cw, acw

    def draw_body(self):
        spine_vecs = self.get_spine_vecs()

        #add both sides of the head
        head_cw, head_acw = self.get_cw_acw_points(self.head_point.pos, spine_vecs[0], Fish.SIZES[0])

        cw_points = [head_cw.get_int_pos()]
        acw_points = [head_acw.get_int_pos()]

        for i, x in enumerate(spine_vecs):
            anchor = self.trail_points[i].pos

            cw, acw = self.get_cw_acw_points(anchor, x, Fish.SIZES[i])

            cw_points.append(cw.get_int_pos())
            acw_points.append(acw.get_int_pos())

        pygame.draw.polygon(self.window, (255, 255, 255), cw_points + acw_points[::-1])

    def draw_head(self):
        radius = Fish.SIZES[0]

        pygame.draw.circle(self.window, (255, 255, 255), self.head_point.pos.get_int_pos(), radius)

    def draw(self):
        self.draw_head()
        self.draw_body()

    def update(self):
        self.update_head()
        self.update_trail()


class PlayerFish(Fish):
    def __init__(self, window, pos):
        super().__init__(window, pos)

    def update_head(self):
        #TODO: const step mag
        mouse_pos = vector.Vec2(*pygame.mouse.get_pos())
        step_dir = mouse_pos - self.head_point.pos
        step = step_dir.set_mag(0.5)

        self.head_point.pos = self.head_point.pos + step


class HeadPoint:
    def __init__(self, window, pos, radius):
        self.window = window

        self.pos = pos
        self.radius = radius

    def debug_draw(self):
        center = self.pos.get_int_pos()

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

    def debug_draw(self):
        center = self.pos.get_int_pos()

        pygame.draw.circle(self.window, (0, 255, 0), center, 4)