#!/usr/bin/env python

import xlsxwriter

import helper

from database import REThink, configure_logging
configure_logging()


class XLSWriter:

    def __init__(self, filename, row=None, column=None):
        self.filename = filename
        self.row = row or 0
        self.column = column or 0

        self.matched_address = None
        self.header_data = [
            "NAME", "AGE", "ADDRESSES", "PHONE NUMBERS", "MOBILE NUMBERS", "EMAILS"]

        self.workbook = xlsxwriter.Workbook(self.filename)
        self.worksheet = self.workbook.add_worksheet()

        self.mobile = self.workbook.add_format(
            {'font_color': 'white', 'bg_color': 'black'})
        self.header = self.workbook.add_format({'bold': True})
        self.width = {
            "name": 10,
            "age": 10,
            "addresses": 50,
            "matched_address": 50,
            "phone_nos": 10,
            "mobile": 10,
            "emails": 10
        }

    def write_header(self):
        column = self.column
        for header in self.header_data:
            self.worksheet.write(self.row, column, header, self.header)
            column += 1

        self.row += 1

    def write_row(self, row_data):
        column = self.column

        for key, value in row_data:
            if key == "matched_address":
                if not self.matched_address:
                    self.matched_address = value

            style = self.workbook.add_format()
            if key in ["mobile", "matched_address"] and value:
                style = self.mobile

            if key == "addresses" and value == self.matched_address:
                style = self.mobile

            if key == "matched_address":
                continue

            self.worksheet.set_column(column, column, self.width.get(key, 20))
            self.worksheet.write(self.row, column, value, style)
            column += 1
        self.row += 1

    def blank_row(self):
        self.write_row([("blank", "")])

    def line_stroke(self):
        self.write_row([
            ("first", "*"*15),
            ("second", "*"*15),
            ("third", "*"*15),
            ("fourth", "*"*15),
        ])

    def close(self):
        self.workbook.close()

    def clear_matched_address(self):
        self.matched_address = None


class DB2XLS(object):

    def __init__(self, section):
        self.final_data = []
        self.section = section
        self.file_name = section

        self.database = helper.get_database_object()

        self.xlsx = XLSWriter("%s.xlsx" % self.file_name)

    def get_index_of_name(self, name):
        try:
            return next(index for (index, item) in enumerate(self.final_data) if item["name"].lower() == name.lower())
        except:
            return None

    def format_xls(self):
        for item in self.final_data:
            name = [item.get("name")]
            items = item.get("items")
            for row in items:
                addresses = row.get("addresses")
                matched_address = row.get("matched_address")
                phone_nos = row.get("phone_nos")
                mobile = row.get("mobile")
                age = [row.get("age").replace("Age: ", "")]
                emails = row.get("emails")
                display = map(
                    None, name, age, addresses, matched_address, phone_nos, mobile, emails)
                for y in display:
                    _row = tuple('' if x is None else x for x in y)
                    test = [
                        ("name", _row[0]),
                        ("age", _row[1]),
                        ("addresses", _row[2]),
                        ("matched_address", _row[3]),
                        ("phone_nos", _row[4]),
                        ("mobile", _row[5]),
                        ("emails", _row[6])
                    ]
                    self.xlsx.write_row(test)
                self.xlsx.blank_row()
                self.xlsx.clear_matched_address()

            self.xlsx.line_stroke()
            self.xlsx.blank_row()

    def parse(self, item):
        name = item.get("name")
        addresses = item.get("addresses")
        phone_nos = item.get("phone_nos")
        mobile = item.get("mobile")
        age = item.get("age")
        emails = item.get("emails")
        matched_address = [item.get("matched_address")]
        index = self.get_index_of_name(name)
        if not index:
            self.final_data.append({
                "name": name,
                "items": [{
                    "addresses": addresses,
                    "matched_address": matched_address,
                    "phone_nos": phone_nos,
                    "mobile": mobile,
                    "age": age,
                    "emails": emails
                }]
            })
        else:
            self.final_data[index]["items"].append({
                "addresses": addresses,
                "matched_address": matched_address,
                "phone_nos": phone_nos,
                "mobile": mobile,
                "age": age,
                "emails": emails
            })

    def export_by_name(self, name):
        cursor = self.database.read(self.section, REThink.rethinkdb.row['name'] == name)
        cursor = list(cursor)
        for item in cursor:
            self.parse(item)

    def export_all(self):
        cursor = self.database.group(self.section, 'name')
        for item in cursor:
            self.export_by_name(item)

    def start(self, name=None):
        if name:
            self.export_by_name(name)
        else:
            self.export_all()

        self.xlsx.write_header()
        self.format_xls()
        self.xlsx.close()

# host = "localhost"
# port = 28015
# db = "intelius"
# table = "BALTIMORE"

# r = REThink(db=db, host=host, port=port)
# cursor = r.read(table, REThink.rethinkdb.row["name"] == "John H Despeaux")
# # cursor = r.read(table, REThink.rethinkdb.row["name"] == "Gopal Ghimire")
# cursor = list(cursor)
# section = "BALTIMORE"
# xlsformat = XLSFormat(section)
# xlsformat.start()
