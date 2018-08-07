from Helpers.Calculations import Calculations
from Helpers.Helper import Helper
from Indices.EMA import EMA
from Indices.MACD import MACD
from Indices.RSI import RSI
from Setup.DatabaseSetup import DatabaseSetup

processedFolder = 'processed/'

helper = Helper("Helpers")
database = DatabaseSetup(helper)
currencyPairs = ['EURUSD', 'EURJPY', 'EURCHF', 'EURNZD', 'USDCAD', 'USDNZD', 'USDJPY']

connection = database.create_connection()

allTicks = database.getAllTicksForPair(connection, currencyPairs[0])

fiveMin = Calculations('minute', 5)
fiveRSI = RSI(fiveMin.allCandles, fiveMin.lastProcessedIndex, 5,'c')

fiveEMA = EMA(fiveMin.allCandles, fiveMin.lastProcessedIndex, 9, 'c')

fiveMACD = MACD(fiveMin.allCandles, fiveMin.lastProcessedIndex, 1, 3, 5, 'c')
lastProcessedCandle = 0

i = 0


for candle in allTicks:
    fiveMin.add(candle)

    if len(fiveMin.allCandles) == lastProcessedCandle:
        continue

    localRSI = fiveRSI.RSI()
    localEMA = fiveEMA.EMA()
    localMACD = fiveMACD.MACD()
    lastProcessedCandle = len(fiveMin.allCandles)


print('asd')
