#!/usr/bin/env python

import argparse

import logging as logger
from database2xls import DB2XLS
from import_csv_to_database import CSV2DB
from start import start_from_database


parser = None


# def set_argparse():
#     global parser
#     parser = argparse.ArgumentParser(
#         description='Process CSV file and put it into database')
#     parser.add_argument(
#         '-n', '--name', help='name header value', required=True)
#     parser.add_argument(
#         '-c', '--city', help='city header value', required=True)
#     parser.add_argument(
#         '-s', '--state', help='state header value', required=True)
#     parser.add_argument(
#         '-a', '--all', help='all header value comma separated', required=True)
#     parser.add_argument(
#         '-f', '--file', help='csv file location', required=True)
#     parser.add_argument(
#         '--section', help='section name', required=True)

def parse_arguments():
    '''parse arguments'''

    parser = argparse.ArgumentParser(description="Process CSV file and put it into database")
    parser.add_argument(
        '--section', help='section name', required=True)
    result = parser.parse_args()
    return result


def import_csv_to_db(args):
    section = args.section
    logger.info("importing csv data to database")
    csv2db = CSV2DB(section)
    csv2db.save()
    logger.info("import successful")

    logger.info("parsing data from intellus")
    # remove number 5 to scrap all data
    start_from_database(section, 5)
    logger.info("parsing complete")

    logger.info("exporting from database to xls file")
    db2xls = DB2XLS(section)
    # provide actual name
    # db2xls.start("Jillian J Orlow")
    # group by name and perform for individual name
    db2xls.start()
    logger.info("exporting complete")


def start(args):
    # database = helper.get_database_object()
    import_csv_to_db(args)


if __name__ == '__main__':
    # set_argparse()
    args = parse_arguments()
    start(args)
