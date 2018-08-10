import time
from datetime import datetime

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

# The next 3 lines of code are needed in order to figure out when the time should start and end.
# for example:
# we start the program at 13:03:02 (after we return from Kebab)
# all the candles until 13:05:00 must go in the first interval
# all the candles after 13:05:00 must go in the second interval
# we need some magic to find the :05. Because if we take in consideration the start time of the program 13:03 and add 5 minutes,
# our first candle would end at 13:08 instead of 13:05
currentTimestamp = datetime.fromtimestamp(allTicks[0][1])
stringAtBeginningOfHour = "{}:{}:{} {}".format(currentTimestamp.year, currentTimestamp.month,
                                               currentTimestamp.day, currentTimestamp.hour)
timeAtBeginningOfHour = time.mktime(datetime.strptime(stringAtBeginningOfHour, "%Y:%m:%d %H").timetuple())

#The initialization of the 5 minutes candle and some of the indicators, as an example
fiveMin = Calculations('minute', 15, allTicks[0], timeAtBeginningOfHour)
fiveRSI = RSI(fiveMin.allCandles, fiveMin.lastProcessedIndex, 5, 'c')
fiveEMA = EMA(fiveMin.allCandles, fiveMin.lastProcessedIndex, 9, 'c')
fiveMACD = MACD(fiveMin.allCandles, fiveMin.lastProcessedIndex, 9, 16, 26, 'c')

#the 'lastProcessedCandle' variable is used to determine if we need to calculate the indices again. It is not the final
# implementation. We need a 'lastProcessedCandle' for each individual time interval.
lastProcessedCandle = 0

for tick in allTicks:
    #example of how to add ticks to specific candles
    fiveMin.add(tick)

    if len(fiveMin.allCandles) == lastProcessedCandle:
        continue

    localRSI = fiveRSI.RSI()
    localEMA = fiveEMA.EMA()
    localMACD = fiveMACD.MACD()
    lastProcessedCandle = len(fiveMin.allCandles)

print('Put breakpoint here for end result :)')
