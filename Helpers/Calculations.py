from Helpers.Interval import Interval


class Calculations(Interval):
    lastProcessedIndex = {}

    def __init__(self, dateType, dateDuration):
        super().__init__(dateType, dateDuration)

    def add(self, candle):
        Interval.add(self, candle)