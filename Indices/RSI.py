class RSI:
    holder = {}
    initialHolder = {}
    smoothedHolder = {}
    metric = ''
    duration = 0
    previousGain = 0
    previousLoss = 0

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

    def calculateRSI(self, smoothRSI: float) -> float:
        return (100 - (100 / (1 + smoothRSI)))

    def calculateSmoothedRS(self, previousAverageGain: float, previousAverageLoss: float) -> float:
        currentGain = 0
        currentLoss = 0

        if self.allCandles[-1]['ohlc'][self.metric] > self.allCandles[-2]['ohlc'][self.metric]:
            currentGain = self.allCandles[-1]['ohlc'][self.metric]-self.allCandles[-2]['ohlc'][self.metric]
        else:
            currentLoss = self.allCandles[-2]['ohlc'][self.metric]-self.allCandles[-1]['ohlc'][self.metric]

        above = ((previousAverageGain*(self.duration - 1))+currentGain)/self.duration
        bellow = ((previousAverageLoss*(self.duration - 1))+currentLoss)/self.duration

        return above / bellow

    # calculates the uptrend and downtrend streams for the last candles
    def trendSums(self) -> (int, int):
        uptrendSum = 0
        downtrendSum = 0
        for pastCandle in self.allCandles[-self.duration:]:
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
        downtrendSum, uptrendSum = self.trendSums()
        averageGain = uptrendSum/self.duration
        averageLoss = downtrendSum/self.duration

        if numberOfCalculatedRSIs == 0:
            # the initial RSI
            initialRS = averageGain / averageLoss
            self.initialHolder[self.durationMetric] = initialRS
            currentRSIValue = self.calculateRSI(initialRS)
        else:
            # normal RSI
            smoothRSI = self.calculateSmoothedRS(self.previousGain, self.previousLoss)
            self.smoothedHolder[self.durationMetric] = smoothRSI
            currentRSIValue = self.calculateRSI(smoothRSI)

        self.previousGain = averageGain
        self.previousLoss = averageLoss
        self.lastProcessedIndex[self.keyName] = length
        self.holder[self.durationMetric].append(currentRSIValue)
        return currentRSIValue
