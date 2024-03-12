import cv2

print("Start!")

webcam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
webcam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))

if webcam.isOpened():
    print("Video is opened!")

while True:
    ret, frame = webcam.read()
    cv2.imshow('Webcam stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.waitKey(0)
webcam.release()
cv2.destroyAllWindows()

print("Happy End!")
