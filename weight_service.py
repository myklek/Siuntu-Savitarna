import threading
import time
import sys
import RPi.GPIO as GPIO
from hx711v0_5_1 import HX711
import queue

hx = HX711(5, 6)

current_weight = 0.0
weight_queue = queue.Queue()

hx.setReadingFormat("MSB", "MSB")
hx.autosetOffset()
offsetValue = hx.getOffset()
referenceUnit = 1051
hx.setReferenceUnit(referenceUnit)


def get_weight():
    raw_bytes = hx.getRawBytes()
    weight_value = hx.rawBytesToWeight(raw_bytes)
    weight_value = -round(weight_value, 1)
    return weight_value


def read_sensor():
    global current_weight
    while True:
        try:
            current_weight = get_weight()
            weight_queue.put(current_weight)
            print("Weight: ", current_weight)

        except (KeyboardInterrupt, SystemExit):
            GPIO.cleanup()
            print("[INFO] 'KeyboardInterrupt Exception' detected. Cleaning and exiting...")
            sys.exit()


background_thread = threading.Thread(target=read_sensor())
background_thread.daemon = True  # Ensure it exits with the main program
background_thread.start()
