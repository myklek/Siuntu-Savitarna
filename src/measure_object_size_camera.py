from object_detector import *

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))
cam.set(cv2.CAP_PROP_EXPOSURE, 110)
# cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0)
# set contrast
# cam.set(cv2.CAP_PROP_CONTRAST, 75)


# Load Aruco detector
parameters = cv2.aruco.DetectorParameters()
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_50)

# Load Object Detector




# Load Cap

while True:
    ret, img = cam.read()

    # Get Aruco marker
    corners, _, _ = cv2.aruco.detectMarkers(img, aruco_dict, parameters=parameters)
    if corners:

        # Draw polygon around the marker
        int_corners = np.intp(corners)
        # cv2.polylines(img, int_corners, True, (0, 255, 0), 3)

        # Aruco Perimeter
        aruco_perimeter = cv2.arcLength(corners[0], True)

        # Pixel to cm ratio
        pixel_cm_ratio = aruco_perimeter / 13.6

        contours = detect_objects(img, int_corners)

        # Draw objects boundaries
        for cnt in contours:
            # Get rect
            rect = cv2.minAreaRect(cnt)
            (x, y), (w, h), angle = rect

            # Get Width and Height of the Objects by applying the Ratio pixel to cm
            object_width = w / pixel_cm_ratio
            object_height = h / pixel_cm_ratio

            # Display rectangle
            box = cv2.boxPoints(rect)
            box = np.intp(box)

            # cv2.circle(img, (int(x), int(y)), 5, (0, 0, 255), -1)
            # cv2.polylines(img, [box], True, (255, 0, 0), 2)
            # cv2.putText(img, "Width {} cm".format(round(object_width, 1)), (int(x - 100), int(y - 20)),
            #             cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)
            # cv2.putText(img, "Height {} cm".format(round(object_height, 1)), (int(x - 100), int(y + 15)),
            #             cv2.FONT_HERSHEY_PLAIN, 2, (100, 200, 0), 2)

            print("Object detected")
            print("Width: {} cm".format(round(object_width, 1)))
            print("Height: {} cm".format(round(object_height, 1)))




    # cv2.imshow("Image", img)
    key = cv2.waitKey(1)
    if key == 27:
        break

cam.release()
cv2.destroyAllWindows()
