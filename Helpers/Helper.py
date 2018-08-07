from configparser import ConfigParser
from math import sqrt
import datetime
import numpy as np

class Helper:
    processedFolder = None

    def __init__(self, processedFolder):
        self.parser = ConfigParser()
        self.processedFolder = processedFolder

    def get_config_value(self, section, key, file='setupConfig.ini'):
        self.parser.read(self.processedFolder+'/'+file)
        return self.parser.get(section, key)

    def generate_fibonacci_for_n_elements(self, n):
        return ((1 + sqrt(5)) ** n - (1 - sqrt(5)) ** n) / (2 ** n * sqrt(5))

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

            np.save(self.processedFolder + file + '.npy', processedLines)

    def convert_to_correct_types(self, data):
        for row in data:
            row['o'] = float(row['o'])
            row['c'] = float(row['c'])
            row['d'] = datetime.datetime.strptime(row['d'], '%Y%m%d %H:%M:%S.%f').timetuple()

        return data
