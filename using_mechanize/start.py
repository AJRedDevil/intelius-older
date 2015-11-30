# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import csv
import time
import helper
import traceback
import logging as log

from MechanizeBrowser import MechanizeBrowser


browser = MechanizeBrowser()
browser.start()

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DRIVER_PATH = os.path.join(CURRENT_DIR, '../bin', helper.readConfig().get('DRIVER','FILENAME'))

try:
    section='CSVFILE'
    file_path = os.path.join(CURRENT_DIR, '..', helper.readConfig().get('STORAGE','CSV_PATH'), "{0}.csv".format(helper.readConfig().get(section, 'FILENAME')))
    field_names = helper.readConfig().get(section,'FIELDNAMES').split(',')
    name=helper.readConfig().get(section,'NAME')
    city=helper.readConfig().get(section,'CITY')
    state=helper.readConfig().get(section,'STATE')
    with open(file_path, 'rU') as f:
        csv_reader = csv.DictReader(f, field_names)
        csv_reader.next()   # The first row is the header
        index = 1
        for row in csv_reader:
            first_name, last_name = helper.split_name(row[name])
            city_state = "{0} , {1}".format(row[city], row[state])

            try:
                browser.search(index, first_name, last_name, city_state)
                log.info("Parsed for First Name: '%s', Last Name: '%s' and City State: '%s' indexed: '%s'" % (first_name, last_name, city_state, index))
                time.sleep(1)
            except Exception, e:
                print str(e)
                print "Error Parsing for First Name: '%s', Last Name: '%s' and City State: '%s' indexed: '%s'" % (first_name, last_name, city_state, index)
                tb = traceback.format_exc()
                if tb:
                    print tb
            index += 1

except Exception, e:
    print str(e)
    tb = traceback.format_exc()
else:
    tb = "No error"
