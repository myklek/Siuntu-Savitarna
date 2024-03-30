import cv2
import numpy as np


def detect_objects(frame, aruco_corners):
    # Convert Image to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Create a Mask with adaptive threshold
    mask = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 91, 25)
    #

    # Find contours
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

            # Calculate the centroid of the contour
            M = cv2.moments(cnt)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Calculate the distance of the centroid to the center of the image
            distance = np.sqrt((image_center[0] - cX) ** 2 + (image_center[1] - cY) ** 2)

            # If the distance is smaller than the current minimum, update the minimum and the most centered contour
            if distance < min_distance:
                min_distance = distance
                most_centered_contour = cnt

    # Approximate the most centered contour and return it
    if most_centered_contour is not None:
        most_centered_contour = cv2.approxPolyDP(most_centered_contour,
                                                 0.03 * cv2.arcLength(most_centered_contour, True), True)
        return [most_centered_contour]
    else:
        return []


class HomogeneousBgDetector:
    def __init__(self):
        pass
