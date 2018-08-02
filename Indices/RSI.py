class RSI:
    RSIholder = {}
    initialHolder = {}
    smoothedHolder = {}

    def __init__(self, allCandles, lastProcessedIndex):
        self.allCandles = allCandles
        self.lastProcessedIndex = lastProcessedIndex

    def initiate(self, duration: int, metric: str):
        durationMetric = str(duration) + '-' + metric
        keyName = 'RSI-' + durationMetric
        self.lastProcessedIndex.update({keyName: 0})
        self.RSIholder.update({durationMetric: []})
        self.initialHolder.update({durationMetric: []})
        self.smoothedHolder.update({durationMetric: []})

    def __calculateRSI(self, smoothRSI: float) -> float:
        return (100 - (100 / 1 + smoothRSI))

    def __calculateSmoothedRS(self, metric: str, duration: int) -> float:
        downtrendSum, uptrendSum = self.__trendSums(duration, metric)

        # if the difference is positive, it is gain, otherwise a loss
        # the last candle is self.allCandles[-1], the candle before that is self.allCandles[-2]
        difference = self.allCandles[-1]['ohlc'][metric] - self.allCandles[-2]['ohlc'][metric]

        if difference > 0:
            up = difference
            down = 0
        else:
            up = 0
            down = difference

        above = ((uptrendSum * (duration - 1) + up) / duration)
        bellow = ((downtrendSum * (duration - 1) + down) / duration)

        return above / bellow

    # calculates the uptrend and downtrend streams for the last candles
    def __trendSums(self, duration: int, metric: str) -> (int, int):
        uptrendSum = 0
        downtrendSum = 0
        for pastCandle in self.allCandles[:duration]:
            if pastCandle['isUptrend']:
                uptrendSum += pastCandle['ohlc'][metric]
            else:
                downtrendSum += pastCandle['ohlc'][metric]
        return downtrendSum, uptrendSum

    # calculate the RSI of the desired duration and metric. By default c (close) is used.
    # math formulas calculated from http://cns.bu.edu/~gsc/CN710/fincast/Technical%20_indicators/Relative%20Strength%20Index%20(RSI).htm
    # Available options: o,h,l
    # for open, high, low
    def RSI(self, duration: int, metric='c'):
        length = len(self.allCandles)
        durationMetric = str(duration) + '-' + metric

        # not enough candles to calculate the RSI
        if length < duration:
            return

        # this candle has been processed already
        keyName = 'RSI-' + durationMetric
        if length == self.lastProcessedIndex[keyName]:
            return

        numberOfCalculatedRSIs = len(self.RSIholder[durationMetric])

        if numberOfCalculatedRSIs == 0:
            # the initial RSI
            downtrendSum, uptrendSum = self.__trendSums(duration, metric)
            initial = (uptrendSum / duration) / (downtrendSum / duration)
            self.initialHolder[durationMetric] = initial
            currentRSIValue = self.__calculateRSI(initial)
        else:
            # normal RSI
            smoothRSI = self.__calculateSmoothedRS(metric, duration)
            self.smoothedHolder[durationMetric] = smoothRSI
            currentRSIValue = self.__calculateRSI(smoothRSI)

        self.lastProcessedIndex[keyName] = length
        self.RSIholder[durationMetric].append(currentRSIValue)
        return currentRSIValue