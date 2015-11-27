# -*- coding: utf-8 -*-

import ConfigParser
import csv
import json
import os

CURRENT_DIR = os.path.dirname(__file__)

CONFIG_FILE = os.path.join(CURRENT_DIR, '..', 'scraping.cfg')

def readConfig():
    config = ConfigParser.ConfigParser()
    config.read(CONFIG_FILE)
    return config

def setup_storage_path():
    config = readConfig()
    storage_path = os.path.join(CURRENT_DIR, '..', config.get('STORAGE','PATH'))
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

def save_detail_to_storage(file_name, data):
    config = readConfig()
    storage_path = os.path.join(CURRENT_DIR, '..', config.get('STORAGE','PATH'))
    file_path = os.path.join(storage_path, file_name)
    if not os.path.exists(file_path):
        setup_storage_path()

    with open(file_path, 'w') as f:
            json.dump(data, f)

def split_name(name):
	_split = name.split()
	return _split[0], _split[-1]