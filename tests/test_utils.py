from src.common.utilities.function_helper import calculate_distance_m


def test_distance_returns_correct():
    lat1 = 44.265328
    lon1 = -72.577973
    lat2 = 44.445821
    lon2 = -73.260199

    distance = calculate_distance_m(lat1, lon1, lat2, lon2)

    assert round(distance, 2) == 57798.54
