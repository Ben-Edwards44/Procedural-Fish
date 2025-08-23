import math
from random import uniform


EPSILON = 0.001


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"<{self.x}, {self.y}>"

    def __add__(self, other_vec):
        return Vec2(self.x + other_vec.x, self.y + other_vec.y)
    
    def __sub__(self, other_vec):
        return Vec2(self.x - other_vec.x, self.y - other_vec.y)
    
    def __mul__(self, scalar):
        return Vec2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vec2(self.x / scalar, self.y / scalar)
    
    def __eq__(self, other_vec):
        return self.x == other_vec.x and self.y == other_vec.y
    
    def dot(self, other_vec):
        return self.x * other_vec.x + self.y * other_vec.y
    
    def get_int_pos(self):
        return (int(self.x), int(self.y))

    def mag_sq(self):
        return self.x * self.x + self.y * self.y

    def mag(self):
        return math.sqrt(self.mag_sq())
    
    def set_mag(self, desired_mag):
        scale = desired_mag / self.mag()
        new_vec = self * scale

        return new_vec
    
    def limit_mag(self, limit):
        if self.mag() > limit:
            return self.set_mag(limit)
        else:
            return self
       
    def get_angle_above_x_axis(self):
        return math.atan2(self.y, self.x)
    
    def get_angle_to(self, other_vec):
        cos_angle = self.dot(other_vec) / (self.mag() * other_vec.mag())

        #floating point imprecision can lead to cos being outside the correct range
        cos_angle = max(-1, cos_angle)
        cos_angle = min(1, cos_angle)
        
        return math.acos(cos_angle)
    
    def get_signed_angle_to(self, other_vec):
        #anticlockwise is positive and clockwise is negative
        abs_angle = self.get_angle_to(other_vec)
        perp_vec = self.rot90(False)

        if perp_vec.dot(other_vec) > 0:
            mult = 1
        else:
            mult = -1

        return abs_angle * mult

    def rot90(self, positive):
        if positive:
            mult = 1
        else:
            mult = -1

        new_x = -self.y * mult
        new_y = self.x * mult

        return Vec2(new_x, new_y)
    
    def rot(self, angle):
        c = math.cos(angle)
        s = math.sin(angle)

        new_x = self.x * c - self.y * s
        new_y = self.x * s + self.y * c

        return Vec2(new_x, new_y)
    

def rand_vec(min, max):
    x = uniform(min, max)
    y = uniform(min, max)

    return Vec2(x, y)