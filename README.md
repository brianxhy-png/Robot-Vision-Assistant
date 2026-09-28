# Robot Vision Assistant

A Python and OpenCV camera demo that detects color selected objects, follows one target across frames, estimates its horizontal bearing and approximate distance, and prints suggested robot turn directions. It is intended as a readable starting point for robotics vision experiments.

> **Project status:** Local computer demo. The robot interface prints commands to the terminal. It does not drive motors, connect to an FTC Control Hub, or provide autonomous navigation.

## Contents

- [What it does](#what-it-does)
- [Quick start](#quick-start)
- [Configuration](#configuration)
- [How the pipeline works](#how-the-pipeline-works)
- [Calibration](#calibration)
- [Project layout](#project-layout)
- [Limitations and safety](#limitations-and-safety)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## What it does

| Capability | Current behavior |
| --- | --- |
| Camera input | Reads a webcam through OpenCV and displays an annotated preview. |
| Detection | Thresholds a configurable HSV color range, removes small mask noise, and finds contours above a minimum area. |
| Target selection | Initially chooses the largest blob. On subsequent frames, chooses the nearest detection within a configurable pixel radius; falls back to the largest blob when no match is nearby. |
| Geometry | Computes horizontal bearing from image position and configured horizontal field of view; estimates range using target width and focal length. |
| Movement display | Shows pixel displacement between consecutive detections. This is **pixels per frame**, not physical speed. |
| Command output | Prints a left/right/stop suggestion when direction changes. No robot is actuated. |
| Loss of target | Clears tracking history and prints STOP. |

The preview draws green boxes around detections, a red dot over the selected target, and a center line. Positive bearing means the target appears to the right of the image center; negative means left.

## Quick start

**Requirements:** Python 3.10 or newer, a camera recognized by OpenCV, and a desktop session that can show an OpenCV window. A headless server will need a different display path.

```bash
git clone https://github.com/brianxhy-png/Robot-Vision-Assistant.git
cd Robot-Vision-Assistant
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python src/main.py
```

On Windows, activate with `.venv\Scripts\activate` and use `python` in place of `python3` if needed. Allow camera access when the operating system asks. Hold an orange object in view under even lighting. Press **Q** or **Esc** while the preview window is focused to quit.

For a different camera or lighting condition:

```bash
python src/main.py --camera 1 --hsv-low 5,100,100 --hsv-high 25,255,255 --min-area 800
```

Run `python src/main.py --help` for the full set of options.

## Configuration

All options are set at launch; the defaults are examples and should be measured for your camera and object.

| Option | Default | Meaning |
| --- | ---: | --- |
| `--camera` | `0` | OpenCV camera index. Try `1` if another camera occupies index 0. |
| `--width`, `--height` | `1280`, `720` | Requested resolution. The camera may return another size; calculations use the actual frame width. |
| `--hsv-low`, `--hsv-high` | `0,100,100`, `25,255,255` | Inclusive color bounds in OpenCV HSV: H 0–179, S/V 0–255. |
| `--min-area` | `500` | Minimum contour area in square pixels. Raise to suppress small blobs. |
| `--match-distance` | `100` | Maximum target center movement in pixels before reacquiring the largest blob. |
| `--horizontal-fov` | `70` | Assumed horizontal camera field of view in degrees. |
| `--object-width-cm` | `7` | Real width of the target in centimeters. |
| `--focal-length-px` | `800` | Effective horizontal focal length in pixels, calibrated at the chosen resolution. |
| `--deadband` | `5` | Bearing within ± this many degrees results in STOP. |

HSV ranges that cross hue zero (such as deep red near H=179 and H=0) need two masks; this detector currently accepts a single continuous range.

## How the pipeline works

```text
Webcam frame
  → BGR to HSV → color mask → open/close cleanup → contours
  → area filter → nearest target match → bounding box and center
  → bearing + width-based range → preview + console suggestion
```

1. **Detection:** HSV color filtering finds pixels in the selected range. Morphological opening removes isolated noise; closing fills small gaps. External contours become bounding boxes.
2. **Tracking:** The largest visible object starts a track. The next frame uses the closest candidate within `--match-distance`. When no candidate is close enough, the tracker reacquires the largest. If no detections remain, tracking resets.
3. **Bearing:** For image width `W`, horizontal field of view `F`, and target center `x`, the approximate focal length is `f = W / (2 tan(F/2))`. Bearing is `atan((x - W/2) / f)`. Angular calculations use radians internally and display degrees.
4. **Range:** `distance_cm = object_width_cm × focal_length_px / observed_width_px`. This assumes the target faces the camera and the supplied width and focal length are correct.
5. **Decision:** Bearing less than `-deadband` prints left; greater than `+deadband` prints right; otherwise prints STOP. The value displayed is the observed bearing, **not** a calibrated motor turn request.

## Calibration

### Color

Put the real target in its intended lighting and inspect its HSV pixel values using an image inspection tool or a small OpenCV script. Choose lower/upper bounds that include the object while excluding background colors. Start with the defaults for orange, then adjust saturation/value for shadows and exposure. A colored background or changing auto exposure can cause false detections.

### Bearing

Get the camera's **horizontal** field of view from its specifications or calibrate it. Keep the image at the intended resolution and avoid digital cropping. A phone or wide angle lens can introduce distortion, especially near image edges. For accurate geometry, calibrate the lens and undistort frames before using this formula.

### Distance

Place an object of measured width `w` centimeters at a measured distance `D` centimeters. Measure its bounding box width `p` pixels in a frame, then compute `focal_length_px = p × D / w`. For example, a 7 cm wide target measuring 140 px at 40 cm gives `f = 800 px`. Set `--object-width-cm 7 --focal-length-px 800`. Validate at several other distances and keep camera resolution unchanged. Bounding box width changes if the object rotates or is partly hidden.

### Matching

Adjust `--match-distance` after observing how far the object moves between frames. Larger values tolerate faster motion but can swap targets. This implementation has no object IDs, prediction, or occlusion recovery.

## Project layout

```text
Robot-Vision-Assistant/
├── LICENSE                 MIT terms
├── README.md               Setup and operating guide
├── requirements.txt        OpenCV and NumPy dependencies
└── src/
    ├── main.py             CLI, camera loop, preview, cleanup
    ├── detector.py         HSV segmentation and contour boxes
    ├── tracker.py          Single-target association
    ├── geometry.py         Bearing and pinhole range helpers
    └── robot_interface.py  Console-only command sink
```

## Limitations and safety

- This is a **prototype**, not an FTC SDK OpMode. It runs on a desktop Python environment, and `RobotInterface` does not send data to hardware.
- A printed direction is not a motor command. A future robot integration needs a transport, measured camera placement, control logic, limits, and a reliable stop path.
- The program selects by color and proximity, not by object class. Similar colored objects can be confused; partial occlusion and poor lighting can interrupt tracking.
- Displacement is measured in pixels per frame. It depends on frame rate and does not account for robot or camera motion.
- Distance is approximate. It is especially unreliable for rotated, irregular, or partially visible objects.
- Never use the prototype output alone as a collision avoidance or safety system. Test any hardware integration with wheels raised or in a controlled space first.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `Cannot open camera index 0` | Close other camera apps; grant camera permission; try `--camera 1`. |
| Window opens but target is absent | Adjust HSV range and lighting; lower `--min-area`; confirm the object is large enough in frame. |
| Background objects are detected | Tighten HSV range, increase minimum area, and simplify the backdrop. |
| Target jumps between objects | Lower `--match-distance`, isolate the target color, or add a stronger tracker. |
| Distance appears wrong | Measure object width and focal length again at the actual camera resolution. |
| No preview on a remote machine | Run on a desktop with a display, or replace `imshow` with a suitable streaming or file output. |
| `ModuleNotFoundError: cv2` | Activate the virtual environment and rerun `python -m pip install -r requirements.txt`. |

## Development

The code is intentionally split so detection, association, geometry, and the robot output adapter can evolve separately. Useful next steps include a live HSV tuning panel, measured camera calibration, saved example frames, multi-object tracking, structured output, and a separately tested hardware adapter. These are future work, not current features.

For local checks:

```bash
python -m compileall -q src
python -m unittest discover -s tests -v
```

A webcam session is still needed to validate lighting, FPS, and real target measurements.

## License

Copyright (c) 2026 Brian Xin. Licensed under the [MIT License](LICENSE). Third party packages remain under their own licenses.
