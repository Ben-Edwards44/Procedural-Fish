import boid
import vector
import pygame


class HeadPoint:
    def __init__(self, pos, radius):
        self.pos = pos
        self.radius = radius


class TrailPoint(HeadPoint):
    def __init__(self, pos, radius, parent):
        self.parent = parent

        super().__init__(pos, radius)

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
        for _ in self.sizes:
            offset = vector.Vec2(-radius, 0)
            new_point = TrailPoint(parent.pos + offset, radius, parent)
            trail_points.append(new_point)

            parent = new_point

        return trail_points

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

    def draw(self):
        spine_vecs = self.get_spine_vecs()

        #add both sides of the head
        head_cw, head_acw = self.get_cw_acw_points(self.head_point.pos, spine_vecs[0], self.sizes[0])

        cw_points = [head_cw.get_int_pos()]
        acw_points = [head_acw.get_int_pos()]

        for i, x in enumerate(spine_vecs):
            anchor = self.trail_points[i].pos

            cw, acw = self.get_cw_acw_points(anchor, x, self.sizes[i])

            cw_points.append(cw.get_int_pos())
            acw_points.append(acw.get_int_pos())

        pygame.draw.polygon(self.window, self.colour, cw_points + acw_points[::-1])

    def update(self):
        for i in self.trail_points:
            i.update_pos()


class TailFin:
    SIZES = [1, 1.5, 2, 2.5]
    LENGTH_RATIO = 0.2

    def __init__(self, trail_point):
        self.trail_point = trail_point

    def get_point_radius(self):
        total_length = TailFin.LENGTH_RATIO * Fish.LENGTH
        num_radii = len(TailFin.SIZES)

        return total_length / num_radii

    def create_fin_points(self):
        radius = self.get_point_radius()
        points = create_horizontal_trail_points(self.trail_point, len(TailFin.SIZES), radius)

        return points
    



class Fish:
    SIZES = [5, 5.5, 6, 5.5, 4.5, 4, 3, 2]
    LENGTH = 42

    DEFAULT_COLOUR = (255, 255, 255)

    def __init__(self, window, pos):
        self.window = window

        self.colour = Fish.DEFAULT_COLOUR

        self.head_point = self.create_head_point(pos)
        self.body = self.create_body()

    def create_head_point(self, pos):
        num_radii = len(Fish.SIZES)
        head_radius = Fish.LENGTH / num_radii

        return HeadPoint(pos, head_radius)
    
    def create_body(self):
        body = TrailPointString(self.window, self.head_point, Fish.SIZES, self.head_point.radius, self.colour)

        return body

    def draw_head(self):
        radius = Fish.SIZES[0]

        pygame.draw.circle(self.window, self.colour, self.head_point.pos.get_int_pos(), radius)

    def draw(self):
        self.draw_head()
        self.body.draw()

    def update(self):
        self.update_head()
        self.body.update()


class PlayerFish(Fish):
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
        #TODO: const step mag
        mouse_pos = vector.Vec2(*pygame.mouse.get_pos())
        step_dir = mouse_pos - self.head_point.pos
        step = step_dir.set_mag(0.5)

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
    #TODO: const min/max
    all_fish = []
    for _ in range(num):
        fish = NonPlayerFish(window, vector.rand_vec(0, 500))
        all_fish.append(fish)

    set_all_fish_boids(all_fish, player_fish)

    return all_fish


def update_all_non_player_fish(all_fish):
    boids = [i.boid for i in all_fish]

    boid.update_all_boids(boids)

    for i in all_fish:
        i.update()