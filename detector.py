import cv2


class ObjectDetector:
    """Detect blobs inside an HSV color range."""

    def __init__(self, lower=(0, 100, 100), upper=(25, 255, 255), min_area=500):
        if any(lo > hi for lo, hi in zip(lower, upper)):
            raise ValueError("HSV lower bounds must not exceed upper bounds")
        if min_area <= 0:
            raise ValueError("min_area must be positive")
        self.lower = lower
        self.upper = upper
        self.min_area = min_area
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    def detect(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.lower, self.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
            x, y, width, height = cv2.boundingRect(contour)
            objects.append({
                "x": x, "y": y, "width": width, "height": height,
                "center": (x + width // 2, y + height // 2), "area": area,
            })
        return sorted(objects, key=lambda obj: obj["area"], reverse=True)
