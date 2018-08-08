import time
from datetime import datetime

from Helpers.Interval import Interval


class Calculations(Interval):
    lastProcessedIndex = {}
    dateType = None

    def __init__(self, dateType, dateDuration, firstTick, timeAtBeginningOfHour):
        super().__init__(dateType, dateDuration, firstTick, timeAtBeginningOfHour)
        self.dateType = dateType

    def add(self, candle):
        Interval.add(self, candle)
