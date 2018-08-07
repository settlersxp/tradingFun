class RSI:
    holder = {}
    initialHolder = {}
    smoothedHolder = {}
    metric = ''
    duration = 0

    def __init__(self, allCandles, lastProcessedIndex, duration: int, metric: str):
        self.allCandles = allCandles
        self.lastProcessedIndex = lastProcessedIndex
        self.metric = metric
        self.duration = duration
        self.durationMetric = str(self.duration) + '-' + self.metric
        self.keyName = 'RSI-' + self.durationMetric
        self.lastProcessedIndex.update({self.keyName: 0})
        self.holder.update({self.durationMetric: []})
        self.initialHolder.update({self.durationMetric: []})
        self.smoothedHolder.update({self.durationMetric: []})

    def __calculateRSI(self, smoothRSI: float) -> float:
        return (100 - (100 / 1 + smoothRSI))

    def __calculateSmoothedRS(self) -> float:
        downtrendSum, uptrendSum = self.__trendSums()

        # if the difference is positive, it is gain, otherwise a loss
        # the last candle is self.allCandles[-1], the candle before that is self.allCandles[-2]
        difference = self.allCandles[-1]['ohlc'][self.metric] - self.allCandles[-2]['ohlc'][self.metric]

        if difference > 0:
            up = difference
            down = 0
        else:
            up = 0
            down = difference

        above = ((uptrendSum * (self.duration - 1) + up) / self.duration)
        bellow = ((downtrendSum * (self.duration - 1) + down) / self.duration)

        return above / bellow

    # calculates the uptrend and downtrend streams for the last candles
    def __trendSums(self) -> (int, int):
        uptrendSum = 0
        downtrendSum = 0
        for pastCandle in self.allCandles[:self.duration]:
            if pastCandle['isUptrend']:
                uptrendSum += pastCandle['ohlc'][self.metric]
            else:
                downtrendSum += pastCandle['ohlc'][self.metric]
        return downtrendSum, uptrendSum

    # calculate the RSI of the desired duration and metric. By default c (close) is used.
    # math formulas calculated from http://cns.bu.edu/~gsc/CN710/fincast/Technical%20_indicators/Relative%20Strength%20Index%20(RSI).htm
    # Available options: o,h,l
    # for open, high, low
    def RSI(self):
        length = len(self.allCandles)

        # not enough candles to calculate the RSI
        if length < self.duration:
            return

        # this candle has been processed already
        if length == self.lastProcessedIndex[self.keyName]:
            return

        numberOfCalculatedRSIs = len(self.holder[self.durationMetric])

        if numberOfCalculatedRSIs == 0:
            # the initial RSI
            downtrendSum, uptrendSum = self.__trendSums()
            initial = (uptrendSum / self.duration) / (downtrendSum / self.duration)
            self.initialHolder[self.durationMetric] = initial
            currentRSIValue = self.__calculateRSI(initial)
        else:
            # normal RSI
            smoothRSI = self.__calculateSmoothedRS()
            self.smoothedHolder[self.durationMetric] = smoothRSI
            currentRSIValue = self.__calculateRSI(smoothRSI)

        self.lastProcessedIndex[self.keyName] = length
        self.holder[self.durationMetric].append(currentRSIValue)
        return currentRSIValue
