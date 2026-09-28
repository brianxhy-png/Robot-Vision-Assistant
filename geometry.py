from math import atan, degrees, radians, tan


def calculate_angle(object_x, frame_width, horizontal_fov):
    """Horizontal bearing in degrees; positive means right of image center.

    Assumes a rectilinear camera and a centered, undistorted image.
    """
    if frame_width <= 0 or not 0 < horizontal_fov < 180:
        raise ValueError("frame_width must be positive and horizontal_fov in (0, 180)")
    focal_length_pixels = frame_width / (2 * tan(radians(horizontal_fov) / 2))
    return degrees(atan((object_x - frame_width / 2) / focal_length_pixels))


def estimate_distance(known_width, focal_length, object_width_pixels):
    """Pinhole estimate, in the same units as known_width."""
    if known_width <= 0 or focal_length <= 0:
        raise ValueError("known_width and focal_length must be positive")
    if object_width_pixels <= 0:
        return None
    return known_width * focal_length / object_width_pixels
