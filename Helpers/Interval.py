import time
from datetime import datetime
from time import mktime


class Interval:
    internalData = {
        'ohlc': {'o': 0, 'h': 0, 'l': 0, 'c': 0},
        'durations': [],
        'isUptrend': True
    }

    allCandles = []
    tempSection = []

    timeAtBeginningOfHour = None
    periodDuration = None
    dateDuration = None
    lastCandleAtPosition = 0

    def __init__(self, dateType, dateDuration, firstTick, timeAtBeginningOfHour):
        if 'min' in dateType:
            self.periodDuration = dateDuration * 60
        elif 'hour' in dateType:
            self.periodDuration = dateDuration * 60 * 60
        elif 'day' in dateType:
            self.periodDuration = dateDuration * 24 * 60 * 60
        else:
            assert False, 'date unsupported'

        #how many minutes, hours or days are inside a candle
        self.dateDuration = dateDuration

        self.timeAtBeginningOfHour = timeAtBeginningOfHour

        timeDifference = firstTick[1] - self.timeAtBeginningOfHour
        result = divmod(timeDifference, self.periodDuration)
        self.lastCandleAtPosition = result[0]

    def add(self, candle):

        if len(self.tempSection) == 0:
            self.tempSection.append(candle)
            self.internalData['ohlc']['o'] = candle[0]
            self.internalData['ohlc']['h'] = candle[0]
            self.internalData['ohlc']['l'] = candle[0]
            return

        timeDifference = candle[1] - self.timeAtBeginningOfHour
        result = divmod(timeDifference, self.periodDuration)
        if result[0] == self.lastCandleAtPosition:
            self.tempSection.append(candle)
        else:
            self.lastCandleAtPosition = result[0]
            self.internalData['durations'].append(self.tempSection.copy())
            self.allCandles.append(self.internalData.copy())

            self.internalData = {
                'ohlc': {'o': candle[0], 'h': candle[0], 'l': candle[0], 'c': 0},
                'durations': [],
                'isUptrend': True
            }
            self.tempSection.clear()
            # TODO: implement indexes for the received candles. No need co copy the data all the time

        if candle[0] > self.internalData['ohlc']['h']:
            self.internalData['ohlc']['h'] = candle[0]
            self.internalData['ohlc']['c'] = candle[0]
        elif candle[0] > self.internalData['ohlc']['l']:
            self.internalData['ohlc']['c'] = candle[0]

        if candle[0] < self.internalData['ohlc']['l']:
            self.internalData['ohlc']['l'] = candle[0]
            self.internalData['ohlc']['c'] = candle[0]

        if self.internalData['ohlc']['l'] < candle[0] < self.internalData['ohlc']['h']:
            self.internalData['ohlc']['c'] = candle[0]
