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

    def add(self, candle, index):
        if len(self.tempSection) == 0:
            self.tempSection.append(candle)
            self.internalData['ohlc']['o'] = candle['o']
            self.internalData['ohlc']['c'] = candle['c']

            if candle['c'] > candle['o']:
                # uptrend
                self.internalData['ohlc']['h'] = candle['c']
                self.internalData['ohlc']['l'] = candle['o']
            else:
                # downtrend
                self.internalData['isUptrend'] = False
                self.internalData['ohlc']['l'] = candle['c']
                self.internalData['ohlc']['h'] = candle['o']

            return

        if mktime(candle['d']) - mktime(self.tempSection[0]['d']) < self.periodDuration:
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
            # TODO: what happens when a new candle is created? What information gets copied?

        # update the new closing, this happens always
        self.internalData['ohlc']['c'] = candle['c']
        # calculate the new high
        if candle['c'] > self.internalData['ohlc']['h']:
            self.internalData['ohlc']['h'] = candle['c']
        if self.internalData['isUptrend']:
            # calculate the new low
            if candle['o'] < self.internalData['ohlc']['l']:
                self.internalData['ohlc']['l'] = candle['o']
            # determine the trend reversal
            if candle['c'] < self.internalData['ohlc']['o']:
                self.internalData['isUptrend'] = False
        else:
            # calculate the new low
            if candle['c'] < self.internalData['ohlc']['l']:
                self.internalData['ohlc']['l'] = candle['c']
            # determine the trend reversal
            if candle['c'] < self.internalData['ohlc']['o']:
                self.internalData['isUptrend'] = True

        return