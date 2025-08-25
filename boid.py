import vector
from math import pi


EPSILON = 0.001


class Boid:
    ALIGN_MAG = 0.1
    COHESION_MAG = 0.3
    SEPERATION_MAG = 0.25

    VIEW_RADIUS = 80
    VIEW_RADIUS_SQ = VIEW_RADIUS**2
    FOV = 2 * pi / 3  #half of the range of view

    WALL_DIST_RATIO = 0.1

    WALL_AVOID_CONST = 1
    PLAYER_AVOID_CONST = 0.1

    MAX_ACC = 0.01
    SPEED = 0.8

    def __init__(self, pos, screen_width, screen_height, player_boid, initial_vel):
        self.pos = pos
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.player_boid = player_boid

        self.vel = initial_vel
        self.new_vel = initial_vel

        self.width_threshold = screen_width * Boid.WALL_DIST_RATIO
        self.height_threshold = screen_height * Boid.WALL_DIST_RATIO

        self.num_grid_x = screen_width // Boid.VIEW_RADIUS + 1
        self.num_grid_y = screen_height // Boid.VIEW_RADIUS + 1

        self.grid = []  #set after all boids initialised

        self.grid_pos = self.get_grid_pos()

    def get_grid_pos(self):
        grid_x = int(self.pos.x / Boid.VIEW_RADIUS)
        grid_y = int(self.pos.y / Boid.VIEW_RADIUS)

        return vector.Vec2(grid_x, grid_y)
    
    def add_to_grid_cell(self, new_grid_pos):
        new_cell = self.grid[new_grid_pos.x][new_grid_pos.y]
        new_cell.append(self)  #add to new cell

        self.grid_pos = new_grid_pos

    def init_grid(self, grid):
        #to be called once all boids initialised
        self.grid = grid
        grid_pos = self.get_grid_pos()

        self.add_to_grid_cell(grid_pos)

    def is_neighbour(self, other_boid):
        if other_boid == self or other_boid == self.player_boid:
            return False

        vec_to_boid = (other_boid.pos - self.pos)
        dist_sq = vec_to_boid.mag_sq()
        angle_to_boid = self.vel.get_angle_to(vec_to_boid)

        return dist_sq < Boid.VIEW_RADIUS_SQ and angle_to_boid < Boid.FOV
    
    def get_neighbours(self):
        neighbours = []
        for i in range(-1, 2):
            cell_x = self.grid_pos.x + i
            if not 0 <= cell_x < self.num_grid_x:
                continue

            for x in range(-1, 2):
                cell_y = self.grid_pos.y + x
                if not 0 <= cell_y < self.num_grid_y:
                    continue

                for boid in self.grid[cell_x][cell_y]:
                    if self.is_neighbour(boid):
                        neighbours.append(boid)

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
    
    def get_avoid_vec(self, dist, direction):
        mult = Boid.WALL_AVOID_CONST / dist
        acc_vec = direction * mult

        return acc_vec

    def avoid_walls(self):
        #steer away from the edge of the screen
        dist_left = max(self.pos.x, EPSILON)
        dist_right = max(self.screen_width - self.pos.x, EPSILON)

        acc_x = vector.Vec2(0, 0)
        if dist_left < self.width_threshold:
            acc_x = self.get_avoid_vec(dist_left, vector.Vec2(1, 0))
        elif dist_right < self.width_threshold:
            acc_x = self.get_avoid_vec(dist_right, vector.Vec2(-1, 0))

        dist_up = max(self.pos.y, EPSILON)
        dist_down = max(self.screen_height - self.pos.y, EPSILON)

        acc_y = vector.Vec2(0, 0)
        if dist_up < self.height_threshold:
            acc_y = self.get_avoid_vec(dist_up, vector.Vec2(0, 1))
        elif dist_down < self.height_threshold:
            acc_y = self.get_avoid_vec(dist_down, vector.Vec2(0, -1))

        return acc_x + acc_y
    
    def avoid_player(self):
        vec_to_player = self.player_boid.pos - self.pos

        avoid_vec = vector.Vec2(0, 0)
        if vec_to_player.mag_sq() < Boid.VIEW_RADIUS_SQ:
            mult = Boid.PLAYER_AVOID_CONST / vec_to_player.mag()
            avoid_vec = vec_to_player * -mult

        return avoid_vec
    
    def update_new_vel(self):
        neighbours = self.get_neighbours()

        acc = vector.Vec2(0, 0)
        if len(neighbours) > 0:
            align_step = self.alignment(neighbours)
            cohesion_step = self.cohesion(neighbours)
            seperation_step = self.seperation(neighbours)

            acc = (align_step + cohesion_step + seperation_step).limit_mag(Boid.MAX_ACC)

        acc = acc + self.avoid_walls() + self.avoid_player()

        self.new_vel = (self.vel + acc).set_mag(Boid.SPEED)

    def update_grid_pos(self):
        #check if this boid has moved to a new grid cell
        new_grid_pos = self.get_grid_pos()
        if new_grid_pos != self.grid_pos:
            self.grid[self.grid_pos.x][self.grid_pos.y].remove(self)  #remove from old cell
            self.add_to_grid_cell(new_grid_pos)

    def update(self):
        self.vel = self.new_vel
        self.pos = self.pos + self.vel

        self.update_grid_pos()


def set_all_boids(all_boids):
    grid = [[[] for _ in range(all_boids[0].num_grid_y)] for _ in range(all_boids[0].num_grid_x)]

    for i in all_boids:
        i.init_grid(grid)


def update_all_boids(all_boids):
    for i in all_boids:
        i.update_new_vel()

    for i in all_boids:
        i.update()