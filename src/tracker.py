class ObjectTracker:

    def __init__(self):
        self.previous_position = None

    def update(self, objects):

        if not objects:
            self.previous_position = None
            return None

        # Track the largest detected object
        target = max(
            objects,
            key=lambda obj: obj["area"]
        )

        current_position = target["center"]

        velocity = (0, 0)

        if self.previous_position is not None:

            dx = (
                current_position[0]
                - self.previous_position[0]
            )

            dy = (
                current_position[1]
                - self.previous_position[1]
            )

            velocity = (dx, dy)

        self.previous_position = current_position

        target["velocity"] = velocity

        return target