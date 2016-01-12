#!/usr/bin/env python

import rethinkdb
import logging

logger = None


def configure_logging():
    global logger

    # create logger with 'intelius'
    logger = logging.getLogger('intelius')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('intelius.log')
    fh.setLevel(logging.DEBUG)
    # create console handler which logs even debug messages
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)


class REThink():
    rethinkdb = rethinkdb

    def __init__(self, db=None, host="localhost", port=28015):
        if not logger:
            configure_logging()

        self.host = host
        self.port = port
        self.db = db

        rethinkdb.connect(self.host, self.port).repl()
        if db:
            rethinkdb.connect(self.host, self.port, self.db).repl()

    def __database_exists(self, database_name):
        db_list = rethinkdb.db_list().run()
        if database_name in db_list:
            logger.debug("database exists")
            return True

        logger.debug("database does not exists")
        return False

    def create_database(self, database_name):
        if self.__database_exists(database_name):
            return

        logger.debug("databae '%s' created" % database_name)
        rethinkdb.db_create(database_name).run()

    def use_database(self, database_name):
        self.db = database_name
        rethinkdb.db(database_name)

    def create_table(self, table_name):
        table_list = rethinkdb.db(self.db).table_list().run()
        if table_name in table_list:
            logger.debug("table already exists")
            return

        response = rethinkdb.db(self.db).table_create(table_name).run()
        logger.debug(response)

    def insert(self, table_name, data):
        logger.debug("insert data to table %s" % table_name)
        response = rethinkdb.db(self.db).table(table_name).insert(data).run()
        logger.debug(response)

    def read(self, table_name, condition=None):
        logger.debug("reading data from table %s" % table_name)
        if condition:
            cursor = rethinkdb.db(self.db).table(
                table_name).filter(condition).run()
            return cursor

        cursor = rethinkdb.db(self.db).table(table_name).run()
        return cursor

    def read_one(self, table_name, id):
        cursor = rethinkdb.db(self.db).table(table_name).get(id).run()
        return cursor

    def update(self, table_name, data):
        pass

    def delete(self, table_name):
        rethinkdb.db(self.db).table(table_name).delete()

    def delete_all(self, table_name):
        rethinkdb.db(self.db).table(table_name).delete().run()
