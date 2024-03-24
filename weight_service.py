from time import sleep

from hx711v0_5_1 import HX711

WEIGHT_CHANGE_THRESHOLD = 1
STABLE_READINGS_REQUIRED = 5
MINIMUM_WEIGHT = 5


class WeightService:
    def __init__(self):
        print("WeightService init")
        self.hx = HX711(5, 6)
        self.hx.setReadingFormat("MSB", "MSB")
        self.hx.autosetOffset()
        self.offsetValue = self.hx.getOffset()
        self.referenceUnit = 1051
        self.hx.setReferenceUnit(self.referenceUnit)

    def get_weight(self):
        raw_bytes = self.hx.getRawBytes()
        weight_value = self.hx.rawBytesToWeight(raw_bytes)
        weight_value = abs(round(weight_value, 0))
        return weight_value

    def get_stable_weight(self):
        prev_weight = None
        equal_readings = 0
        while True:
            sleep(0.2)
            current_weight = self.get_weight()
            yield current_weight  # yield the current weight reading
            if (prev_weight is not None
                    and abs(prev_weight - current_weight) < WEIGHT_CHANGE_THRESHOLD
                    and current_weight > MINIMUM_WEIGHT):
                equal_readings += 1
                if equal_readings == STABLE_READINGS_REQUIRED:
                    break
            else:
                equal_readings = 0
            prev_weight = current_weight
