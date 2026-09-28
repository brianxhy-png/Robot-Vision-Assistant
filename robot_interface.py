class RobotInterface:
    """Console-only command sink. No physical robot is controlled."""

    def __init__(self):
        self.last_direction = None

    def _emit(self, direction, command):
        if direction != self.last_direction:
            print(f"ROBOT COMMAND → {command}")
            self.last_direction = direction

    def turn_left(self, amount):
        self._emit("left", f"Turn left (bearing {amount:.1f} degrees)")

    def turn_right(self, amount):
        self._emit("right", f"Turn right (bearing {amount:.1f} degrees)")

    def stop(self):
        self._emit("stop", "STOP")
