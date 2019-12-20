# -*- coding: utf-8 -*-
#!/usr/bin/env python

import csv
import logging as log
import os
import time

from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, TimeoutException

import helper

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DRIVER_PATH = os.path.join(CURRENT_DIR, '../bin', helper.readConfig().get('DRIVER','FILENAME'))
STORAGE_PATH = os.path.join(CURRENT_DIR, '..', helper.readConfig().get('STORAGE','PATH'))

class CSVFormat(object):
    def __init__(self, section, file_name, data):
        self.data = data
        self.final_data = []
        file_name = "results.csv"

        file_path = os.path.join(STORAGE_PATH, section)
        helper.check_path(file_path)

        file_path = os.path.join(STORAGE_PATH, section, file_name)
        self.file_name = file_path

    def get_index_of_name(self, name):
        try:
            return next(index for (index, item) in enumerate(self.final_data) if item["name"].lower() == name.lower())
        except:
            return None

    def format_csv(self):
        with open(self.file_name, "a") as csvfile:
            csv_file = csv.writer(csvfile, lineterminator='\n')
            for item in self.final_data:
                name = [item.get("name")]
                items = item.get("items")
                for row in items:
                    addresses = row.get("addresses")
                    phone_nos = row.get("phone_nos")
                    age = [row.get("age").replace("Age: ", "")]
                    emails = row.get("emails")
                    display = map(None, name, age, addresses, phone_nos, emails)
                    for y in display:
                        _row = tuple('' if x == None else x for x in y)
                        csv_file.writerow(_row)
                    csv_file.writerow(("", ))

                csv_file.writerow(("*"*15, "*"*15, "*"*15, "*"*15))
                csv_file.writerow(("", ))


    def parse(self, item):
        name = item.get("name")
        addresses = item.get("addresses")
        phone_nos = item.get("phone_nos")
        age = item.get("age")
        emails = item.get("emails")
        index = self.get_index_of_name(name)
        if index == None:
            self.final_data.append({
                "name": name,
                "items": [{
                    "addresses": addresses,
                    "phone_nos": phone_nos,
                    "age": age,
                    "emails": emails
                }]
            })
        else:
            self.final_data[index]["items"].append({
                    "addresses": addresses,
                    "phone_nos": phone_nos,
                    "age": age,
                    "emails": emails
                })

    def start(self):
        for item in self.data:
            self.parse(item)

        self.format_csv()


class InteliusScraper(object):
    def extract_profile_links(self, source):
        return self.__extract_full_profile()

    def extract_profile_links(self, source):
        return self.__extract_profile_links(source)

    def __extract_profile_links(self, source):
        lexml = html.fromstring(source)
        return lexml.xpath("//div[contains(@class,'box-d')]/div[@class='inner']/div[@class='identity']/div[@class='actions']/a/@href")

    def extract_full_profile(self, source, city_state, state, index, address):
        return self.__extract_full_profile(source, city_state, state, index, address)

    def __extract_full_profile(self, source, city_state, state, index, matching_address):
        data = {}
        lexml = html.fromstring(source)
        data['name'] = lexml.xpath("//div[@class='identity']/span[@class='name']/text()")[0]
        data['age'] = lexml.xpath("//div[@class='identity']/p")[0].text_content()
        data['phone_nos'] = [li.text_content().strip().split("  ")[0] for li in lexml.xpath("//div[@class='inner contact']/ul[1]/li") if 'mobile' not in li.text_content()]
        data['mobile'] = [li.text_content().strip().split("  ")[0] for li in lexml.xpath("//div[@class='inner contact']/ul[1]/li") if 'mobile' in li.text_content()]
        data['emails'] = [li.text_content().strip() for li in lexml.xpath("//div[@class='inner contact']/ul[2]/li")]
        data['addresses'] = [" ".join(li.xpath("./a/text()")) for li in lexml.xpath("//ul[@class='addresses']/li")]

        found = False
        for address in data['addresses']:
            if matching_address.lower() in address.lower():
                found = True
                break

        if not found:
            address = ""

        data['matched_address'] = address
        data['index'] = index

        return data

    def save_full_profile(self, section, index, first_name, last_name, data):
        self.__save_full_profile(section, index, first_name, last_name, data)

    def __save_full_profile(self, section, index, first_name, last_name, data):
        file_name = "{0}_{1}_{2}".format(index, first_name, last_name)
        helper.save_detail_to_storage(section, file_name, data)
        self.__save_to_csv(section, file_name, data)

    def __save_to_csv(self, section, file_name, data):
        file_name = "%s.csv" % file_name
        csvformat = CSVFormat(section, file_name, data)
        csvformat.start()
