# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import mechanize
import cookielib
import json
import csv
from lxml import html
from bs4 import BeautifulSoup
from collections import OrderedDict

import helper

from InteliusScraper import InteliusScraper

class MechanizeBrowser(object):

    def __init__(self, section):
        self.BASE_URL = "https://iservices.intelius.com/premier/dashboard.php"

        self.login_required = True
        self.username = helper.readConfig().get('LOGIN','EMAIL')
        self.password = helper.readConfig().get('LOGIN','PASSWORD')
        self.login_url = self.BASE_URL
        self.login_form_index = 0  # index of form to use as login
        self.login_user_key = "email"
        self.login_password_key = "password"

        self.section = section

        self.first_search = True
        self.profile_url_lists = []
        self.profile_data = []

        self.categories = {}
        self.extracted_information = {}

        self.scraper = InteliusScraper()

        self.__setup_browser()

    def __setup_browser(self):
        # setting up browser for login
        self.browser = mechanize.Browser()
        self.cookie_jar = cookielib.LWPCookieJar()
        self.browser.set_cookiejar(self.cookie_jar)

        # Browser options
        self.browser.set_handle_equiv(True)
        self.browser.set_handle_gzip(True)
        self.browser.set_handle_redirect(True)
        self.browser.set_handle_referer(True)
        self.browser.set_handle_robots(False)
        self.browser.set_handle_refresh(
            mechanize._http.HTTPRefreshProcessor(), max_time=1)
        self.browser.addheaders = [('User-agent', 'Chrome')]

    def login(self):
        self.browser.open(self.login_url)
        self.browser.select_form(nr=self.login_form_index)
        self.browser.form[self.login_user_key] = self.username
        self.browser.form[self.login_password_key] = self.password

        self.browser.submit()

    def open_url(self, url):
        response = self.browser.open(url).read()
        return response

    def next_result_page(self):
        content = self.browser.response().read()
        lexml = html.fromstring(content)

        # check if this is last page
        # if there is single result for below condition, it does not have next
        # link so this is considered as last page
        if not self.first_search:
            tags = lexml.xpath("//div[@id='pager']/a/img")
            if len(tags) < 2:
                return

        # if there is no url, that means it is only single page result
        next_url = lexml.xpath("//div[@id='pager']/a/@href")
        if next_url:
            next_url = next_url[-1]
        else:
            return

        self.open_url(next_url)

        self.first_search = False
        self.extract_profile_urls()

    def extract_profile_urls(self):
        content = self.browser.response().read()
        profile_list = self.scraper.extract_profile_links(content)

        self.profile_url_lists.extend(profile_list)

        # return
        self.next_result_page()

    def search(self, index, first_name, last_name, city_state):
        self.first_search = True
        self.profile_url_lists = []
        self.profile_data = []

        self.browser.select_form("search")

        self.browser.form['qf'] = first_name
        self.browser.form['qn'] = last_name
        self.browser.form['qcs'] = city_state
        self.browser.submit()

        self.extract_profile_urls()

        self.extract_all_profiles_from_search()

        self.scraper.save_full_profile(self.section, index, first_name, last_name, self.profile_data)

    def extract_all_profiles_from_search(self):
        for profile_url in self.profile_url_lists:
            content = self.open_url(profile_url)
            self.profile_data.append(self.scraper.extract_full_profile(content))

    def pre_process(self):
        if self.login_required:
            self.login()

    def start(self):
        self.pre_process()
