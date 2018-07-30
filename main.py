from time import mktime

import numpy as np

import datetime

processedFolder = 'processed/'


class Helper:
    def prepare_file(self, fileName):
        lines = []
        processedLines = []

        with open(fileName) as f:
            lines.extend(f.read().splitlines())

        for line in lines:
            columns = line.split(',')
            dateValue = datetime.datetime.strptime(columns[1], '%Y%m%d %H:%M:%S.%f').timetuple()
            openValue = float(columns[2])
            closeValue = float(columns[3])

            processedLines.append({'d': dateValue, 'o': openValue, 'c': closeValue})

        return processedLines

    def process_files(self, files, numberOfRows='all'):
        for file in files:
            processedLines = self.prepare_file(file)
            if numberOfRows != 'all':
                processedLines = self.prepare_file(file)[:int(numberOfRows)]
                file = numberOfRows + '-' + file

            np.save(processedFolder + file + '.npy', processedLines)

    def convert_to_correct_types(self, data):
        for row in data:
            row['o'] = float(row['o'])
            row['c'] = float(row['c'])
            row['d'] = datetime.datetime.strptime(row['d'], '%Y%m%d %H:%M:%S.%f').timetuple()

        return data


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


class Calculations(Interval):
    __lastProcessedIndex = {}
    RSIholder = {}

    def __init__(self, dateType, dateDuration):
        super().__init__(dateType, dateDuration)

    def add(self, candle, index):
        Interval.add(self, candle, index)
        self.RSI(5)

    def __calculateRSI(self, smoothRSI: float) -> float:
        return (100 - (100 / 1 + smoothRSI))

    def __calculateSmoothedRS(self, metric, duration):
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

    # calculate the RSI of the desired duration and metric. By default c (close) is used.
    # Available options: o,h,l
    # for open, high, low
    def RSI(self, duration: int, metric='c'):
        length = len(self.allCandles)

        # the initial RSI
        if length == duration:
            downtrendSum, uptrendSum = self.__trendSums(duration, metric)

            initial = (uptrendSum / duration) / (downtrendSum / duration)
            self.RSIholder[str(duration) + '-' + metric] = {
                'lastIndex': length,
                'initial': initial,
                'current': self.__calculateRSI(initial),
                'smoothed': self.__calculateSmoothedRS(metric, duration),
                'historical': []
            }
            return

        if length > duration:
            object = self.RSIholder[str(duration) + '-' + metric]
            object['smoothed'] = self.__calculateSmoothedRS(metric, duration)
            object['current'] = self.__calculateRSI(object['smoothed'])
            object['historical'].append(object['current'])
            object['lastIndex'] = length

            return

        #TODO: It should not process this if there is no new candle

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


helper = Helper()
# helper.process_files(['USDCHF-2018-01.csv', 'USDCHF-2018-02.csv', 'USDCHF-2018-04.csv', 'USDCHF-2018-05.csv', 'USDCHF-2018-06.csv'])
numberOfRows = '10000'
fileName = 'USDCHF-2018-02.csv'
# helper.process_files([fileName], numberOfRows)
if numberOfRows != 'all':
    fileName = numberOfRows + '-' + fileName

data = np.load(processedFolder + fileName + '.npy')

fiveMin = Calculations('minute', 5)

i = 0
# simulate the candle ticking
for candle in data:
    fiveMin.add(candle, i)
    i += 1

print('asd')
