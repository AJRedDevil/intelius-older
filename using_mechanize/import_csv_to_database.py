#!/usr/bin/env python

import csv
import argparse

import helper

parser = None

header_table = "csv_header"


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
    def __init__(self, args):
        super(CSV2DB, self).__init__()
        self.args = args

    def save(self):
        database = helper.get_database_object()

        name = self.args.name
        city = self.args.city
        state = self.args.state
        section = self.args.section
        section_name = "%s_input" % self.args.section
        file_path = self.args.file

        all_fields = [key.strip() for key in self.args.all.split(",")]

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

        database.create_table(section)
        database.create_table(section_name)

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
