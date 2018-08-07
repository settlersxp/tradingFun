#https://www.dummies.com/personal-finance/investing/stocks-trading/how-to-calculate-exponential-moving-average-in-trading/
#https://sciencing.com/calculate-exponential-moving-averages-8221813.html
class EMA:
    EMAHolder = {}
    multiplicators = {}
    metric = ''
    duration = 0
    durationMetric = ''
    keyName = ''

    def __init__(self, allCandles, lastProcessedIndex, duration: int, metric: str):
        self.duration = duration
        self.metric = metric
        self.allCandles = allCandles
        self.lastProcessedIndex = lastProcessedIndex
        self.durationMetric = str(duration) + '-' + metric
        self.keyName = 'EMA-' + self.durationMetric
        self.lastProcessedIndex.update({self.keyName: 0})
        self.multiplicators.update({self.durationMetric: self.SMA_multiplicator()})
        self.EMAHolder.update({self.durationMetric: []})

    # calculates Simple Moving Average
    # 10 period sum / 10
    def SMA(self) -> float:
        sum = 0
        for candle in self.allCandles[:self.duration]:
            sum += candle['ohlc'][self.metric]

        return sum / self.duration

    # it is used in order to emphasize the newer candles of the older
    # Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
    def SMA_multiplicator(self) -> float:
        return (2 / (self.duration + 1))

    # https://github.com/patharanordev/ema
    # EMA - Estimated moving average
    # EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day).
    def EMA(self):
        length = len(self.allCandles)

        if length < self.duration:
            return

        if length == self.lastProcessedIndex[self.keyName]:
            return

        numberOfCalculatedEMAs = len(self.EMAHolder[self.durationMetric])

        #the initial EMA
        if numberOfCalculatedEMAs == 0:
            prevDayValue = self.SMA()

            self.EMAHolder[self.durationMetric].append(prevDayValue)

        finalValue = (self.allCandles[-1]['ohlc'][self.metric] - self.EMAHolder[self.durationMetric][-1]) * self.multiplicators[self.durationMetric] + self.EMAHolder[self.durationMetric][-1]

        self.lastProcessedIndex[self.keyName] = length
        self.EMAHolder[self.durationMetric].append(finalValue)
        return finalValue

