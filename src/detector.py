import cv2


class ObjectDetector:

    def __init__(self):
        # HSV range for detecting orange/red objects
        self.lower = (0, 100, 100)
        self.upper = (25, 255, 255)

    def detect(self, frame):

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(
            hsv,
            self.lower,
            self.upper
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        objects = []

        for contour in contours:

            area = cv2.contourArea(contour)

            # Ignore tiny objects/noise
            if area < 500:
                continue

            x, y, width, height = cv2.boundingRect(contour)

            center_x = x + width // 2
            center_y = y + height // 2

            objects.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "center": (center_x, center_y),
                "area": area
            })

        return objects