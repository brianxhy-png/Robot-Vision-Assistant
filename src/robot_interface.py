class RobotInterface:

    def turn_left(self, amount):
        print(
            f"ROBOT COMMAND → Turn left "
            f"{amount:.2f} degrees"
        )

    def turn_right(self, amount):
        print(
            f"ROBOT COMMAND → Turn right "
            f"{amount:.2f} degrees"
        )

    def move_forward(self, distance):
        print(
            f"ROBOT COMMAND → Move forward "
            f"{distance:.2f} cm"
        )

    def stop(self):
        print("ROBOT COMMAND → STOP")