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

    def mag(self):
        return sqrt(self.x * self.x + self.y * self.y)
    
    def set_mag(self, desired_mag):
        scale = desired_mag / self.mag()
        new_vec = self * scale

        return new_vec