#https://www.dummies.com/personal-finance/investing/stocks-trading/how-to-calculate-exponential-moving-average-in-trading/
#https://sciencing.com/calculate-exponential-moving-averages-8221813.html
class EMA:
    EMAHolder = {}
    multiplicators = {}

    def __init__(self, allCandles, lastProcessedIndex):
        self.allCandles = allCandles
        self.lastProcessedIndex = lastProcessedIndex

    # calculates Simple Moving Average
    # 10 period sum / 10
    def SMA(self, duration: int, metric='c') -> float:
        sum = 0
        for candle in self.allCandles[:duration]:
            sum += candle[metric]

        return sum / duration

    # it is used in order to emphasize the newer candles of the older
    # Multiplier: (2 / (Time periods + 1) ) = (2 / (10 + 1) ) = 0.1818 (18.18%)
    def SMA_multiplicator(self, duration: int) -> float:
        return (2 / (duration + 1))

    # https://github.com/patharanordev/ema
    # EMA - Estimated moving average
    # EMA: {Close - EMA(previous day)} x multiplier + EMA(previous day).
    def EMA(self, duration, metric):
        length = len(self.allCandles)

        if length < duration:
            return

        durationMetric = str(duration) + '-' + metric
        keyName = 'EMA-' + durationMetric
        existingEmas = len(self.lastProcessedIndex[keyName])

        if existingEmas == 0:
            prevDayValue = self.SMA(duration, metric)
            self.lastProcessedIndex[keyName] = length
            self.EMAHolder[keyName].append(prevDayValue)

        finalValue = (self.allCandles[metric] - self.EMAHolder[keyName][:-1]) * \
                     self.multiplicators[durationMetric] + \
                     self.EMAHolder[keyName][:-1]

        self.EMAHolder[keyName].append(finalValue)
        return finalValue

    def initiate(self, duration: int, metric: str):
        durationMetric = str(duration) + '-' + metric
        keyName = 'EMA-' + durationMetric
        self.lastProcessedIndex.update({keyName: 0})
        self.multiplicators.update({durationMetric: self.SMA_multiplicator(duration)})
        self.EMAHolder.update({durationMetric: []})