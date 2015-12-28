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
        '-f', '--firstname', help='first name header value', required=True)
    parser.add_argument(
        '-l', '--lastname', help='last name header value', required=True)
    parser.add_argument(
        '-c', '--city', help='city header value', required=True)
    parser.add_argument(
        '-s', '--state', help='state header value', required=True)
    parser.add_argument(
        '-a', '--all', help='all header value comma separated', required=True)
    parser.add_argument(
        '--file', help='csv file location', required=True)
    parser.add_argument(
        '--section', help='section name', required=True)


def start(args):
    database = helper.get_database_object()

    first_name = args.firstname
    last_name = args.lastname
    city = args.city
    state = args.state
    section_name = args.section
    file_path = args.file

    all_fields = [key.strip() for key in args.all.split(",")]

    data = {
        "name": section_name,
        "headers": {
            "first_name": first_name,
            "last_name": last_name,
            "city": city,
            "state": state,
            "all_fields": all_fields
        }
    }

    database.create_table(header_table)
    database.insert(header_table, data)

    database.create_table(section_name)

    with open(file_path, 'rU') as f:
        csv_reader = csv.DictReader(f, all_fields)
        print csv_reader.next()   # The first row is the header
        for row in csv_reader:
            database.insert(section_name, row)


if __name__ == '__main__':
    set_argparse()
    args = parser.parse_args()
    start(args)
