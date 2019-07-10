from math import pi, tan
from typing import Optional


class Point:
    """Represents an element of the two-dimensional Euclidean space.
    
    Attributes:
        x: The abscissa.
        y: The ordinate.
    """
    
    def __init__(self, x: float, y: float, canvas_id: int = None):
        """Create a point with the given coordinates."""
        self.x = x
        self.y = y
        self.canvas_id = canvas_id
    
    def __str__(self):
        """Return (x, y) with this point's abscissa and ordinate."""
        return (f'{self.canvas_id}: ' if self.canvas_id else '') + f'({self.x}, {self.y})'
    
    def __mul__(self, other):
        """Compute the dot product of this point with another."""
        return self.x * other.x + self.y * other.y
    
    def __eq__(self, other):
        """Determine if the two points represent the same element in the Euclidean space."""
        return isinstance(other, type(self)) and (self.x, self.y) == (other.x, other.y)
    
    def __hash__(self):
        """Hash the coordinates and their respective order."""
        return hash(self.x) ^ hash(self.y) ^ hash((self.x, self.y))
    
    def distance_to(self, other) -> float:
        """Compute the distance from this point to another."""
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5
    
    def midpoint(self, other):
        """Return the point halfway between this point and another."""
        return Point((self.x + other.x) / 2, (self.y + other.y) / 2)


class Segment:
    """Represents a straight line with extremes on two distinct points.
    
    Attributes:
        p1: The first point.
        p2: The second point."""
    
    def __init__(self, p1: Point, p2: Point):
        """Create a segment between the two given points."""
        if p1 == p2:
            raise Exception(f'A segment cannot begin and end on the same point; {p1}.')
        self.p1 = p1
        self.p2 = p2
        
    def __eq__(self, other):
        """Determine if this segment has the same two points as another (in any order)."""
        return (isinstance(other, type(self))) and not {self.p1, self.p2} - {other.p1, other.p2}
    
    def __hash__(self):
        """Hash the two points; a segment PQ will return the same hash as QP."""
        return hash(self.p1) ^ hash(self.p2)
    
    def __str__(self):
        """Return P-Q."""
        return f'{self.p1}-{self.p2}'
    
    
class Ray:
    def __init__(self, p: Point, angle: float):
        self.p = p
        self.angle = angle
        
    def __str__(self):
        return f'({self.p}, {self.angle})'

    def __eq__(self, other):
        """Determine if this ray has the same endpoint and angle as another."""
        return (isinstance(other, type(self))) and (self.p, self.angle) == (other.p, other.angle)

    def __hash__(self):
        """Hash the endpoint and angle in that order."""
        return hash(self.p) ^ hash(self.angle) ^ hash((self.p, self.angle))
        
    def angle_in_degrees(self) -> float:
        return self.angle * 180 / pi
    

class Triangle:
    """Represents the polygon formed by three distinct points on plane."""
    
    def __init__(self, p1: Point, p2: Point, p3: Point):
        """Create a triangle with the given points."""
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3

    def __eq__(self, other):
        """Determine if this triangle has the same three points as another (in any order)."""
        return (isinstance(other, type(self))) and not (
            {self.p1, self.p2, self.p3} - {other.p1, other.p2, other.p3})

    def __hash__(self):
        """Hash the three points; triangles with any order of PQR will return the same hash."""
        return hash(self.p1) ^ hash(self.p2) ^ hash(self.p3)
    
    def __str__(self):
        """Return (p1, p2, p3) with this triangle's points."""
        return f'({self.p1}, {self.p2}, {self.p3})'
    
    def strictly_contains(self, p: Point) -> bool:
        """Return False if a point is strictly inside this triangle.

        Uses barycentric coordinates to determine if the given point is on or beyond this triangle's
        perimeter.
        Reference: https://stackoverflow.com/a/34093754.
        """
        d_x, d_y = p.x - self.p3.x, p.y - self.p3.y
        d_x_p3p2, d_y_p2p3 = self.p3.x - self.p2.x, self.p2.y - self.p3.y
        d = d_y_p2p3 * (self.p1.x - self.p3.x) + d_x_p3p2 * (self.p1.y - self.p3.y)
        s = d_y_p2p3 * d_x + d_x_p3p2 * d_y
        t = (self.p3.y - self.p1.y) * d_x + (self.p1.x - self.p3.x) * d_y
        return s < 0 and t < 0 and s + t > d if d < 0 else s > 0 and t > 0 and s + t < d
    
    def shares_point(self, other) -> bool:
        """Return True if this triangle contains a point from the given triangle."""
        points = {self.p1, self.p2, self.p3}
        return other.p1 in points or other.p2 in points or other.p3 in points


