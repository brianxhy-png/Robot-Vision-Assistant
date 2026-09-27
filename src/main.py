import cv2

from detector import ObjectDetector
from tracker import ObjectTracker
from geometry import calculate_angle, estimate_distance
from robot_interface import RobotInterface


# ==========================================
# CAMERA SETTINGS
# ==========================================

CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

# Approximate horizontal field of view
HORIZONTAL_FOV = 70


# ==========================================
# DISTANCE ESTIMATION
# ==========================================

# Example object width in centimeters.
# This must be changed for the real object.
KNOWN_OBJECT_WIDTH = 7.0

# Example focal length.
# This must be calibrated for the real camera.
FOCAL_LENGTH = 800


# ==========================================
# CREATE SYSTEM COMPONENTS
# ==========================================

detector = ObjectDetector()
tracker = ObjectTracker()
robot = RobotInterface()


# ==========================================
# OPEN CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

camera.set(
    cv2.CAP_PROP_FRAME_WIDTH,
    CAMERA_WIDTH
)

camera.set(
    cv2.CAP_PROP_FRAME_HEIGHT,
    CAMERA_HEIGHT
)


if not camera.isOpened():

    print("ERROR: Could not open camera.")
    exit()


print("Robot Vision Assistant started.")
print("Press Q to quit.")


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    success, frame = camera.read()

    if not success:

        print("ERROR: Could not read camera.")
        break


    frame_height, frame_width = frame.shape[:2]


    # ======================================
    # OBJECT DETECTION
    # ======================================

    objects = detector.detect(frame)


    # ======================================
    # OBJECT TRACKING
    # ======================================

    target = tracker.update(objects)


    # ======================================
    # DRAW ALL DETECTED OBJECTS
    # ======================================

    for obj in objects:

        x = obj["x"]
        y = obj["y"]

        width = obj["width"]
        height = obj["height"]

        center = obj["center"]


        cv2.rectangle(
            frame,
            (x, y),
            (x + width, y + height),
            (0, 255, 0),
            2
        )


        cv2.circle(
            frame,
            center,
            5,
            (255, 0, 0),
            -1
        )


    # ======================================
    # TARGET PROCESSING
    # ======================================

    if target is not None:

        center_x, center_y = target["center"]

        object_width = target["width"]


        # ----------------------------------
        # Calculate angle
        # ----------------------------------

        angle = calculate_angle(
            center_x,
            frame_width,
            HORIZONTAL_FOV
        )


        # ----------------------------------
        # Estimate distance
        # ----------------------------------

        distance = estimate_distance(
            KNOWN_OBJECT_WIDTH,
            FOCAL_LENGTH,
            object_width
        )


        # ----------------------------------
        # Get movement
        # ----------------------------------

        velocity_x, velocity_y = target["velocity"]


        # ==================================
        # DISPLAY INFORMATION
        # ==================================

        cv2.putText(
            frame,
            f"Angle: {angle:.2f} deg",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Distance: {distance:.2f} cm",
            (30, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"Velocity: {velocity_x}, {velocity_y}",
            (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


        # ==================================
        # CAMERA CENTER LINE
        # ==================================

        cv2.line(
            frame,
            (frame_width // 2, 0),
            (frame_width // 2, frame_height),
            (255, 255, 0),
            2
        )


        # ==================================
        # ROBOT DECISION
        # ==================================

        if angle < -5:

            robot.turn_left(abs(angle))

        elif angle > 5:

            robot.turn_right(abs(angle))

        else:

            robot.stop()


    else:

        cv2.putText(
            frame,
            "NO TARGET",
            (30, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )


    # ======================================
    # SHOW CAMERA
    # ======================================

    cv2.imshow(
        "Robot Vision Assistant",
        frame
    )


    # ======================================
    # QUIT
    # ======================================

    if cv2.waitKey(1) & 0xFF == ord("q"):

        break


# ==========================================
# CLEANUP
# ==========================================

camera.release()

cv2.destroyAllWindows()

print("Robot Vision Assistant stopped.")