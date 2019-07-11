from math import pi, atan
from typing import List, Set, Tuple
from geometry.plane import Point, Segment, Ray, Triangle, Line, Circle


def convex_hull(points: Set[Point]) -> List[Point]:
    """Compute the convex hull of a list of points in a two-dimensional space.

    This function implements the Quickhull algorithm.
    Reference: https://en.wikipedia.org/wiki/Quickhull#Algorithm.
    """
    n, hull, points_as_list = len(points), [], list(points)
    if len(points) <= 3:
        return points_as_list
    
    def find_hull(_points: Set[Point], p1: Point, p2: Point) -> None:
        if not _points:
            return
        # Construct a triangle with the furthest point as the third vertex.
        main_line = Line.from_two_points(p1, p2)
        furthest_point = max(_points, key=lambda p: main_line.distance_to(p))
        triangle = Triangle(p1, furthest_point, p2)
        # Remove triangle and points strictly inside of it.
        _points = {p for p in _points if not triangle.strictly_contains(p)} - {furthest_point}
        # Now we only need to consider one of p1-fp or p2-fp to create the partition.
        line_p1fp = Line.from_two_points(p1, furthest_point)
        s1, s2 = set(), set()
        if main_line.is_strictly_below(furthest_point):
            for p in _points:
                (s1 if line_p1fp.is_strictly_below(p) or line_p1fp.contains(p) else s2).add(p)
        else:
            for p in _points:
                (s1 if not line_p1fp.is_strictly_below(p) else s2).add(p)
        find_hull(s1, p1, furthest_point)
        hull.append(furthest_point)
        find_hull(s2, furthest_point, p2)
        
    # Find leftmost and rightmost points.
    min_x, max_x = points_as_list[0], points_as_list[n - 1]
    for i in range(n - 1):
        min_x = points_as_list[i + 1] if points_as_list[i + 1].x < min_x.x else min_x
        max_x = points_as_list[n - 2 - i] if points_as_list[n - 2 - i].x > max_x.x else max_x
    # First line that partitions the set (in two).
    line = Line.from_two_points(min_x, max_x)
    hull.append(min_x)
    find_hull({p for p in points if line.is_strictly_below(p)}, min_x, max_x)
    hull.append(max_x)
    find_hull({p for p in points if not line.is_strictly_below(p)} - {min_x, max_x}, max_x, min_x)
    return hull


def delaunay_triangulation(points: Set[Point]) -> Set[Triangle]:
    """Compute the Delaunay triangulation of a list of points in a two-dimensional space.
    
    This function implements the Bowyer-Watson algorithm.
    Reference: https://en.wikipedia.org/wiki/Bowyer-Watson_algorithm.
    """
    if len(points) <= 2:
        return set()
    min_x, max_x = min(points, key=lambda p: p.x), max(points, key=lambda p: p.x)
    min_y, max_y = min(points, key=lambda p: p.y), max(points, key=lambda p: p.y)
    super_triangle_line1 = Line.from_two_points(
        Point(min_x.x - 1, min_y.y - 1), Point(min_x.x, max_y.y + 1))
    super_triangle_line2 = Line.from_two_points(
        Point(max_x.x + 1, min_y.y - 1), Point(max_x.x, max_y.y + 1))
    super_triangle = Triangle(
        Point(min_x.x - 1, min_y.y - 1),
        Point(max_x.x + 1, min_y.y - 1),
        super_triangle_line1.intersection(super_triangle_line2))
    triangulation = {super_triangle}
    for p in points:
        bad_triangles = {
            triangle for triangle in triangulation
            if Circle.from_triangle(triangle).strictly_contains(p)}
        polygon = set()
        for triangle in bad_triangles:
            edges = [Segment(triangle.p1, triangle.p2), Segment(triangle.p2, triangle.p3),
                     Segment(triangle.p3, triangle.p1)]
            for edge in edges:
                # Use the fact that an edge can only be part of at most two triangles.
                if edge in polygon:
                    polygon.remove(edge)
                else:
                    polygon.add(edge)
        triangulation -= bad_triangles
        triangulation |= {Triangle(edge.p1, edge.p2, p) for edge in polygon}
    triangulation -= {
        triangle for triangle in triangulation if triangle.shares_vertex(super_triangle)}
    return triangulation


def voronoi_diagram(points: Set[Point]) -> Tuple[Set[Segment], Set[Ray]]:
    if len(points) <= 2:
        return set(), set()
    triangles = delaunay_triangulation(points)
    circumcenters1, circumcenters2, edge_below_point = {}, {}, {}
    for triangle in triangles:
        p1, p2, p3 = triangle.p1, triangle.p2, triangle.p3
        circumcircle = Circle.from_triangle(triangle)
        circumcenter = Point(circumcircle.h, circumcircle.k)
        edges = [Segment(p1, p2), Segment(p2, p3), Segment(p3, p1)]
        edge_below_point.update({
            edges[0]: Line.from_two_points(p1, p2).is_strictly_below(p3),
            edges[1]: Line.from_two_points(p2, p3).is_strictly_below(p1),
            edges[2]: Line.from_two_points(p3, p1).is_strictly_below(p2)})
        for edge in edges:
            try:
                _ = circumcenters1[edge]
                circumcenters2[edge] = circumcenter
            except KeyError:
                circumcenters1[edge] = circumcenter
    segments, rays = set(), set()
    for edge, point in circumcenters1.items():
        try:
            other_point = circumcenters2[edge]
            segments.add(Segment(point, other_point))
        except KeyError:
            midpoint = edge.p1.midpoint(edge.p2)
            line = Line.from_two_points(edge.p1, edge.p2).orthogonal_line(midpoint)
            if line.a == 0:
                angle = pi if edge_below_point[edge] else 0
            elif line.b == 0:
                angle = 3 * pi / 2 if edge_below_point[edge] else pi / 2
            else:
                angle = atan(line.slope) if line.slope >= 0 else pi - abs(atan(line.slope))
                angle = pi + angle if edge_below_point[edge] else angle
            rays.add(Ray(point, angle))
    return segments, rays
