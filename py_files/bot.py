import os
import sys
import time 
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import lxml
import re
import sqlite3
from sqlite3 import Error as DB_ERROR
import random

# Import chromedriver.exe
platform = sys.platform

if platform == "linux":
    chromedriver = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webdriver/linux/chromedriver.exe")
    sys.path.append("/home/jarret/.local/lib/python3.6/site-packages/")
elif platform == "win32":
    chromedriver = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), r"webdriver\windows\chromedriver.exe")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

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
        root_url = "https://www.linkedin.com"
        for person_object in url_list:
            split_person_object = person_object.replace("/", " ").replace("-", " ")
            split_person_object = split_person_object.split()
            person_url = root_url + person_object

            if split_person_object:
                if len(split_person_object) ==5:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = split_person_object[3]
                    ID = split_person_object[4]
                if len(split_person_object) == 4:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = "None"
                    ID = split_person_object[3]
                elif len(split_person_object) == 3:
                    first_name = split_person_object[1]
                    last_name = split_person_object[2]
                    certification = "None"
                    ID = str(split_person_object[1]) + str(split_person_object[2])
                elif len(split_person_object) == 2:
                    first_name = split_person_object[1]
                    last_name = "None"
                    certification = "None"

                person = {
                    'ID' : ID,
                    'first_name' : first_name,
                    'last_name' : last_name,
                    'certification' : certification, 
                    'added' : False, 
                    'URL' : person_url, 
                    'position_desc' : 'None',
                    'job_potential' : False,
                    'messaged' : False
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
            added boolean, 
            URL text NOT NULL, 
            position_desc text,
            job_potential boolean,
            messaged boolean
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
                values = "'{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'".format(str(person["ID"]), str(person["first_name"]), str(person["last_name"]), str(person["certification"]), person["added"], person["URL"], person["position_desc"], person["job_potential"], person["messaged"])
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

        except Exception as e:
            print(e)
            return 

    def find_not_added(self, db_connection):
        
        try:
            not_added = self.query_db(db_connection, select_condition="added='False' AND messaged <> 'True'" )
            return not_added
        except DB_ERROR as e:
            print(e)
            return 

    def format_stored_people(self, people_not_yet_added):

        people = []

        random.shuffle(people_not_yet_added)

        for person in people_not_yet_added:
            person_url = person[5]
            person_id = person[0]

            person = {
                "ID" : person_id,
                "URL" : person_url
            }

            people.append(person)

        return people

    def add_friends(self, urls_and_ids, db_connection, num_profiles, add_mode):
        
        profiles_visited = 0

        while profiles_visited < num_profiles:
            for url_and_id in urls_and_ids:
                url = url_and_id["URL"]
                ID = url_and_id["ID"]
                self.navigate_to_url(url, random.uniform(3.5, 5.9))
                job_description = self.acquire_job_description()
                first_name, last_name = self.acquire_full_name()
                if add_mode:
                    self.connect_to_person()
                    self.update_person(url, db_connection, job_description)
                else:
                    self.update_database(db_connection, "SET position_desc = '{}', first_name = '{}', last_name = '{}'".format(job_description, first_name, last_name), "WHERE ID = '{}'".format(ID))
                    print("{} {} with the ID {}'s job description updated to: {}".format(first_name, last_name, ID, job_description))
                profiles_visited += 1

    def update_person(self, candidate_url, db_connection, job_description):

        split_url = candidate_url.replace("/", " ").replace("-", " ").split()
        
        if len(split_url) == 7:
            ID = split_url[5]
        elif len(split_url) == 6:
            ID = split_url[5]
        elif len(split_url) == 5:
            ID = str(split_url[3]) + str(split_url[4])
        elif len(split_url) == 4:
            ID = split_url[3]

        # Returns a DB entry of one person that hasn't been added yet
        # And hasn't been messaged yet
        person_not_connected = self.query_db(db_connection, select_condition="WHERE ID = '{}' AND added <> 'True' AND messaged <> 'True'".format(ID))
        
        if person_not_connected:
            # Mark person as not connected in the DB
            self.update_database(db_connection, sql_set_command="SET added = 'True'", sql_where_command="WHERE ID = '{}'".format(ID))

        else:
            # No entries were returned from the DB which means that 
            # 1) Entry doesn't exist
            # 2) Entry has been added already
            # 3) Entry has been messaged already
            print("Person with the ID {} has already been added".format(ID))

    def connect_to_person(self):

        try:
            # Click the connect button
            connect_button = self.browser.find_element_by_class_name("pv-s-profile-actions__label")
            connect_button.click()
            # Wait for browser to load
            time.sleep(2)
            # Click the 'Send now' button
            send_now_button = self.browser.find_element_by_xpath("//button[text()='Send now']")
            send_now_button.click()
            print("Person added")
            return True 
        except NoSuchElementException as e:
            print(e)
            print("An error arose... Bypassing Send Now button... Database to be updated.")
            return False    
        except WebDriverException as e:
            print(e)
            print("An error arose... Bypassing Send Now button... Database to be updated.")
            return False
        except Exception as e:
            print(e)
            print("An error arose... Bypassing Send Now button... Database to be updated.")
            return False

    def acquire_job_description(self):
        current_page = self.get_page_source()
        job_description_with_tags = current_page.find("h2")
        job_description = job_description_with_tags.text
        job_description = str(job_description)
        job_description = job_description.replace("\n", "")
        formatted_js = re.sub("\s\s+", "", job_description)
        return formatted_js

    def acquire_full_name(self):

        try:
            current_page = self.get_page_source()
            full_name_with_tags = current_page.find("h1", {"class" : "pv-top-card-section__name"})
            full_name = full_name_with_tags.text
            full_name = str(full_name)
            full_name = full_name.replace("\n", "")
            full_name = re.sub("\s\s+", "", full_name)
            split_name = full_name.split(" ")
            if len(split_name) == 1:
                first_name = split_name[0]
                last_name = 'None'
            if len(split_name) == 2:
                first_name = split_name[0]
                last_name = split_name[1]
            elif len(split_name) > 2:
                first_name = split_name[0]
                last_name = split_name[len(split_name) - 1]

        except AttributeError as e:
            print(e)
            first_name = "None"
            last_name = "None"
        except Exception as e:
            print(e)
            first_name = "None"
            last_name = "None"

        return first_name, last_name


    def find_updated_job_descriptions(self, db_connection):

        matches = []

        # Find people who have a job description that haven't been messaged yet
        sql_job_description_command = "position_desc <> 'None' AND messaged <> 'True'"

        # Execute search in DB
        people_with_job_descriptions = self.query_db(db_connection, select_condition=sql_job_description_command)

        for person in people_with_job_descriptions:

            # Grab the 6th index of the resultant people from the db
            job_description = person[6]

            # Compare the resultant people against the text file for job keywords
            # and compare against the list of elimination keywords
            each_match = self.compare_desc_against_criteria(job_description, person)

            if each_match:
                matches.append(each_match)

        return matches


    def compare_desc_against_criteria(self, job_description, person):

        SEARCH_CRITERIA_TXT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'txt/search_criteria.txt')
        
        matches = []

        ignore_criteria = [
            "FCA", 
            "FCA Fiat Chrysler Automobiles",
            "Jeep",
            "Operations", 
            "DHL", 
            "Chrysler", 
            "Fiat", 
            "Mopar", 
            "Supply Chain", 
            "WCM", 
            "Logistics", 
            "MLM", 
            "Quality",
            "Retail", 
            "Student", 
            "Clerical", 
            "Intern", 
            "Sales"
        ]
        
        # Open the text file where I have the keywords defined
        match_criteria = open(SEARCH_CRITERIA_TXT, 'r')

        job_description = str(job_description)
        
        for match_description in match_criteria:

            # Format the text file so we can iterate properly
            match_description = match_description.strip()
            match_description = match_description.replace(" ", "")
            match_description = str(match_description)

            if match_description:

                # Read in the list of keywords that we want to ignore
                for ignore_description in ignore_criteria:

                    # Format them so we can work with them
                    ignore_description = ignore_description.replace(" ", "")
                    ignore_description = str(ignore_description)

                    # If the target keyword is in their job description
                    if match_description in job_description:

                        # If the name triggers the list of words we want to avoid
                        if ignore_description in job_description:

                            # throw it out
                            return 

                        else:

                            # If we haven't already added it, add it
                            if person not in matches:

                                if person:
                                    matches.append(person)

        match_criteria.close()
        return matches

    def get_matching_candidates(self, db_connection):

        candidates = []

        sql_search_command = "WHERE job_potential = 'True' AND messaged = 'False'"

        matching_candidates = self.query_db(db_connection, select_condition=sql_search_command)

        for candidate in matching_candidates:
            if candidate:
                candidates.append(candidate)

        return candidate


    def message_candidates(self, candidates):

        for candidate in candidates:
            ID = candidate[0]
            first_name = candidate[1]
            last_name = candidate[2]
            candidate_url = candidate[5]

            if candidate_url:
                self.navigate_to_url(candidate_url, 2)
                page = self.get_page_source()

                span_text = page.find("span", {"class": "pv-s-profile-actions__label"}).text
                if span_text == 'Message':
                    self.send_message(ID, first_name, last_name)
                elif span_text == 'Pending':
                    print("Connection Request is pending for {} {} with the ID {}. Proceeding to the next candidate".format(first_name, last_name, ID))
                else:
                    print("Another issue arose, proceeding to the next candidate")

    def message_with_subject(self, first_name):

        first_name = first_name.title()

        subject = "Hi {}".format(first_name)

        message = """My name is Jarret Laberdee, I'm an aspiring software developer looking for connections here, on LinkedIn. Sorry for the intrusive message but 
        your profile stuck out to me.  
        While my motive is to find a job in the technological sector, I'm really just looking to expand my network of associates. I would love to hear from you! 
        If any of this is resonating, you can check out some of my work on my website, http://www.carnsjalone.com. Hoping 
        hear from you {}! Have a nice day!""".format(first_name)

        message = message.replace("\n", " ")
        message = re.sub("\s\s+", " ", message)

        return subject, message

    def message_no_subject(self, first_name):

        first_name = first_name.title()

        message = """Hi {}. My name is Jarret Laberdee, I'm an aspiring software developer looking for connections here, on LinkedIn. Sorry for the intrusive message but 
        your profile stuck out to me.  
        While my motive is to find a job in the technological sector, I'm really just looking to expand my network of associates. I would love to hear from you! 
        If any of this is resonating, you can check out some of my work on my website, http://www.carnsjalone.com. Hoping 
        hear from you {}! Have a nice day!""".format(first_name, first_name)

        message = message.replace("\n", " ")
        message = re.sub("\s\s+", " ", message)

        return message


    def send_message(self, ID, first_name, last_name):

        db_connection = self.open_database()

        premium_url = "https://www.linkedin.com/premium/products"

        send_message_button = self.browser.find_element_by_class_name("pv-s-profile-actions__label")
        send_message_button.click()

        time.sleep(2)

        current_url = self.browser.current_url

        if premium_url in current_url:
            print("Messaging {} {} with the ID {} has been forwarded to premium account URL, skipping to next candidate...".format(first_name, last_name, ID))
            return 
        else:
            
            time.sleep(1)

            # If there's no issue with the subject form, return a tuple from the format message function
            subject, message = self.message_with_subject(first_name)
            
            # Begin message with a subject line

            try:
                # Type the subject to the candidate
                message_form_subject = self.browser.find_element_by_class_name("msg-form__subject")
                message_form_subject.send_keys(subject)

            except NoSuchElementException as e:

                # Begin message with no subject line

                print(e + "\nExecuting message with no subject function...\n")
                
                # If there's an issue with the subject form ie it's not there, returns a single string from the errored format
                message = self.message_no_subject(first_name)

                try:
                    # Type the message to the candidate
                    message_form_message = self.browser.find_element_by_class_name("msg-form__contenteditable")
                    message_form_message.send_keys(message)
                    print("Sending message to {} {} with the ID {}.".format(first_name, last_name, ID))
                
                except NoSuchElementException as e:
                    print(e + "\n")
                    pass
                
                except WebDriverException as e:
                    print(e + "\n")
                    pass
                
                except Exception as e:
                    print(e + "\n")
                    pass

                try:
                    
                    # Click the submit button
                    message_form_submit_button = self.browser.find_element_by_class_name("msg-form__send-button")
                    message_form_submit_button.click()
                
                except NoSuchElementException as e:
                    print(e)
                    pass
                
                except WebDriverException as e:
                    print(e)
                    pass
                
                except Exception as e:
                    print(e + "\n")

            except WebDriverException as e:
                print(e + "\n")
                return 
            
            except Exception as e:
                print(e + "\n")
                return 

            try:
                # Type the message to the candidate
                message_form_message = self.browser.find_element_by_class_name("msg-form__contenteditable")
                message_form_message.send_keys(message)
                print("Sending message to {} {} with the ID {}.".format(first_name, last_name, ID))
            except NoSuchElementException as e:
                print(e)
                pass
            except WebDriverException as e:
                print(e)
                pass
            except Exception as e:
                print(e)
                pass

            time.sleep(1)

            try:
                # Click the submit button
                message_form_submit_button = self.browser.find_element_by_class_name("msg-form__send-button")
                message_form_submit_button.click()
            except NoSuchElementException as e:
                print(e)
                pass
            except WebDriverException as e:
                print(e)
                pass

            time.sleep(1)

            try:
                self.update_database(db_connection, sql_set_command="SET messaged = 'True'", sql_where_command="WHERE ID = '{}'".format(ID))
                print("{} {} with the ID {} has been set to 'Messaged' in the database.".format(first_name, last_name, ID))
            except Exception as e:
                print(e)

        db_connection.close()

    def update_database(self, db_connection, sql_set_command, sql_where_command):

        update_command = """
            UPDATE people
            {} 
            {}
        """.format(sql_set_command, sql_where_command)

        try:
            db_cursor = db_connection.cursor()
            db_cursor.execute(update_command)
            db_connection.commit()
        except DB_ERROR as e:
            print(e)
            return
        except Exception as e:
            print(e)
            return


        






        
        
        


            





    



