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

    def process_files(self, files):
        for file in files:
            processedLines = self.prepare_file(file)
            np.save(processedFolder + file + '.npy', processedLines)

    def convert_to_correct_types(self, data):
        for row in data:
            row['o'] = float(row['o'])
            row['c'] = float(row['c'])
            row['d'] = datetime.datetime.strptime(row['d'], '%Y%m%d %H:%M:%S.%f').timetuple()

        return data


class Interval:
    internalData = {
        'ohlc': {'o':0, 'h':0, 'l':0, 'c':0},
        'durations': [],
        'isUptrend': True
    }
    currentInterval = []

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
        if len(self.currentInterval) == 0:
            self.currentInterval.append(candle)
            self.internalData['ohlc']['o'] = candle['o']
            self.internalData['ohlc']['c'] = candle['c']

            if candle['c'] > candle['o']:
                #uptrend
                self.internalData['ohlc']['h'] = candle['c']
                self.internalData['ohlc']['l'] = candle['o']
            else:
                #downtrend
                self.internalData['isUptrend'] = False
                self.internalData['ohlc']['l'] = candle['c']
                self.internalData['ohlc']['h'] = candle['o']

            return

        if mktime(candle['d']) - mktime(self.currentInterval[0]['d']) < self.periodDuration:
            self.currentInterval.append(candle)
        else:
            self.internalData['durations'].append(self.currentInterval.copy())
            self.currentInterval.clear()
            self.currentInterval.append(candle)
            #TODO: implement dinamic period duration. Somtimes candles come with a slight delay, for example every 322s vs 300s. This can lead to big problems down the line
            #TODO: what happens when a new candle is created? What information gets copied?

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


# helper = Helper()
# helper.process_files(['USDCHF-2018-01.csv', 'USDCHF-2018-02.csv', 'USDCHF-2018-04.csv', 'USDCHF-2018-05.csv', 'USDCHF-2018-06.csv'])
# helper.process_files(['USDCHF-2018-01.csv'])
data = np.load(processedFolder + 'min-USDCHF-2018-01.csv.npy')

fiveMin = Interval('minute', 5)
tenMin = Interval('minute', 10)
fifteenMin = Interval('minute', 15)
oneHour = Interval('hour', 1)

# simulate the candle ticking
for candle in data:
    fiveMin.add(candle)
