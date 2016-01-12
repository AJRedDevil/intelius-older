#!/usr/bin/env python

import argparse
import subprocess

import logging as logger
from database2xls import DB2XLS
from import_csv_to_database import CSV2DB
from start import start_from_database


parser = None


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


def import_csv_to_db(args):
    section = args.section
    logger.info("importing csv data to database")
    csv2db = CSV2DB(args)
    csv2db.save()
    logger.info("import successful")

    logger.info("parsing data from intellus")
    start_from_database(section, 5)
    logger.info("parsing complete")

    logger.info("exporting from database to xls file")
    db2xls = DB2XLS(section)
    # provide actual name
    db2xls.start("Sang-Jae J Lee")
    logger.info("exporting complete")


def start(args):
    # database = helper.get_database_object()
    import_csv_to_db(args)


if __name__ == '__main__':
    set_argparse()
    args = parser.parse_args()
    start(args)
