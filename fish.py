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


class Eyes:
    LENGTH_RATIO = 0.6

    ANGLE = math.pi / 3

    COLOUR = (0, 0, 255)

    RADIUS = 2

    def __init__(self, window, head_point, first_trail_point):
        self.window = window
        self.head_point = head_point
        self.first_trail_point = first_trail_point

        self.dist_along = self.first_trail_point.size * Eyes.LENGTH_RATIO

    def get_pos(self):
        pointing_dir = self.first_trail_point.get_direction()
        scaled_vec = pointing_dir.set_mag(self.dist_along)

        eye_pos1 = self.head_point.pos + scaled_vec.rot(Eyes.ANGLE)
        eye_pos2 = self.head_point.pos + scaled_vec.rot(-Eyes.ANGLE)

        return eye_pos1, eye_pos2
    
    def draw(self):
        pos1, pos2 = self.get_pos()

        pygame.draw.circle(self.window, Eyes.COLOUR, pos1.get_int_pos(), Eyes.RADIUS)
        pygame.draw.circle(self.window, Eyes.COLOUR, pos2.get_int_pos(), Eyes.RADIUS)


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
    NUM_T_STEPS = 20
    T_STEP = math.pi * 1.5 / NUM_T_STEPS

    COLOUR = (200, 0, 0)

    ANGLE_OFFSET = math.radians(60)

    A = 10
    B = 5

    def __init__(self, window, anchor_point, rotation_point, positive_rot):
        self.window = window
        self.anchor_point = anchor_point
        self.rotation_point = rotation_point  #should be the point in front of the anchor point
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
        rot_point_angle = self.rotation_point.get_direction().get_angle_above_x_axis()

        if not self.positive_rot:
            rot_angle = rot_point_angle + BodyFin.ANGLE_OFFSET
        else:
            rot_angle = rot_point_angle - BodyFin.ANGLE_OFFSET

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


class DorsalFin:
    COLOUR = (200, 200, 0)

    CONST_PROPORTIONALITY = 30

    NUM_BEZIER_STEPS = 10
    STEP_SIZE = 1 / NUM_BEZIER_STEPS

    MAX_MULT = 2

    def __init__(self, window, start_inx, mid_inx, end_inx, body):
        self.window = window
        self.start_inx = start_inx
        self.end_inx = end_inx

        self.mid_point = body.trail_points[mid_inx]
        self.trail_points = body.trail_points[self.start_inx : self.end_inx + 1]

    def lerp(self, a, b, t):
        return a + (b - a) * t
    
    def bezier_curve(self, points, t):
        if len(points) == 1:
            return points[0]
        
        lerped_points = []
        for i, x in enumerate(points):
            if i == 0:
                continue

            new_point = self.lerp(points[i - 1], x, t)
            lerped_points.append(new_point)

        return self.bezier_curve(lerped_points, t)
    
    def get_total_curvature(self):
        total_angle = 0
        prev_dir = self.trail_points[0].get_direction()
        for i in self.trail_points[1:]:
            new_dir = i.get_direction()
            total_angle += new_dir.get_signed_angle_to(prev_dir)
            prev_dir = new_dir

        num_angles = len(self.trail_points) - 1
        avg_angle = total_angle / num_angles

        normalised = avg_angle / math.pi

        return normalised

    def get_body_points(self):
        return [i.pos.get_int_pos() for i in self.trail_points]
    
    def get_outside_points(self):
        curvature = self.get_total_curvature()

        mult = abs(curvature) * DorsalFin.CONST_PROPORTIONALITY
        mult = min(mult, DorsalFin.MAX_MULT)

        outside_point = self.mid_point.get_outside_point(curvature > 0)
        scaled_vec = (outside_point - self.mid_point.pos) * mult
        apex = self.mid_point.pos + scaled_vec

        bezier_points = [self.trail_points[0].pos, apex, self.trail_points[-1].pos]

        outside_points = []
        for i in range(DorsalFin.NUM_BEZIER_STEPS):
            t = i * DorsalFin.STEP_SIZE
            point_on_bezier = self.bezier_curve(bezier_points, t)
            outside_points.append(point_on_bezier.get_int_pos())

        return outside_points
    
    def draw(self):
        body_points = self.get_body_points()
        outside_points = self.get_outside_points()

        pygame.draw.polygon(self.window, DorsalFin.COLOUR, body_points + outside_points[::-1])


class Fish:
    SIZES = [6, 7, 7.5, 7.5, 7.25, 7, 6.5, 6, 5.5, 5, 4, 3, 2, 1]
    LENGTH = 64

    BODY_FIN_ANCHOR_INX = 2

    DORSAL_FIN_START_INX = 3
    DORSAL_FIN_END_INX = 8
    DORSAL_FIN_MID_INX = (DORSAL_FIN_START_INX + DORSAL_FIN_END_INX) // 2

    DEFAULT_COLOUR = (255, 255, 255)

    def __init__(self, window, pos):
        self.window = window

        self.colour = Fish.DEFAULT_COLOUR

        self.head_point = self.create_head_point(pos)
        self.body = self.create_body()
        self.tail_fin = self.create_tail_fin()
        self.left_fin, self.right_fin = self.create_body_fins()
        self.eyes = self.create_eyes()
        self.dorsal_fin = self.create_dorsal_fin()

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
        rotation = self.body.trail_points[Fish.BODY_FIN_ANCHOR_INX - 1]

        left_fin = BodyFin(self.window, anchor, rotation, False)
        right_fin = BodyFin(self.window, anchor, rotation, True)

        return left_fin, right_fin
    
    def create_eyes(self):
        eyes = Eyes(self.window, self.head_point, self.body.trail_points[0])

        return eyes
    
    def create_dorsal_fin(self):
        dorsal_fin = DorsalFin(self.window, Fish.DORSAL_FIN_START_INX, Fish.DORSAL_FIN_MID_INX, Fish.DORSAL_FIN_END_INX, self.body)

        return dorsal_fin

    def draw_head(self):
        radius = Fish.SIZES[0]

        pygame.draw.circle(self.window, self.colour, self.head_point.pos.get_int_pos(), radius)

    def draw(self):
        self.draw_head()
        self.tail_fin.draw()
        self.left_fin.draw()
        self.right_fin.draw()
        self.body.draw()
        self.dorsal_fin.draw()
        self.eyes.draw()

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