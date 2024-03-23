from hx711v0_5_1 import HX711

class WeightService:
    def __init__(self):
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
