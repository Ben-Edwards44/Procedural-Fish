import vector


class Boid:
    ALIGN_MAG = 0.1
    COHESION_MAG = 0.3
    SEPERATION_MAG = 0.1

    MAX_ACC = 0.001
    SPEED = 0.2

    def __init__(self, pos, view_radius):
        self.pos = pos
        self.view_radius_sq = view_radius * view_radius

        self.all_boids = []  #set after all boids initialised

        self.new_vel = vector.Vec2(0, 0)
        self.vel = vector.rand_vec(-1, 1)

    def get_neighbours(self):
        neighbours = []
        for i in self.all_boids:
            if i == self:
                continue

            dist_sq = (i.pos - self.pos).mag_sq()

            if dist_sq < self.view_radius_sq:
                neighbours.append(i)

        return neighbours
    
    def alignment(self, neighbours):
        #align velocity with average velocity of neighbours
        total_vel = vector.Vec2(0, 0)
        for i in neighbours:
            total_vel = total_vel + i.vel

        desired_vel = total_vel / len(neighbours)
        vel_step = desired_vel - self.vel

        return vel_step.set_mag(Boid.ALIGN_MAG)
    
    def cohesion(self, neighbours):
        #steer to average position of neighbours
        sum_pos = vector.Vec2(0, 0)
        for i in neighbours:
            sum_pos = sum_pos + i.pos

        desired_pos = sum_pos / len(neighbours)
        desired_vel = desired_pos - self.pos
        vel_step = desired_vel - self.vel

        return vel_step.set_mag(Boid.COHESION_MAG)
    
    def seperation(self, neighbours):
        #steer to avoid close neighbours
        away_dir = vector.Vec2(0, 0)
        for i in neighbours:
            away_from_boid = self.pos - i.pos
            scaled_mag = 1 / away_from_boid.mag()
            away_dir = away_dir + away_from_boid.set_mag(scaled_mag)

        return away_dir.set_mag(Boid.SEPERATION_MAG)
    
    def update_new_vel(self):
        neighbours = self.get_neighbours()

        if len(neighbours) == 0:
            return

        #TODO: experiment with limit_mag not set_mag!!!!
        align_step = self.alignment(neighbours)
        cohesion_step = self.cohesion(neighbours)
        seperation_step = self.seperation(neighbours)

        acc = (align_step + cohesion_step + seperation_step).limit_mag(Boid.MAX_ACC)

        self.new_vel = (self.vel + acc).set_mag(Boid.SPEED)

    def update(self):
        self.vel = self.new_vel
        self.pos = self.pos + self.vel


def set_all_boids(all_boids):
    for i in all_boids:
        i.all_boids = all_boids


def update_all_boids(all_boids):
    for i in all_boids:
        i.update_new_vel()

    for i in all_boids:
        i.update()