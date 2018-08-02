import numpy as np

from Helpers.Calculations import Calculations

processedFolder = 'processed/'

# helper = Helper()
# helper.process_files(['USDCHF-2018-01.csv', 'USDCHF-2018-02.csv', 'USDCHF-2018-04.csv', 'USDCHF-2018-05.csv', 'USDCHF-2018-06.csv'])
numberOfRows = '10000'
fileName = 'USDCHF-2018-02.csv'
# helper.process_files([fileName], numberOfRows)
if numberOfRows != 'all':
    fileName = numberOfRows + '-' + fileName

data = np.load(processedFolder + fileName + '.npy')

fiveMin = Calculations('minute', 5)
fiveMin.RSI.initiate(5, 'c')
fiveMin.EMA.initiate(9, 'c')

i = 0
# simulate the candle ticking
for candle in data:
    fiveMin.add(candle, i)

    fiveMin.RSI.RSI(5, 'c')
    fiveMin.EMA.EMA(9, 'c')

    i += 1

print('asd')
