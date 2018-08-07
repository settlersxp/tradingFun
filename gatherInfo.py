import os
from selenium import webdriver

from Setup.DatabaseSetup import DatabaseSetup
from Helpers.Helper import Helper

helper = Helper("Helpers")
database = DatabaseSetup(helper)
currencyPairs = ['EURUSD', 'EURJPY', 'EURCHF', 'EURNZD', 'USDCAD', 'USDNZD', 'USDJPY']

connection = database.create_connection()
database.create_database_with(connection)
database.create_tables_with(connection, currencyPairs)

if ('windows' in os.environ['OS'].lower()):
    chromeDriverPath = 'Setup/chromedriver.exe'
else:
    chromeDriverPath = 'Setup/chromedriver'

browser = webdriver.Chrome(executable_path=chromeDriverPath)
browser.get('https://www.tradingview.com/#signin')

# just to populate the holder, very lazy, very QA :)
oldValuesHolder = {}
for currencyPair in currencyPairs:
    oldValuesHolder[currencyPair] = 0

cssSelectorTemplate = '[symbol-short="{}"] .last-block'

while True:
    for currencyPair in currencyPairs:
        value = browser.find_element_by_css_selector(cssSelectorTemplate.format(currencyPair)).text
        if value != oldValuesHolder[currencyPair]:
            database.insertTick(value, connection, currencyPair)
            oldValuesHolder[currencyPair] = value