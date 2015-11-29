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

class InteliusScraper(object):
    def extract_profile_links(self, source):
        return self.__extract_full_profile()

    def extract_profile_links(self, source):
        return self.__extract_profile_links(source)

    def __extract_profile_links(self, source):
        lexml = html.fromstring(source)
        return lexml.xpath("//div[contains(@class,'box-d')]/div[@class='inner']/div[@class='identity']/div[@class='actions']/a/@href")

    def extract_full_profile(self, source):
        return self.__extract_full_profile(source)

    def __extract_full_profile(self, source):
        data = {}
        lexml = html.fromstring(source)
        data['name'] = lexml.xpath("//div[@class='identity']/span[@class='name']/text()")[0]
        data['age'] = lexml.xpath("//div[@class='identity']/p")[0].text_content()
        data['phone_nos'] = [li.text_content().strip().split("  ")[0] for li in lexml.xpath("//div[@class='inner contact']/ul[1]/li")]
        data['emails'] = [li.text_content().strip() for li in lexml.xpath("//div[@class='inner contact']/ul[2]/li")]
        data['addresses'] = [" ".join(li.xpath("./a/text()")) for li in lexml.xpath("//ul[@class='addresses']/li")]
        return data

    def save_full_profile(self, index, first_name, last_name, data):
        self.__save_full_profile(index, first_name, last_name, data)

    def __save_full_profile(self,index, first_name, last_name, data):
        file_name = "{0}_{1}_{2}".format(index, first_name, last_name)
        helper.save_detail_to_storage(file_name, data)