class Line:
    """Represents the general line equation Ax + By + C = 0."""
    
    def __init__(self, a: float, b: float, c: float):
        """Create a line with the given parameters."""
        self.a = a
        self.b = b
        self.c = c
        self.slope = -self.a / self.b if self.b != 0 else None
    
    def __str__(self):
        """Return Ax + By + C = 0."""
        return f'{self.a}x + {self.b}y + {self.c} = 0'
    
    @classmethod
    def from_two_points(cls, p1: Point, p2: Point):
        """Compute the line equation given two distinct points."""
        if p1 == p2:
            raise Exception(f'Points cannot be equal; {p1}.')
        if p1.x == p2.x:
            return cls(1, 0, -p1.x)
        else:
            m = (p2.y - p1.y) / (p2.x - p1.x)
            return cls(m, -1, p1.y - m * p1.x)
        
    @classmethod
    def from_ray(cls, ray: Ray):
        if ray.angle == pi / 2 or ray.angle == 3 * pi / 2:
            return Line(1, 0, -ray.p.x)
        else:
            m = tan(ray.angle)
            return Line(m, -1, ray.p.y - m * ray.p.x)
        
    def orthogonal_line(self, p: Point):
        if not self.contains(p):
            return None
        if self.a == 0:
            return Line(1, 0, -p.x)
        elif self.b == 0:
            return Line(0, 1, -p.y)
        else:
            m = -1 / self.slope
            return Line(m, -1, p.y - m * p.x)
    
    def distance_to(self, p: Point) -> float:
        """Compute the distance between a point p and the point on this line closest to p."""
        if self.a == 0:
            return abs(p.y + self.c / self.b)
        elif self.b == 0:
            return abs(p.x + self.c / self.a)
        else:
            y = ((self.slope * self.c + p.y * self.a + self.slope * p.x * self.a) / (
                        self.a - self.slope * self.b))
            x = -(self.b * y + self.c) / self.a
            return Point(x, y).distance_to(p)
    
    def is_strictly_below(self, p: Point) -> bool:
        """Determine if this line is strictly below a point.

        Note that this method returns False if the given point is on this line.
        """
        return -self.c / self.a < p.x if self.b == 0 else -(p.x * self.a + self.c) / self.b < p.y
    
    def contains(self, p: Point) -> bool:
        """Determine if a point is on this line."""
        return self.a * p.x + self.b * p.y + self.c == 0
    
    def intersection(self, other) -> Optional[Point]:
        """Compute the point at which this line intersects with another line.

        Returns None if the lines are parallel to each other."""
        if self.slope == other.slope:
            return None
        y = (self.a * other.c - other.a * self.c) / (other.a * self.b - self.a * other.b)
        line = self if self.a != 0 else other  # At least one of the 'a's is nonzero.
        return Point(-line.b * y / line.a - line.c / line.a, y)
    
    
class Circle:
    """Represents the general circle equation (x - h)^2 + (y - k)^2 = r^2."""
    
    def __init__(self, h: float, k: float, r: float):
        """Create a circle with the given parameters."""
        self.h = h
        self.k = k
        self.r = r
        
    def __str__(self):
        """Return (x - h)^2 + (y - k)^2 = r^2."""
        return f'(x - {self.h})^2 + (y - {self.k})^2 = {self.r}^2'
        
    @classmethod
    def from_triangle(cls, triangle: Triangle):
        """Computes the circle circumscribed in the given polygon.
        
        Reference: https://en.wikipedia.org/wiki/Circumscribed_circle#Cartesian_coordinates
        """
        a, b, c = triangle.p1, triangle.p2, triangle.p3
        s = Point(
            0.5 * ((a * a) * (b.y - c.y) - (b * b) * (a.y - c.y) + (c * c) * (a.y - b.y)),
            0.5 * (-(a * a) * (b.x - c.x) + (b * b) * (a.x - c.x) - (c * c) * (a.x - b.x)))
        d1 = a.x * (b.y - c.y) - b.x * (a.y - c.y) + c.x * (a.y - b.y)
        d2 = ((a * a) * (b.x * c.y - b.y * c.x) - (b * b) * (a.x * c.y - a.y * c.x)
              + (c * c) * (a.x * b.y - a.y * b.x))
        return cls(s.x / d1, s.y / d1, (d2 / d1 + (s * s) / d1**2)**0.5)
    
    def strictly_contains(self, p: Point) -> bool:
        """Determine if a point is strictly inside this circle."""
        return Point(self.h, self.k).distance_to(p) < self.r
