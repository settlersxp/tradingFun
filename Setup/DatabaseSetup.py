import time

import pymysql

from Helpers.Database import Database


class DatabaseSetup:
    __config = None

    def __init__(self, helper):
        self.__config = Database(helper)

    def create_tables_with(self, connection, currencies):
        tables = {}

        for currency in currencies:
            tables['d_' + currency] = (
                    "CREATE TABLE `d_" + currency +
                    "` ( "
                    " `id` int(11) NOT NULL AUTO_INCREMENT, "
                    " `time` INT(11), "
                    " `tick` FLOAT(11,6), "
                    "  PRIMARY KEY (`id`)"
                    ") ENGINE=InnoDB"
            )

        cursor = connection.cursor()

        for name, ddl in tables.items():
            try:
                print("Creating table {}: ".format(name), end='')
                cursor.execute(ddl)
            except pymysql.InternalError as err:
                if err.args[0] == 1050:
                    print("Table " + name + " already exists.")
                else:
                    print("Database creation error: %s" % err.args[1])
            else:
                print("OK")
        cursor.close()

    def create_connection(self):
        try:
            connection = pymysql.connect(host="localhost", user=self.__config.user, password=self.__config.password,
                                         port=int(self.__config.port),
                                         db=self.__config.db_name)
        except pymysql.InternalError as err:
            if err.args[0] == 1049:
                connection = pymysql.connect(host="localhost", user=self.__config.user, password=self.__config.password,
                                             port=int(self.__config.port))
            else:
                print("Database connection failed: %s" % err.args[1])

        assert connection is not None, 'Database connection could not be created'

        connection.autocommit(True)
        return connection

    def create_database_with(self, connection):
        cursor = connection.cursor()

        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self.__config.db_name))
        except pymysql.Error as err:
            if err.args[0] == 1007:
                print("Database exists, moving on!")
            else:
                print("Failed creating database: {}".format(err))
                cursor.close()
                exit(1)

        cursor.close()
        return connection

    def getAllTicksForPair(self, connection, currencies_pair):
        query = "SELECT tick, time FROM " + \
                self.__config.db_name + ".d_" + currencies_pair
        cursor = connection.cursor()
        cursor.execute(query)

        return cursor.fetchall()

    def getLastTickForPair(self, connection, currencies_pair):
        query = "SELECT tick, time FROM " + \
                self.__config.db_name + ".d_" + currencies_pair + \
                " ORDER BY id DESC LIMIT 1"
        cursor = connection.cursor()
        cursor.execute(query)

        return cursor.fetchall()

    def insertTick(self, newTitle, connection, currencyPair):
        query = 'INSERT INTO '+'`d_'+currencyPair+'` (time, tick) VALUES ({},{})'.format(time.time(), newTitle)

        cursor = connection.cursor()
        cursor.execute(query)
