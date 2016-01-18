#!/usr/bin/env python

import argparse
import csv
import os


import helper

parser = None

header_table = "csv_header"

CURRENT_DIR = os.path.dirname(__file__)


def set_argparse():
    global parser
    parser = argparse.ArgumentParser(
        description='Process CSV file and put it into database')
    parser.add_argument(
        '-n', '--name', help='name header value', required=True)
    parser.add_argument(
        '-c', '--city', help='city header value', required=True)
    parser.add_argument(
        '-s', '--state', help='state header value', required=True)
    parser.add_argument(
        '-a', '--all', help='all header value comma separated', required=True)
    parser.add_argument(
        '-f', '--file', help='csv file location', required=True)
    parser.add_argument(
        '--section', help='section name', required=True)


class CSV2DB(object):
    """docstring for CSV2DB"""
    def __init__(self, section):
        super(CSV2DB, self).__init__()
        self.section = section

    def save(self):
        database = helper.get_database_object()

        config = helper.readConfig()
        name = config.get(self.section, 'NAME')
        city = config.get(self.section, 'CITY')
        state = config.get(self.section, 'STATE')
        section = self.section
        section_name = "%s_input" % self.section
        file_name = config.get(self.section, 'FILENAME')

        all_fields = [key.strip() for key in config.get(self.section, 'ALL_FIELD').split(",")]

        data = {
            "name": section_name,
            "headers": {
                "name": name,
                "city": city,
                "state": state,
                "all_fields": all_fields
            }
        }

        database.create_table(header_table)
        database.insert(header_table, data)

        database.create_table(self.section)
        database.create_table(section_name)

        csv_path = os.path.join(CURRENT_DIR, '..', config.get('STORAGE', 'CSV_PATH'))
        file_path = os.path.join(csv_path, file_name)
        with open(file_path, 'rU') as f:
            csv_reader = csv.DictReader(f, all_fields)
            csv_reader.next()   # The first row is the header
            for row in csv_reader:
                database.insert(section_name, row)


if __name__ == '__main__':
    set_argparse()
    args = parser.parse_args()
    csv2db = CSV2DB(args)
    csv2db.start(args)

# sample command
# ./using_mechanize/import_csv_to_database.py -n "Cash Buyer Name" -c "Cash Buyer City" -s "Cash Buyer State" -a "Cash Buyer Name,Cash Buyer Address,Cash Buyer City,Cash Buyer State,Cash Buyer Zip" --section BALTIMORE --file using_mechanize/Baltimore\ City\ -\ Cash\ Buyers_Sample.csv
