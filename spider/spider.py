# -*- coding: utf-8 -*-


import csv
import logging as log
import os
import time
import traceback

from lxml import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotVisibleException, TimeoutException

import helper

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
DRIVER_PATH = os.path.join(CURRENT_DIR, '../bin',
                           helper.readConfig().get('DRIVER', 'FILENAME'))

URL = "https://iservices.intelius.com/premier/dashboard.php"

EMAIL = os.environ['EMAIL']
PASSWORD = os.environ['PASSWORD']


class InteliusScraper(object):
    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=DRIVER_PATH)
        self.driver.wait = WebDriverWait(self.driver, 10)
        self.brisk = 1
        self.short_wait_time = self.brisk*5
        self.long_wait_time = self.brisk*10
        self.mahabarat = self.brisk*15
        self.login()

    def login(self):
        self.driver.get(URL)
        assert "Intelius" in self.driver.title
        elem = self.driver.find_element_by_name("email")
        elem.clear()
        elem.send_keys(EMAIL)
        elem = self.driver.find_element_by_name("password")
        elem.clear()
        elem.send_keys(PASSWORD)
        elem.send_keys(Keys.RETURN)
        time.sleep(self.short_wait_time)

    def search(self, last_name="", first_name="", city_state=""):  # Phyllis Henderson Baltimore, MD
        if not last_name:
            raise ValueError("Last Name is empty")
        assert "Intelius" in self.driver.title
        time.sleep(self.brisk)
        elem = self.driver.wait.until(EC.presence_of_element_located(
            (By.NAME, "qf")))
        elem.clear()
        elem.send_keys(first_name)
        elem = self.driver.find_element_by_name("qn")
        elem.clear()
        elem.send_keys(last_name)
        elem = self.driver.find_element_by_name("qcs")
        elem.clear()
        elem.send_keys(city_state)
        elem.send_keys(Keys.RETURN)
        time.sleep(self.mahabarat)

    def __extract_profile_links(self, source):
        lexml = html.fromstring(source)
        # log.warn(lexml.xpath("//div[contains(@class,'box-d')]/div[@class='inner']/div[@class='identity']/div[@class='actions']/a/@href"))
        return lexml.xpath("//div[contains(@class,'box-d')]/div[@class='inner']/div[@class='identity']/div[@class='actions']/a/@href")

    def __get_profile_links(self):
        prev_url = self.driver.current_url
        profile_link = []
        profile_link.extend(
            self.__extract_profile_links(self.driver.page_source))
        while True:
            assert "Intelius" in self.driver.title
            try:
                elem = self.driver.wait.until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "tip-right")))
                elem.click()
                time.sleep(self.short_wait_time)
            except TimeoutException, e:
                print str(e)
                return profile_link
            if prev_url == self.driver.current_url:
                return profile_link
            profile_link.extend(
                self.__extract_profile_links(self.driver.page_source))
            prev_url = self.driver.current_url
        return profile_link

    def __extract_full_profile(self, source):
        data = {}
        lexml = html.fromstring(source)
        data['name'] = lexml.xpath(
            "//div[@class='identity']/span[@class='name']/text()")[0]
        data['age'] = lexml.xpath(
            "//div[@class='identity']/p")[0].text_content()
        data['phone_nos'] = [li.text_content().strip().split("  ")[0]
                             for li in lexml.xpath("//div[@class='inner contact']/ul[1]/li")]
        data['emails'] = [li.text_content().strip()
                          for li in lexml.xpath("//div[@class='inner contact']/ul[2]/li")]
        data['addresses'] = [" ".join(li.xpath("./a/text()"))
                             for li in lexml.xpath("//ul[@class='addresses']/li")]
        return data

    def __save_full_profile(self, index, first_name, last_name, data):
        file_name = "{0}_{1}_{2}".format(index, first_name, last_name)
        helper.save_detail_to_storage(file_name, data)

    def main_process(self):
        try:
            section = 'CSVFILE'
            file_path = os.path.join(CURRENT_DIR, '..', helper.readConfig().get(
                'STORAGE', 'CSV_PATH'), "{0}.csv".format(helper.readConfig().get(section, 'FILENAME')))
            field_names = helper.readConfig().get(section, 'FIELDNAMES').split(',')
            name = helper.readConfig().get(section, 'NAME')
            city = helper.readConfig().get(section, 'CITY')
            state = helper.readConfig().get(section, 'STATE')
            with open(file_path, 'rU') as f:
                csv_reader = csv.DictReader(f, field_names)
                csv_reader.next()   # The first row is the header
                index = 1
                for row in csv_reader:
                    first_name, last_name = helper.split_name(row[name])
                    city_state = "{0} , {1}".format(row[city], row[state])
                    self.search(last_name, first_name, city_state)
                    profile_links = self.__get_profile_links()
                    data = []
                    for link in profile_links:
                        self.driver.get(link)
                        assert "Intelius" in self.driver.title
                        time.sleep(self.short_wait_time)
                        data.append(self.__extract_full_profile(
                            self.driver.page_source))
                    self.__save_full_profile(
                        index, first_name, last_name, data)
                    index += 1
        except Exception, e:
            print str(e)
            tb = traceback.format_exc()
        else:
            tb = "No error"
        finally:
            print tb
            self.driver.quit()


if __name__ == "__main__":
    scraper = InteliusScraper()
    scraper.main_process()


# def get_cookie(driver):
#   time.sleep(10)
#   print driver.get_cookies()
#   return driver.get_cookie("cookie")
