from time import mktime


class Interval:
    internalData = {
        'ohlc': {'o': 0, 'h': 0, 'l': 0, 'c': 0},
        'durations': [],
        'isUptrend': True
    }

    allCandles = []
    tempSection = []

    periodDuration = None
    dateDuration = None

    def __init__(self, dateType, dateDuration):
        if 'min' in dateType:
            self.periodDuration = dateDuration * 60
        elif 'hour' in dateType:
            self.periodDuration = dateDuration * 60 * 60
        elif 'day' in dateType:
            self.periodDuration = dateDuration * 24 * 60 * 60
        else:
            assert False, 'date unsupported'

        self.dateDuration = dateDuration

    def add(self, candle):

        if len(self.tempSection) == 0:
            self.tempSection.append(candle)
            self.internalData['ohlc']['o'] = candle[0]
            self.internalData['ohlc']['h'] = candle[0]
            self.internalData['ohlc']['l'] = candle[0]
            return

        if candle[1] - self.tempSection[0][1] < self.periodDuration:
            self.tempSection.append(candle)
        else:
            self.internalData['durations'].append(self.tempSection.copy())
            self.allCandles.append(self.internalData.copy())

            self.internalData = {
                'ohlc': {'o': 0, 'h': 0, 'l': 0, 'c': 0},
                'durations': [],
                'isUptrend': True
            }
            self.tempSection.clear()
            # TODO: implement indexes for the received candles. No need co copy the data all the time
            # TODO: implement dinamic period duration. Somtimes candles come with a slight delay, for example every 322s vs 300s. This can lead to big problems down the line

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