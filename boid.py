import vector
from math import pi


class Boid:
    ALIGN_MAG = 0.1
    COHESION_MAG = 0.3
    SEPERATION_MAG = 0.2
    VIEW_RADIUS_SQ = 60**2
    FOV = 2 * pi / 3  #half of the range of view

    MAX_ACC = 0.01
    SPEED = 0.6

    def __init__(self, pos):
        self.pos = pos

        self.all_boids = []  #set after all boids initialised

        self.vel = vector.rand_vec(-1, 1)
        self.new_vel = self.vel

    def get_neighbours(self):
        neighbours = []
        for i in self.all_boids:
            if i == self:
                continue

            vec_to_boid = (i.pos - self.pos)
            dist_sq = vec_to_boid.mag_sq()
            angle_to_boid = self.vel.get_angle_to(vec_to_boid)

            if dist_sq < Boid.VIEW_RADIUS_SQ and angle_to_boid < Boid.FOV:
                neighbours.append(i)

        return neighbours
    
    def alignment(self, neighbours):
        #align velocity with average velocity of neighbours
        total_vel = vector.Vec2(0, 0)
        for i in neighbours:
            total_vel = total_vel + i.vel

        desired_vel = total_vel / len(neighbours)
        vel_step = desired_vel - self.vel

        return vel_step.limit_mag(Boid.ALIGN_MAG)
    
    def cohesion(self, neighbours):
        #steer to average position of neighbours
        sum_pos = vector.Vec2(0, 0)
        for i in neighbours:
            sum_pos = sum_pos + i.pos

        desired_pos = sum_pos / len(neighbours)
        desired_vel = desired_pos - self.pos
        vel_step = desired_vel - self.vel

        return vel_step.limit_mag(Boid.COHESION_MAG)
    
    def seperation(self, neighbours):
        #steer to avoid close neighbours
        away_dir = vector.Vec2(0, 0)
        for i in neighbours:
            away_from_boid = self.pos - i.pos
            scaled_mag = 1 / away_from_boid.mag()
            away_dir = away_dir + away_from_boid.set_mag(scaled_mag)

        return away_dir.limit_mag(Boid.SEPERATION_MAG)
    
    def update_new_vel(self):
        neighbours = self.get_neighbours()

        if len(neighbours) == 0:
            return

        align_step = self.alignment(neighbours)
        cohesion_step = self.cohesion(neighbours)
        seperation_step = self.seperation(neighbours)

        acc = (align_step + cohesion_step + seperation_step).limit_mag(Boid.MAX_ACC)

        self.new_vel = (self.vel + acc).set_mag(Boid.SPEED)

    def update(self):
        self.vel = self.new_vel
        self.pos = self.pos + self.vel

        #TODO: use consts
        o = 80
        if self.pos.x < -o:
            self.pos.x = 500 + o
        elif self.pos.x > 500 + o:
            self.pos.x = -o

        if self.pos.y < -o:
            self.pos.y = 500 + o
        elif self.pos.y > 500 + o:
            self.pos.y = -o


def set_all_boids(all_boids):
    for i in all_boids:
        i.all_boids = all_boids


def update_all_boids(all_boids):
    for i in all_boids:
        i.update_new_vel()

    for i in all_boids:
        i.update()