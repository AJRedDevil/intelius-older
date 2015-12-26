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
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    # test
    logger.info('test log')


class REThink():
    rethinkdb = rethinkdb

    def __init__(self, db=None, host="localhost", port=28015):
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
        rethinkdb.db(database_name)

    def create_table(self, table_name):
        table_list = rethinkdb.table_list().run()
        if table_name in table_list:
            logger.debug("table already exists")
            return

        response = rethinkdb.table_create(table_name).run()
        logger.debug(response)

    def insert(self, table_name, data):
        logger.debug("insert data to table %s" % table_name)
        response = rethinkdb.table(table_name).insert(data).run()
        logger.debug(response)

    def read(self, table_name, condition=None):
        logger.debug("reading data from table %s" % table_name)
        if condition:
            cursor = rethinkdb.table(table_name).filter(condition).run()
            return cursor

        cursor = rethinkdb.table(table_name).run()
        return cursor

    def read_one(self, table_name, id):
        cursor = rethinkdb.table(table_name).get(id).run()
        return cursor

    def update(self, table_name, data):
        pass

    def delete(self, table_name):
        rethinkdb.table(table_name).delete()

    def delete_all(self, table_name):
        rethinkdb.table(table_name).delete().run()

# def rethink():
#     r.connect("localhost", 28015).repl()
#     print r.db("test").table_create("authors").run()


def postgres():
    import psycopg2
    import sys

    def create(cursor, schema):
        try:
            cursor.execute(schema)
        except psycopg2.DatabaseError, e:
            print str(e)

    def insert(cursor, data):
        cursor.execute(data)

    def start():
        try:
            con = psycopg2.connect(database='intelius', user='bunkdeath')

            cur = con.cursor()
            query = "CREATE TABLE Cars(Id INTEGER PRIMARY KEY, Name VARCHAR(20), Price INT)"
            create(cur, query)

            insert(cur, "INSERT INTO Cars VALUES(1,'Audi',52642)")
            insert(cur, "INSERT INTO Cars VALUES(2,'Mercedes',57127)")
            insert(cur, "INSERT INTO Cars VALUES(3,'Skoda',9000)")
            insert(cur, "INSERT INTO Cars VALUES(4,'Volvo',29000)")
            insert(cur, "INSERT INTO Cars VALUES(5,'Bentley',350000)")
            insert(cur, "INSERT INTO Cars VALUES(6,'Citroen',21000)")
            insert(cur, "INSERT INTO Cars VALUES(7,'Hummer',41400)")
            insert(cur, "INSERT INTO Cars VALUES(8,'Volkswagen',21600)")

            con.commit()

        except psycopg2.DatabaseError, e:
            print 'Error %s' % e
            sys.exit(1)

        finally:
            if con:
                con.close()


if __name__ == '__main__':
    database = "bunkdeath"
    table = "bunkdeath"
    configure_logging()
    r = REThink(database)
    r.create_database(database)
    r.create_table(table)
    # r.insert(table, [
    #     {
    #         "name": "William Adama",
    #         "tv_show": "Battlestar Galactica",
    #         "posts": [{
    #             "title": "Decommissioning speech",
    #             "content": "The Cylon War is long over..."
    #         }, {
    #             "title": "We are at war",
    #             "content": "Moments ago, this ship received..."
    #         }, {
    #             "title": "The new Earth",
    #             "content": "The discoveries of the past few days..."
    #         }]
    #     },
    #     {
    #         "name": "Laura Roslin",
    #         "tv_show": "Battlestar Galactica",
    #         "posts": [{
    #             "title": "The oath of office",
    #             "content": "I, Laura Roslin, ..."
    #         }, {
    #             "title": "They look like us",
    #             "content": "The Cylons have the ability..."
    #         }]
    #     }, {
    #         "name": "Jean-Luc Picard",
    #         "tv_show": "Star Trek TNG",
    #         "posts": [{
    #             "title": "Civil rights",
    #             "content": "There are some words I've known since..."
    #         }]
    #     }
    # ])

    cursor = r.read(table, rethinkdb.row["posts"].count() > 0)
    cursor = r.read(table)
    for data in cursor:
        print
        print data

    print "-"*158
    print r.read_one(table, "5c365a7d-9f8d-4f7e-9269-74b72a05990b")
    # # r.delete_all("hello")
    # # postgres()
