from object_detector import *
import cv2
import numpy as np


class QRDetectionService:
    def __init__(self, cam):
        print("QR Detection Service init")
        self.cam = cam
        self.qr_code_detector = cv2.QRCodeDetector()

    def get_qr_code_data(self, stop_event):
        while not stop_event.is_set():

            if not self.cam.isOpened():
                self.cam.open(0)
                # Detect and decode the qrcode

            ret, img = self.cam.read()
            data, points, _ = self.qr_code_detector.detectAndDecode(img)

            if points is not None:
                if data:
                    yield {"type": "qrData", "data": data}  # y

    def close(self):
        if self.cam:
            self.cam.release()
