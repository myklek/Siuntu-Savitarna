from object_detector import *
import cv2
import numpy as np

ARCUO_PERIMETER = 13.6
STABLE_CHANGE_THRESHOLD = 1
STABLE_READINGS_REQUIRED = 5

class CameraService:
    def __init__(self):
        print("CameraService init")
        self.cam = cv2.VideoCapture(0)
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self.cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))
        self.cam.set(cv2.CAP_PROP_EXPOSURE, 110)

        self.parameters = cv2.aruco.DetectorParameters()
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)

    def get_object_dimensions(self, stop_event):
        last_width, last_height = None, None
        stable_count = 0

        while not stop_event.is_set():
            ret, img = self.cam.read()

            corners, _, _ = cv2.aruco.detectMarkers(img, self.aruco_dict, parameters=self.parameters)
            if corners:
                aruco_perimeter = cv2.arcLength(corners[0], True)
                pixel_cm_ratio = aruco_perimeter / ARCUO_PERIMETER

                contours = detect_objects(img, np.intp(corners))

                for cnt in contours:
                    rect = cv2.minAreaRect(cnt)
                    (x, y), (w, h), angle = rect

                    object_width = w / pixel_cm_ratio
                    object_height = h / pixel_cm_ratio

                    is_stable = False
                    if (last_width is not None and
                            last_height is not None and
                            abs(last_width - object_width) < STABLE_CHANGE_THRESHOLD and
                            abs(last_height - object_height) < STABLE_CHANGE_THRESHOLD):
                        stable_count += 1
                    else:
                        stable_count = 0

                    if stable_count >= STABLE_READINGS_REQUIRED:
                        is_stable = True
                    else:
                        is_stable = False
                    last_width, last_height = object_width, object_height
                    print({"type": "dimensions",
                           "width": round(object_width, 0),
                           "length": round(object_height, 0),
                           "stable": is_stable})
                    yield {"type": "dimensions",
                           "width": round(object_width, 0),
                           "length": round(object_height, 0),
                           "stable": is_stable}