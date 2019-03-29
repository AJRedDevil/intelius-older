# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import re
import time
import random
import mechanize
import cookielib
import json
import csv
from lxml import html
from random import shuffle
from bs4 import BeautifulSoup
from collections import OrderedDict

import helper

from InteliusScraper import InteliusScraper


def select_form_by_id(form):
    return form.attrs.get('id', None) == 'frmNameSearch'


class MaxTryException(Exception):
    # def __init__(self, message, errors):
    def __init__(self, message):
        # Call the base class constructor with the parameters it needs
        super(MaxTryException, self).__init__(message)

        # # Now for your custom code...
        # self.errors = errors


class MechanizeBrowser(object):

    def __init__(self, section):
        self.BASE_URL = "https://iservices.intelius.com/premier/dashboard.php"

        self.login_required = True
        self.username = helper.readConfig().get('LOGIN', 'EMAIL')
        self.password = helper.readConfig().get('LOGIN', 'PASSWORD')
        self.login_url = self.BASE_URL
        self.login_form_index = 0  # index of form to use as login
        self.login_user_key = "email"
        self.login_password_key = "password"

        self.http_proxy_server = ['120.198.231.22:8080', '124.206.133.227:80', '121.8.69.162:9797', '202.117.15.80:8080', '120.198.231.86:8080', '120.197.234.164:80', '24.173.40.24:8080', '123.134.185.11:4040', '180.73.0.6:81', '222.88.236.235:80', '125.212.37.72:3128', '198.169.246.30:80', '121.41.161.110:80', '46.105.152.77:8888', '124.88.67.31:81', '121.69.24.22:8118', '180.73.66.245:81', '109.207.61.148:8090',
                                  '92.222.237.20:8898', '106.38.251.62:8088', '124.88.67.40:843', '213.136.79.124:80', '121.69.8.234:8080', '117.136.234.5:80', '209.150.253.81:8080', '200.46.24.114:80', '183.207.228.122:80', '31.25.141.148:8080', '222.59.246.38:8118', '124.88.67.40:82', '121.15.230.126:9797', '116.212.157.111:8080', '115.228.54.251:3128', '60.250.81.97:80', '124.88.67.19:80', '196.36.53.202:9999', '122.76.249.2:8118', '124.88.67.40:83']
        shuffle(self.http_proxy_server)
        self.url_open_try = 0
        self.max_url_open_try = 30

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

        self.change_proxy()

    def login(self):
        self.browser.open(self.login_url)
        self.browser.select_form(nr=self.login_form_index)
        self.browser.form[self.login_user_key] = self.username
        self.browser.form[self.login_password_key] = self.password

        self.browser.submit()

    def change_proxy(self):
        proxy = random.choice(self.http_proxy_server)
        # print "using proxy %s" % proxy
        self.browser.set_proxies({"http": proxy})

    def open_url(self, url):
        self.change_proxy()
        try:
            response = self.browser.open(url).read()
        except Exception, e:
            if self.url_open_try > self.max_url_open_try:
                raise MaxTryException(
                    "Maximum try exceeded to open a single url")

            self.url_open_try += self.url_open_try
            print str(e)
            response = self.open_url(url)

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

        self.browser.select_form(predicate=select_form_by_id)
        # self.browser.select_form("search")

        self.browser.form['qf'] = first_name
        self.browser.form['qn'] = last_name
        self.browser.form['qcs'] = city_state
        self.browser.submit()

        self.extract_profile_urls()

        self.extract_all_profiles_from_search()

        self.scraper.save_full_profile(
            self.section, index, first_name, last_name, self.profile_data)

    def extract_all_profiles_from_search(self):
        for profile_url in self.profile_url_lists:
            content = self.open_url(profile_url)
            self.profile_data.append(
                self.scraper.extract_full_profile(content))

    def pre_process(self):
        if self.login_required:
            self.login()

    def start(self):
        self.pre_process()

    def save_current_page_to_file(self):
        content = self.browser.response().read()
        filename = "test.html"
        open(filename, "w").write(content)
        import webbrowser
        import os
        webbrowser.open('file://' + os.path.realpath(filename))
        import pdb
        pdb.set_trace()
