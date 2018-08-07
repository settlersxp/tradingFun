# https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:moving_average_convergence_divergence_macd
from Indices.EMA import EMA


class MACD:
    holder = {}
    shortDuration = 0
    mediumDuration = 0
    longDuration = 0
    metric = 'c'
    durationMetric = 0
    keyName = ''

    def __init__(self, allCandles, lastProcessedIndex, shortDuration, mediumDuration, longDuration, metric):
        self.allCandles = allCandles
        self.lastProcessedIndex = lastProcessedIndex
        self.shortDuration = shortDuration
        self.mediumDuration = mediumDuration
        self.longDuration = longDuration
        self.shortEMA = EMA(allCandles, lastProcessedIndex, shortDuration, metric)
        self.longEMA = EMA(allCandles, lastProcessedIndex, longDuration, metric)
        self.durationMetric = str(self.shortDuration) + '-' + str(self.mediumDuration) + '-' + str(
            self.longDuration) + '-' + self.metric
        self.keyName = 'MACD-' + self.durationMetric
        self.lastProcessedIndex.update({self.keyName: 0})
        self.holder.update({self.durationMetric: []})

    # MACD Line: (12-day EMA - 26-day EMA)
    # this means that the medium duration vs the long duration
    def macdLine(self):
        if len(self.allCandles) < self.longDuration:
            return None
        return self.shortEMA.SMA() - self.longEMA.SMA()

    # Signal Line: 9-day EMA of MACD Line
    def signalLine(self):
        if len(self.allCandles) < self.shortDuration:
            return None
        return self.shortEMA.SMA()

    # MACD Histogram: MACD Line - Signal Line
    def histogram(self, macdLine=None, signalLine=None):
        if macdLine is None:
            macdLine = self.macdLine()

        if signalLine is None:
            signalLine = self.signalLine()

        if macdLine is None or signalLine is None:
            return None

        return macdLine - signalLine

    def MACD(self):
        durationMetric = str(self.shortDuration) + '-' + str(self.mediumDuration) + '-' + str(
            self.longDuration) + '-' + self.metric
        signalLine = self.signalLine()
        macdLine = self.macdLine()
        histogram = self.histogram(macdLine=macdLine, signalLine=signalLine)
        currentMACD = {
            'signal': signalLine,
            'macd': macdLine,
            'histogram': histogram
        }
        self.holder[durationMetric].append(currentMACD)

        return currentMACD
