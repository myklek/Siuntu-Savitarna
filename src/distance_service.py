import RPi.GPIO as GPIO
import time
from threading import Event

DISTANCE_CHANGE_THRESHOLD = 5
STABLE_READINGS_REQUIRED = 5
BASE_DISTNACE = 41.3
AVG_READINGS = 10


class DistanceService:
    def __init__(self):
        print("DistanceService init")
        GPIO.setmode(GPIO.BCM)
        self.PIN_TRIGGER = 4
        self.PIN_ECHO = 17
        GPIO.setup(self.PIN_TRIGGER, GPIO.OUT)
        GPIO.setup(self.PIN_ECHO, GPIO.IN)
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)
        time.sleep(2)

    def get_distance(self):
        GPIO.output(self.PIN_TRIGGER, GPIO.HIGH)
        time.sleep(0.01)
        GPIO.output(self.PIN_TRIGGER, GPIO.LOW)

        pulse_start_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 0:
            pulse_start_time = time.time()

        pulse_end_time = time.time()
        while GPIO.input(self.PIN_ECHO) == 1:
            pulse_end_time = time.time()

        pulse_duration = (pulse_end_time - pulse_start_time)
        distance = round(pulse_duration * 17150, 2)

        return distance

    def get_stable_distance(self, stop_event):
        prev_distance = None
        equal_readings = 0
        last_n_distances = []
        while not stop_event.is_set():
            time.sleep(0.05)
            current_distance = self.get_distance()
            print('raw distance', current_distance)
            last_n_distances.append(current_distance)
            if len(last_n_distances) > AVG_READINGS:
                last_n_distances.pop(0)  # remove the oldest distance
            average_distance = sum(last_n_distances) / len(last_n_distances)
            if (prev_distance is not None
                    and abs(prev_distance - average_distance) < DISTANCE_CHANGE_THRESHOLD):
                equal_readings += 1
                if equal_readings == STABLE_READINGS_REQUIRED:
                    print({"type": "distance", "distance": round(BASE_DISTNACE - average_distance,1), "stable": True})
                    yield {"type": "distance", "distance": round(BASE_DISTNACE - average_distance,1), "stable": True}
                    equal_readings = 0
            else:
                equal_readings = 0
                print({"type": "distance", "distance": round(BASE_DISTNACE - average_distance,1), "stable": False})
                yield {"type": "distance", "distance":  round(BASE_DISTNACE - average_distance,1), "stable": False}
            prev_distance = average_distance


    def close(self):
        GPIO.cleanup()
