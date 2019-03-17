from selenium import webdriver
import os
import time 
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import lxml
import re
import sqlite3
from sqlite3 import Error as DB_ERROR
import random

# Import chromedriver.exe
chromedriver = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"webdriver\chromedriver.exe")

class LinkedIn_Bot:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.current_page_source = None

    def __str__(self):
        return "LinkedIn_Bot - Created By Jarret Laberdee - Class Object Created To Increase Reach Of Development Web On LinkedIn"

    def create_browser(self):
        """Creates a browser instance of webdriver."""
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        self.browser = webdriver.Chrome(executable_path=chromedriver, chrome_options=options)

    def get_page_source(self):
        page = BeautifulSoup(self.browser.page_source, features='lxml')
        return page 

    def close_browser(self):
        self.browser.close()

    def navigate_to_url(self, url, sleep_interval):
        self.browser.get(url)
        time.sleep(sleep_interval)

    def login(self):
        self.browser.find_element_by_id("login-email").send_keys(self.username)
        self.browser.find_element_by_id("login-password").send_keys(self.password)
        self.browser.find_element_by_id("login-submit").click()
        time.sleep(2)

    def navigate_to_network(self):
        self.browser.find_element_by_id("mynetwork-tab-icon").click()
        time.sleep(2)

    def compile_people_links(self, page):
        links = []
        for link in page.find_all('a'):
            url = link.get('href')
            if url:
                if '/in/' in url:
                    if url not in links:
                        links.append(url)
        return links
        # print(links)

    def scroll_to_bottom(self, num_scrolls):
        """Scrolls to the bottom of the page by executing Javascript"""

        SCROLL_PAUSE_TIME = 1.25
        scroll_height_cmd = "window.scrollTo(0, document.body.scrollHeight);"
        
        for page in range(num_scrolls):
            last_height = self.browser.execute_script("return document.body.scrollHeight")
            self.browser.execute_script(scroll_height_cmd)
            # self.browser.execute_script("alert('Scrolling')")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return
            last_height = new_height

    def store_people(self, url_list):
        people_list = []
        for person_object in url_list:
            split_person_object = person_object.replace("/", " ").replace("-", " ")
            split_person_object = split_person_object.split()

            if split_person_object:
                if len(split_person_object) ==5:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = split_person_object[3]
                    ID = split_person_object[4]
                    visited = False
                if len(split_person_object) == 4:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = "None"
                    ID = split_person_object[3]
                    visited = False
                elif len(split_person_object) == 3:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = "None"
                    ID = str(split_person_object[1]) + str(split_person_object[2])
                    visited = False
                elif len(split_person_object) == 2:
                    first_name = split_person_object[1]
                    last_name = "None"
                    certification = "None"
                    ID = split_person_object[1]
                    visited = False

                person = {
                    'ID' : ID,
                    'first_name' : first_name,
                    'last_name' : last_name,
                    'certification' : certification, 
                    'visited' : visited
                }

            people_list.append(person)

        return people_list

    def open_database(self):
        ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        DB_PATH = os.path.join(ROOT_DIR, 'LinkedIn_People.db')

        try:
            db_connection = sqlite3.connect(DB_PATH)
            return db_connection
        except DB_ERROR as e:
            print(e)
            return None
        return None

    def database_write(self, people_list):
        db_connection = self.open_database()

        try:
            self.create_table(db_connection)
            db_connection.commit()
            self.append_people(people_list, db_connection)
            db_connection.commit()
        except DB_ERROR as e:
            print(e)
        finally:
            db_connection.close()

    def create_table(self, db_connection):

        create_table = """ CREATE TABLE IF NOT EXISTS people (
            ID text PRIMARY KEY UNIQUE,
            first_name text NOT NULL,
            last_name text NOT NULL, 
            certification text, 
            visited boolean
        ) """

        try:
            db_cursor = db_connection.cursor()
            db_cursor.execute(create_table)
        except DB_ERROR as e:
            print(e)

    def append_people(self, people_list, db_connection):
        
        try:
            db_cursor = db_connection.cursor()

            for person in people_list:
                columns = ', '.join(person.keys())
                values = "'{}', '{}', '{}', '{}', '{}'".format(str(person["ID"]), str(person["first_name"]), str(person["last_name"]), str(person["certification"]), person["visited"])
                # values = ''
                command = 'INSERT INTO people ({}) VALUES({})'.format(columns, values)

                try:
                    db_cursor.execute(command)
                except DB_ERROR as e:
                    print(e)
        except DB_ERROR as e:
            print(e)

    def query_db(self, db_connection, select_condition):

        target_list = []

        statement = """
            SELECT * FROM people WHERE {}
        """.format(select_condition)

        print(statement)

        try: 
            db_cursor = db_connection.cursor()
            db_cursor.execute(statement)

            entries = db_cursor.fetchall()

            for entry in entries:
                target_list.append(entry)

            return target_list
                
        except DB_ERROR as e:
            print(e)
            return

    def find_unvisited(self):

        db_connection = self.open_database()
        
        try:
            unvisited = self.query_db(db_connection, select_condition="visited='{}'".format(bool(False)))
            return unvisited
        except DB_ERROR as e:
            print(e)
            return 
        finally:
            db_connection.close()

    def format_stored_people(self, unvisited_people):

        formatted_urls = []
        root_url = "https://www.linkedin.com/in/"

        for person in unvisited_people:

            ID = person[0]
            first_name = person[1]
            last_name = person[2]
            certification = person[3]
            visited = person[4]

            if first_name in ID or last_name in ID:
                person_url = root_url + ID + "/"
                formatted_urls.append(person_url)

            if certification != "None":
                person_url = root_url + first_name + "-" + last_name + "-" + certification + "-" + ID + "/"
                formatted_urls.append(person_url)
            elif certification == "None":
                if last_name != "None":
                    person_url = root_url + first_name + "-" + last_name + "-" + ID + "/"
                    formatted_urls.append(person_url)
                elif last_name == "None":
                    person_url = root_url + ID + "/"
                    formatted_urls.append(person_url)

        return formatted_urls

    def go_to_pages(self, formatted_urls):
        
        for peoples_url in formatted_urls:
            self.navigate_to_url(peoples_url, random.uniform(3.5, 5.9))
        

        
        
        


            





    


