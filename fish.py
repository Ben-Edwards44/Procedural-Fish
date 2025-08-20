import boid
import vector

import math
import pygame
from random import uniform


class HeadPoint:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class TrailPoint(HeadPoint):
    def __init__(self, size, pos, radius, parent):
        self.size = size
        self.parent = parent

        super().__init__(pos, radius)

    def get_direction(self):
        #get the direction this point is pointing in
        return self.parent.pos - self.pos
    
    def get_outside_point(self, positive_rot):
        scaled_vec = self.get_direction().set_mag(self.size)
        perp_vec = scaled_vec.rot90(positive_rot)

        return self.pos + perp_vec

    def update_pos(self):
        vec_to_parent = self.parent.pos - self.pos
        step_length = vec_to_parent.mag() - self.parent.radius
        step = vec_to_parent.set_mag(step_length)

        self.pos = self.pos + step


class TrailPointString:
    def __init__(self, window, head_point, sizes, radius, colour):
        self.window = window
        self.head_point = head_point
        self.sizes = sizes
        self.colour = colour

        self.trail_points = self.create_horizontal_points(radius)

    def create_horizontal_points(self, radius):
        parent = self.head_point

        trail_points = []
        for i in self.sizes:
            offset = vector.Vec2(-radius, 0)
            new_point = TrailPoint(i, parent.pos + offset, radius, parent)
            trail_points.append(new_point)

            parent = new_point

        return trail_points
    
    def get_head_cw_acw_points(self):
        pointing_dir = self.trail_points[0].get_direction()

        scaled_vec = pointing_dir.set_mag(self.sizes[0])

        cw = self.head_point.pos + scaled_vec.rot90(False)
        acw = self.head_point.pos + scaled_vec.rot90(True)

        return cw, acw

    def draw(self):
        head_cw, head_acw = self.get_head_cw_acw_points()

        #add both sides of the head
        cw_points = [head_cw.get_int_pos()]
        acw_points = [head_acw.get_int_pos()]

        for i in self.trail_points:
            cw = i.get_outside_point(False)
            acw = i.get_outside_point(True)

            cw_points.append(cw.get_int_pos())
            acw_points.append(acw.get_int_pos())

        pygame.draw.polygon(self.window, self.colour, cw_points + acw_points[::-1])

    def update(self):
        for i in self.trail_points:
            i.update_pos()


class TailFin:
    SIZES = [1, 1.5, 2, 2.5]
    LENGTH_RATIO = 0.2

    COLOUR = (0, 0, 255)

    def __init__(self, window, head_point):
        self.window = window
        self.head_point = head_point

        self.fin_points = self.create_fin_points()

    def get_point_radius(self):
        total_length = TailFin.LENGTH_RATIO * Fish.LENGTH
        num_radii = len(TailFin.SIZES)

        return total_length / num_radii

    def create_fin_points(self):
        radius = self.get_point_radius()
        point_string = TrailPointString(self.window, self.head_point, TailFin.SIZES, radius, TailFin.COLOUR)

        return point_string
    
    def update(self):
        self.fin_points.update()

    def draw(self):
        self.fin_points.draw()


class BodyFin:
    NUM_T_STEPS = 50
    T_STEP = math.pi / NUM_T_STEPS

    COLOUR = (0, 255, 0)

    ANGLE_OFFSET = math.radians(60)

    A = 10
    B = 5

    def __init__(self, window, anchor_point, positive_rot):
        self.window = window
        self.anchor_point = anchor_point
        self.positive_rot = positive_rot

        self.ellipse_points = self.get_ellipse_points()

    def get_ellipse_points(self):
        ellipse_points = []
        for i in range(BodyFin.NUM_T_STEPS):
            t = math.pi / 2 + BodyFin.T_STEP * i
            ellipse_points.append(vector.Vec2(BodyFin.A * math.cos(t), BodyFin.B * math.sin(t)))

        return ellipse_points
    
    def transform_ellipse_points(self):
        anchor_pos = self.anchor_point.get_outside_point(self.positive_rot)
        anchor_angle = self.anchor_point.get_direction().get_angle_above_x_axis()

        if not self.positive_rot:
            rot_angle = anchor_angle + BodyFin.ANGLE_OFFSET
        else:
            rot_angle = anchor_angle - BodyFin.ANGLE_OFFSET

        transformed = []
        for i in self.ellipse_points:
            rotated = i.rot(rot_angle)
            translated = rotated + anchor_pos

            transformed.append(translated)

        return transformed
    
    def draw(self):
        vector_points = self.transform_ellipse_points()
        coord_points = [i.get_int_pos() for i in vector_points]

        pygame.draw.polygon(self.window, BodyFin.COLOUR, coord_points)


