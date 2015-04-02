import pytest
from bcam.loader_excellon import *

# Test buffer loading
@pytest.mark.parametrize('lines, expected_points, expected_units', [
    (["METRIC,TZ", "X90.1Y-84.5", "X-91.7Y-84.8", "X92.2Y-73.6", "X93.Y-86.3", "X95.6Y-67.", "X-97.Y-87.2"], [(90.1, -84.5), (-91.7, -84.8), (92.2, -73.6), (93., -86.3), (95.6, -67.), (-97., -87.2)], ExcUnits.metric)
])
def test_buffer_loading(lines, expected_points, expected_units):
    el = ExcellonLoader()
    el.load_from_list(lines)
    for p, e in zip(el.points, expected_points):
        assert(p == e)
    assert(el.units == expected_units)
