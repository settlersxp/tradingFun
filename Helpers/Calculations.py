from Helpers.Interval import Interval
from Indices.EMA import EMA
from Indices.RSI import RSI


class Calculations(Interval):
    __lastProcessedIndex = {}
    RSI = None
    EMA = None

    def __init__(self, dateType, dateDuration):
        super().__init__(dateType, dateDuration)
        self.RSI = RSI(self.allCandles, self.__lastProcessedIndex)
        self.EMA = EMA(self.allCandles, self.__lastProcessedIndex)

    def add(self, candle, index):
        Interval.add(self, candle, index)