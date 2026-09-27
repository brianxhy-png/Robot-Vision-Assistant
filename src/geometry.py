def calculate_angle(
    object_x,
    frame_width,
    horizontal_fov
):
    """
    Calculate the horizontal angle from the
    center of the camera to the detected object.
    """

    frame_center = frame_width / 2

    pixel_offset = object_x - frame_center

    degrees_per_pixel = horizontal_fov / frame_width

    angle = pixel_offset * degrees_per_pixel

    return angle


def estimate_distance(
    known_width,
    focal_length,
    object_width_pixels
):
    """
    Estimate distance using the pinhole camera model.

    distance = (known object width × focal length)
               / observed pixel width
    """

    if object_width_pixels <= 0:
        return 0

    distance = (
        known_width *
        focal_length /
        object_width_pixels
    )

    return distance