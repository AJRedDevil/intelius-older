# -*- coding: utf-8 -*-

import ConfigParser
import json
import os

from database import REThink

CURRENT_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(CURRENT_DIR, '..', 'scraping.cfg')
database = None


def readConfig():
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    return config


def setup_database():
    global database
    config = readConfig()
    host = config.get('DATABASE', 'host')
    port = config.get('DATABASE', 'port')
    db = config.get('DATABASE', 'database')
    table = config.get('DATABASE', 'table')

    database = REThink(db=None, host=host, port=port)

    database.create_database(db)
    database.use_database(db)

    database.create_table(table)


def get_database_object():
    global database
    if not database:
        setup_database()

    return database


def setup_storage_path():
    config = readConfig()
    storage_path = os.path.join(
        CURRENT_DIR, '..', config.get('STORAGE', 'PATH'))
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)


def save_detail_to_storage(section, file_name, data):
    config = readConfig()
    storage_path = os.path.join(
        CURRENT_DIR, '..', config.get('STORAGE', 'PATH'))

    file_path = os.path.join(storage_path, section)
    check_path(file_path)

    file_path = os.path.join(storage_path, section, file_name)
    if not os.path.exists(file_path):
        setup_storage_path()

    with open(file_path, 'w') as f:
        json.dump(data, f)

    database.insert(section, data)


def split_name(name):
    _split = name.split()
    return _split[0], _split[-1]


def check_path(path):
    '''
    checks if path is present,
    if not, create it.
    '''
    if not os.path.exists(path):
        os.makedirs(path)