class Fish:
    SIZES = [5, 5.5, 6, 5.5, 4.5, 4, 3, 2]
    LENGTH = 42

    BODY_FIN_ANCHOR_INX = 1

    DEFAULT_COLOUR = (255, 255, 255)

    def __init__(self, window, pos):
        self.window = window

        self.colour = Fish.DEFAULT_COLOUR

        self.head_point = self.create_head_point(pos)
        self.body = self.create_body()
        self.tail_fin = self.create_tail_fin()
        self.left_fin, self.right_fin = self.create_body_fins()

    def create_head_point(self, pos):
        num_radii = len(Fish.SIZES)
        head_radius = Fish.LENGTH / num_radii

        return HeadPoint(pos, head_radius)
    
    def create_body(self):
        body = TrailPointString(self.window, self.head_point, Fish.SIZES, self.head_point.radius, self.colour)

        return body
    
    def create_tail_fin(self):
        tail_fin = TailFin(self.window, self.body.trail_points[-1])

        return tail_fin
    
    def create_body_fins(self):
        anchor = self.body.trail_points[Fish.BODY_FIN_ANCHOR_INX]

        left_fin = BodyFin(self.window, anchor, False)
        right_fin = BodyFin(self.window, anchor, True)

        return left_fin, right_fin

    def draw_head(self):
        radius = Fish.SIZES[0]

        pygame.draw.circle(self.window, self.colour, self.head_point.pos.get_int_pos(), radius)

    def draw(self):
        self.draw_head()
        self.body.draw()
        self.tail_fin.draw()
        self.left_fin.draw()
        self.right_fin.draw()

    def update(self):
        self.update_head()
        self.body.update()
        self.tail_fin.update()


class PlayerFish(Fish):
    SPEED = 0.6
    COLOUR = (255, 0, 0)

    def __init__(self, window, pos):
        super().__init__(window, pos)

        self.colour = PlayerFish.COLOUR
        self.body.colour = PlayerFish.COLOUR

        self.dummy_boid = self.create_dummy_boid()

    def create_dummy_boid(self):
        #create a boid object with same pos and vel as fish so non player fish interact with player fish
        boid_obj = boid.Boid(self.head_point.pos, 0)

        return boid_obj
    
    def update_dummy_boid(self, head_step):
        #ensure dummy boids attrs match the actual fish
        self.dummy_boid.pos = self.head_point.pos
        self.dummy_boid.vel = head_step

    def update_head(self):
        mouse_pos = vector.Vec2(*pygame.mouse.get_pos())
        step_dir = mouse_pos - self.head_point.pos
        step = step_dir.set_mag(PlayerFish.SPEED)

        self.head_point.pos = self.head_point.pos + step

        self.update_dummy_boid(step)


class NonPlayerFish(Fish):
    VIEW_RADIUS = 80

    def __init__(self, window, pos):
        super().__init__(window, pos)

        self.boid = boid.Boid(pos, NonPlayerFish.VIEW_RADIUS)

    def update_head(self):
        #NOTE: this does not actually update the boid pos, this must be done with update_all_non_player_fish
        self.head_point.pos = self.boid.pos


def set_all_fish_boids(all_fish, player_fish):
    #to be called once all fish have been initialised
    boids = [i.boid for i in all_fish]
    boids.append(player_fish.dummy_boid)

    boid.set_all_boids(boids)


def create_non_player_fish(window, num, player_fish):
    width = window.get_width()
    height = window.get_height()

    all_fish = []
    for _ in range(num):
        pos_x = uniform(0, width)
        pos_y = uniform(0, height)

        fish = NonPlayerFish(window, vector.Vec2(pos_x, pos_y))
        all_fish.append(fish)

    set_all_fish_boids(all_fish, player_fish)

    return all_fish


def update_all_non_player_fish(all_fish):
    boids = [i.boid for i in all_fish]

    boid.update_all_boids(boids)

    for i in all_fish:
        i.update()