import cv2
import numpy as np
import base64


def detect_objects(frame, aruco_corners):
    # Kovertuoja į grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Bitmapas
    mask = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 91, 25)

    # Kontūrai
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    aruco_contour = cv2.convexHull(aruco_corners[0])
    contours = [cnt for cnt in contours if not cv2.intersectConvexConvex(cnt, aruco_contour)[0]]

    # cv2.imshow("mask", mask)
    image_center = (frame.shape[1] // 2, frame.shape[0] // 2)

    min_distance = float('inf')
    most_centered_contour = None

    for cnt in contours:

        area = cv2.contourArea(cnt)
        if area > 1000:

            M = cv2.moments(cnt)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Centras
            distance = np.sqrt((image_center[0] - cX) ** 2 + (image_center[1] - cY) ** 2)

            if distance < min_distance:
                min_distance = distance
                most_centered_contour = cnt

    if most_centered_contour is not None:
        most_centered_contour = cv2.approxPolyDP(most_centered_contour,
                                                 0.03 * cv2.arcLength(most_centered_contour, True), True)

        x, y, w, h = cv2.boundingRect(most_centered_contour)
        cropped_mask = mask[y:y + h, x:x + w]
        # Nuotraukos negatyvas siuntimui

        cropped_mask = cv2.bitwise_not(cropped_mask)
        # cv2.imshow("cropped", cropped_mask)
        base64_image = convert_to_base64(compress_image(cropped_mask, 100))

        return most_centered_contour, base64_image


class HomogeneousBgDetector:
    def __init__(self):
        pass


def convert_to_base64(cropped_mask):
    _, encoded_image = cv2.imencode('.jpg', cropped_mask)

    byte_image = encoded_image.tobytes()

    base64_bytes = base64.b64encode(byte_image)

    base64_string = base64_bytes.decode('utf-8')

    return base64_string


def compress_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)

    dsize = (width, height)

    output = cv2.resize(image, dsize)

    return output
