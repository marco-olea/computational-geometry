from geometry.point import Point
from typing import List, Tuple, Callable


def upper_common_tangent(hull_1: List[Point], hull_2: List[Point]) -> Tuple[int, int]:
    def find_tangent_point(pivot: Point, begin: int, end: int, polygon: List[Point],
                           comp_1: Callable[[float, float], bool],
                           comp_2: Callable[[float, float], bool]) -> int:
        t_point = begin + (end - begin) // 2
        m = (polygon[t_point].y - pivot.y) / (polygon[t_point].x - pivot.x)
        b = pivot.y - m * pivot.x
        if t_point - 1 >= 0 and comp_1(polygon[t_point - 1].y, m * polygon[t_point - 1].x + b):
            return find_tangent_point(pivot, begin, t_point, polygon, comp_1, comp_2)
        if (t_point + 1 < len(polygon)
                and comp_2(polygon[t_point + 1].y, m * polygon[t_point + 1].x + b)):
            return find_tangent_point(pivot, t_point + 1, end, polygon, comp_1, comp_2)
        return t_point
    t_point_2 = find_tangent_point(hull_1[len(hull_1) // 2], 0, len(hull_2), hull_2,
                                   lambda w, z: w > z, lambda w, z: w >= z)
    t_point_1 = find_tangent_point(hull_2[t_point_2], 0, len(hull_1), hull_1,
                                   lambda w, z: w >= z, lambda w, z: w > z)
    return t_point_1, t_point_2


def lower_common_tangent(hull_1: List[Point], hull_2: List[Point]) -> Tuple[int, int]:
    def find_tangent_point(pivot: Point, begin: int, end: int, polygon: List[Point],
                           comp_1: Callable[[float, float], bool],
                           comp_2: Callable[[float, float], bool]) -> int:
        t_point = begin + (end - begin) // 2
        m = (polygon[t_point].y - pivot.y) / (polygon[t_point].x - pivot.x)
        b = pivot.y - m * pivot.x
        if t_point - 1 >= 0 and comp_1(polygon[t_point - 1].y, m * polygon[t_point - 1].x + b):
            return find_tangent_point(pivot, begin, t_point, polygon, comp_1, comp_2)
        if (t_point + 1 < len(polygon)
                and comp_2(polygon[t_point + 1].y, m * polygon[t_point + 1].x + b)):
            return find_tangent_point(pivot, t_point + 1, end, polygon, comp_1, comp_2)
        return t_point
    t_point_2 = find_tangent_point(hull_1[len(hull_1) // 2], 0, len(hull_2), hull_2,
                                   lambda w, z: w <= z, lambda w, z: w < z)
    t_point_1 = find_tangent_point(hull_2[t_point_2], 0, len(hull_1), hull_1,
                                   lambda w, z: w < z, lambda w, z: w <= z)
    return t_point_1, t_point_2
        

def upper_hull(points: List[Point]) -> List[Point]:
    n = len(points)
    if n in [0, 1, 2]:
        return points
    # if n in [3, 4]:
    #     hull = [p for p in points[1:-1] if p.y > points[0].y]
    #     return [points[0]] + hull + [points[-1]]
    upper_hull_1 = upper_hull(points[:n // 2])
    upper_hull_2 = upper_hull(points[n // 2:])
    # Determine the upper common tangent of the upper hulls.
    q1, q2 = upper_common_tangent(upper_hull_1, upper_hull_2)
    return upper_hull_1[:q1 + 1] + upper_hull_2[q2:]


def lower_hull(points: List[Point]) -> List[Point]:
    n = len(points)
    if n <= 2:
        return points
    # if n in [3, 4]:
    #     hull = [p for p in points[1:-1] if p.y <= points[0].y]
    #     return [points[0]] + hull + [points[-1]]
    lower_hull_1 = lower_hull(points[:n // 2])
    lower_hull_2 = lower_hull(points[n // 2:])
    # Determine the lower common tangent of the lower hulls.
    q1, q2 = lower_common_tangent(lower_hull_1, lower_hull_2)
    return lower_hull_1[:q1 + 1] + lower_hull_2[q2:]


def convex_hull(points: List[Point]) -> List[Point]:
    points.sort(key=lambda p: p.x)
    uh, lh = upper_hull(points), lower_hull(points)
    return uh[:-1] + lh[::-1][:-1]
        
    
# ps = [Point(4, 1), Point(1, 2), Point(2, 3), Point(3, 4), Point(6, 3.5), Point(1, 5), Point(5, 6),
#     Point(0, 0), Point(0, 7), Point(7, 7), Point(7, 0)]
# print(convex_hull(ps))