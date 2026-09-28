"""Run the camera preview and print suggested turn directions."""
import argparse

import cv2

from detector import ObjectDetector
from geometry import calculate_angle, estimate_distance
from robot_interface import RobotInterface
from tracker import ObjectTracker


def hsv_triplet(value):
    try:
        triplet = tuple(int(part.strip()) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Use H,S,V integers") from exc
    if len(triplet) != 3 or not (0 <= triplet[0] <= 179) or not all(0 <= x <= 255 for x in triplet[1:]):
        raise argparse.ArgumentTypeError("HSV must be H=0..179, S=0..255, V=0..255")
    return triplet


def positive_float(value):
    number = float(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("Value must be positive")
    return number


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0)")
    parser.add_argument("--width", type=int, default=1280, help="Requested camera width")
    parser.add_argument("--height", type=int, default=720, help="Requested camera height")
    parser.add_argument("--hsv-low", type=hsv_triplet, default=(0, 100, 100), help="HSV lower bound H,S,V")
    parser.add_argument("--hsv-high", type=hsv_triplet, default=(25, 255, 255), help="HSV upper bound H,S,V")
    parser.add_argument("--min-area", type=positive_float, default=500, help="Minimum contour area in pixels squared")
    parser.add_argument("--match-distance", type=positive_float, default=100, help="Maximum matching distance in pixels")
    parser.add_argument("--horizontal-fov", type=positive_float, default=70, help="Camera horizontal FOV in degrees")
    parser.add_argument("--object-width-cm", type=positive_float, default=7, help="Real target width in cm")
    parser.add_argument("--focal-length-px", type=positive_float, default=800, help="Calibrated focal length in pixels")
    parser.add_argument("--deadband", type=positive_float, default=5, help="Bearing deadband in degrees")
    return parser.parse_args()


def run(config):
    if config.width <= 0 or config.height <= 0 or not 0 < config.horizontal_fov < 180:
        raise ValueError("Width and height must be positive; FOV must be between 0 and 180 degrees")

    detector = ObjectDetector(config.hsv_low, config.hsv_high, config.min_area)
    tracker = ObjectTracker(config.match_distance)
    robot = RobotInterface()
    camera = cv2.VideoCapture(config.camera)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Cannot open camera index {config.camera}")

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
    print("Robot Vision Assistant started. Press Q or Esc to quit.")

    try:
        while True:
            success, frame = camera.read()
            if not success:
                print("Camera read failed; stopping.")
                robot.stop()
                break

            height, width = frame.shape[:2]
            objects = detector.detect(frame)
            target = tracker.update(objects)
            cv2.line(frame, (width // 2, 0), (width // 2, height), (255, 255, 0), 1)

            for obj in objects:
                x, y, w, h = obj["x"], obj["y"], obj["width"], obj["height"]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 180, 0), 2)

            if target is None:
                robot.stop()
                cv2.putText(frame, "NO TARGET", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            else:
                cx, cy = target["center"]
                angle = calculate_angle(cx, width, config.horizontal_fov)
                distance = estimate_distance(config.object_width_cm, config.focal_length_px, target["width"])
                dx, dy = target["velocity"]
                cv2.circle(frame, (cx, cy), 6, (0, 0, 255), -1)
                lines = [
                    f"Bearing: {angle:+.1f} deg",
                    f"Estimated range: {distance:.1f} cm",
                    f"Frame displacement: ({dx:+d}, {dy:+d}) px",
                ]
                for index, line in enumerate(lines):
                    cv2.putText(frame, line, (30, 40 + index * 35),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                if angle < -config.deadband:
                    robot.turn_left(abs(angle))
                elif angle > config.deadband:
                    robot.turn_right(abs(angle))
                else:
                    robot.stop()

            cv2.imshow("Robot Vision Assistant", frame)
            if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                break
    finally:
        robot.stop()
        camera.release()
        cv2.destroyAllWindows()
        print("Robot Vision Assistant stopped.")


if __name__ == "__main__":
    run(arguments())
