from app.core.geometry import Point, angle_degrees


def test_angle_degrees_right_angle() -> None:
    # Angle at B is 90 degrees: A(1,0), B(0,0), C(0,1)
    a = Point(1, 0)
    b = Point(0, 0)
    c = Point(0, 1)
    ang = angle_degrees(a, b, c)
    assert 89.9 < ang < 90.1


def test_angle_degrees_straight_line() -> None:
    a = Point(-1, 0)
    b = Point(0, 0)
    c = Point(1, 0)
    ang = angle_degrees(a, b, c)
    assert 179.9 < ang < 180.1

