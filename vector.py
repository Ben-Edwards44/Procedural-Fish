from math import sqrt


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other_vec):
        return Vec2(self.x + other_vec.x, self.y + other_vec.y)
    
    def __sub__(self, other_vec):
        return Vec2(self.x - other_vec.x, self.y - other_vec.y)
    
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    
    def get_int_pos(self):
        return (int(self.x), int(self.y))

    def mag(self):
        return sqrt(self.x * self.x + self.y * self.y)
    
    def set_mag(self, desired_mag):
        scale = desired_mag / self.mag()
        new_vec = self * scale

        return new_vec
    
    def rot90(self, positive):
        if positive:
            mult = 1
        else:
            mult = -1

        new_x = -self.y * mult
        new_y = self.x * mult

        return Vec2(new_x, new_y)