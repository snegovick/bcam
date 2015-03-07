from math import pi
import pytest
from bcam import calc_utils


@pytest.mark.parametrize('startangle, endangle, angle, expected', [
        (-10, 300, 90, True),
        (-10, 300, 190, True),
        (-10, 300, -15, False),
        (-10, 300, 290, True),
        (-10, 300, 301, False),
])
def test_angle_range(startangle, endangle, angle, expected):
   au = calc_utils.ArcUtils((0, 0), 1, startangle * pi/180, endangle * pi/180)
   assert au.check_angle_in_range(angle * pi/180) == expected
