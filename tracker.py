from math import hypot


class ObjectTracker:
    """Associate one detection across frames using nearest-center matching.

    This is a lightweight single-target tracker, not a persistent object ID system.
    """

    def __init__(self, max_match_distance=100):
        if max_match_distance <= 0:
            raise ValueError("max_match_distance must be positive")
        self.previous_position = None
        self.max_match_distance = max_match_distance

    def update(self, objects):
        if not objects:
            self.previous_position = None
            return None

        if self.previous_position is None:
            target = max(objects, key=lambda obj: obj["area"])
        else:
            nearest = min(
                objects,
                key=lambda obj: hypot(obj["center"][0] - self.previous_position[0],
                                      obj["center"][1] - self.previous_position[1]),
            )
            distance = hypot(nearest["center"][0] - self.previous_position[0],
                             nearest["center"][1] - self.previous_position[1])
            target = nearest if distance <= self.max_match_distance else max(objects, key=lambda obj: obj["area"])

        position = target["center"]
        velocity = (0, 0) if self.previous_position is None else (
            position[0] - self.previous_position[0],
            position[1] - self.previous_position[1],
        )
        self.previous_position = position
        return {**target, "velocity": velocity}
