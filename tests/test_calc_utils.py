from math import pi, sqrt
import pytest
from bcam import calc_utils


# Test AABB.
@pytest.mark.parametrize('box, point, expected', [
    ([1, 2, 3, 4], [0, 0], False),
    ([1, 2, 3, 4], [1, 2], True),
    ([1, 2, 3, 4], [1.5, 2.5], True),
    ([1, 2, 3, 4], [1, 3], True),
    ([1, 2, 3, 4], [1, 4], True),
    ([1, 2, 3, 4], [1, 4.1], False),
    ([1, 2, 3, 4], [1.5, 2], True),
    ([1, 2, 3, 4], [3.5, 2], False),
    ([1.1, 2.1, 3.1, 4.1], [3, 2], False),
    ([1.1, 2.1, 3.1, 4.1], [3, 3], True),
])
def test_point_in(box, point, expected):
    aabb = calc_utils.AABB(*box)
    assert aabb.point_in_aabb(point) == expected

OE = calc_utils.OverlapEnum
@pytest.mark.parametrize('box1, box2, check_inside, expected', [
    ([1, 2, 3, 4], [0, 0, 1, 1], True, OE.no_overlap),
    ([1, 2, 3, 4], [1.1, 2.1, 2.9, 3.9], True, OE.fully_covers),
    ([1.1, 2.1, 2.9, 3.9], [1, 2, 3, 4], True, OE.fully_lays_inside),
    ([1.1, 2.1, 2.9, 3.9], [1, 2, 3, 4], False, OE.no_overlap),
    ([1, 2, 3, 4], [0, 0, 1.1, 2.1], True, OE.partially_overlap),
    ([1, 2, 3, 4], [1, 2, 3, 4], True, OE.fully_covers),
    ([1, 2, 3, 4], [1, 2, 5, 6], True, OE.fully_lays_inside),
    ([1, 2, 3, 4], [1, 2, 5, 6], False, OE.partially_overlap),
])
def test_aabb_in(box1, box2, check_inside, expected):
    aabb1 = calc_utils.AABB(*box1)
    aabb2 = calc_utils.AABB(*box2)
    assert aabb1.aabb_in_aabb(aabb2, check_inside) == expected


# Test CircleUtils.
@pytest.mark.parametrize('center, radius, box', [
    ([0, 0], 1, [-1, 1, 1, -1]),
    ([1.3, -2.7], 33, [-31.7, 34.3, 30.3, -35.7]),
])
def test_circle_get_aabb(center, radius, box):
    aabb = calc_utils.CircleUtils(center, radius).get_aabb()
    assert aabb.left == box[0]
    assert aabb.right == box[1]
    assert aabb.top == box[2]
    assert aabb.bottom == box[3]

@pytest.mark.parametrize('center, radius, inner_space, pt, distance', [
    ([0, 0], 1, False, [0, 0], 1),
    ([0, 0], 1, True, [0, 0], 0),
    ([0, 0], 1, False, [0.5, 0], 0.5),
    ([0, 0], 1, True, [0.5, 0], 0),
    ([0, 0], 1, False, [0, 1], 0),
    ([0, 0], 1, True, [0, 1], 0),
    ([1, 1], 1, True, [2, 2], sqrt(2) - 1),
])
def test_circle_distance_to_pt(center, radius, inner_space, pt, distance):
    c = calc_utils.CircleUtils(center, radius, inner_space)
    assert c.distance_to_pt(pt) == distance


# Test ArcUtils.
@pytest.mark.parametrize('startangle, endangle, angle, expected', [
    (-10, 300, 90, True),
    (-10, 300, 190, True),
    (-10, 300, -15, False),
    (-10, 300, -70, True),
    (-10, 300, -60, True),
    (-10, 300, 290, True),
    (-10, 300, 300, True),
    (-10, 300, -10, True),
    (-10, 300, 301, False),
    (-20, -30, -25, False),
    (-20, -30, 335, False),
    (-20, -30, 0, True),
    (-20, -30, -10, True),
    (-20, -30, -100, True),
])
def test_angle_in_range(startangle, endangle, angle, expected):
   au = calc_utils.ArcUtils((0, 0), 1, startangle * pi/180, endangle * pi/180)
   assert au.check_angle_in_range(angle * pi/180) == expected
