import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geometry import calculate_angle, estimate_distance
from tracker import ObjectTracker


def detection(x, area):
    return {"center": (x, 30), "area": area, "width": 20}


class GeometryTests(unittest.TestCase):
    def test_bearing_sign_and_center(self):
        self.assertAlmostEqual(calculate_angle(640, 1280, 70), 0)
        self.assertAlmostEqual(calculate_angle(1280, 1280, 70), 35)
        self.assertAlmostEqual(calculate_angle(0, 1280, 70), -35)

    def test_distance_and_invalid_width(self):
        self.assertAlmostEqual(estimate_distance(7, 800, 140), 40)
        self.assertIsNone(estimate_distance(7, 800, 0))


class TrackerTests(unittest.TestCase):
    def test_nearest_detection_stays_selected_even_when_smaller(self):
        tracker = ObjectTracker(max_match_distance=30)
        tracker.update([detection(10, 100)])
        selected = tracker.update([detection(20, 60), detection(150, 500)])
        self.assertEqual(selected["center"], (20, 30))
        self.assertEqual(selected["velocity"], (10, 0))

    def test_empty_frame_resets_track(self):
        tracker = ObjectTracker()
        tracker.update([detection(10, 100)])
        self.assertIsNone(tracker.update([]))
        self.assertEqual(tracker.update([detection(30, 100)])["velocity"], (0, 0))


if __name__ == "__main__":
    unittest.main()
