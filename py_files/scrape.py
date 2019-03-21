from bot import LinkedIn_Bot
import os 
import json 


credentials = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "json/credentials.json")

read_credentials = open(credentials, "r").read()
json_credentials = json.loads(read_credentials)
username = json_credentials["LinkedIn_Credentials"][0]["Username"]
password = json_credentials["LinkedIn_Credentials"][1]["Password"]

class webScraper():

    def __init__(self, username, password):
        self.bot = LinkedIn_Bot(username, password)

    def __repr__(self):
        return "Bot Created for the purpose of extending one's social web."

    def discover_new_people(self, num_pages):
        """This function goes into the 'Network' tab on linkedIn and logs people into the database for future add"""

        bot = self.bot

        # Open the browser
        bot.create_browser()

        # To to Linkin Homepage
        bot.navigate_to_url("https://www.linkedin.com", 2)

        # Enter credentials to log on 
        bot.login()

        # Navigate to the 'Network' tab
        bot.navigate_to_network()

        # Scroll to the bottom of the page continu
        bot.scroll_to_bottom(num_pages)
        
        # Get the current page source of the current URL
        page_source = bot.get_page_source()

        # Add all of the people into a list after formatted their names and IDs
        compiled_links = bot.compile_people_links(page_source)

        # Further format the people in preparation of the database storage
        people = bot.store_people(compiled_links)

        # Store all of the people into our database for later use
        bot.database_write(people)

        # Close the browser
        bot.close_browser()


    def get_personalized_information(self, num_profiles, add_mode):
        """This function iterates through all the entries in the 
        database and updates the 'Job Description' field by scraping 
        their LinkedIn page"""

        bot = self.bot

        db_connection = bot.open_database()

        # Find people who are in the database but have a job description
        # Marked as 'None'
        people_not_yet_added = bot.find_not_added(db_connection)

        # Grabs the urls and IDs for everyone who has 'None' as a 
        # Job description in the DB
        urls_and_ids = bot.format_stored_people(people_not_yet_added)

        # Open up Chrome
        bot.create_browser()

        # Navigate to Linkin Homepage
        bot.navigate_to_url("https://www.linkedin.com", 2)

        # Enter credentials to log on 
        bot.login()

        # Go to each page
        # Once there, grabs the job description that shows in each 
        # Candidate's profile, then logs into the database
        bot.add_friends(urls_and_ids, db_connection, num_profiles, add_mode=add_mode)

        db_connection.close()

        # Close the browser
        bot.close_browser()

    def update_matches(self):
        """This function updates the 'Job Potential' flag in the 
        database by comparing each person's job description against 
        a list of predefined target words in the /txt directory 
        """
        bot = self.bot

        # Open DB to execute the update command
        db_connection = bot.open_database()

        # Gather people who's job description has been updated
        matches = bot.find_updated_job_descriptions(db_connection)

        # Erase the updated criteria so we can expand the candidates
        bot.update_database(db_connection, sql_set_command="SET job_potential = 'False'", sql_where_command="WHERE job_potential = 'True'")
       
        for match in matches:
            ID = match[0][0]
            try:
                # Update DB with updated inquiry
                bot.update_database(db_connection, sql_set_command="SET job_potential = 'True'", sql_where_command="WHERE ID = '{}'".format(ID))
                print("Person with the ID {} has been marked as a potential candidate.".format(ID))
            except Exception as e:
                print(e)

        db_connection.close()

    def message_candidates(self):
        bot = self.bot

        # Create a connection
        db_connection = bot.open_database()

        # Open the browser
        bot.create_browser()

        # Go to LinkedIn homepage
        bot.navigate_to_url("https://www.linkedin.com", 2)

        # Login
        bot.login()

        # Return an array of candidates who have not yet been messaged 
        # And match our predefined list of search terminology
        matching_candidates = bot.get_matching_candidates(db_connection)

        # Message each candidate
        bot.message_candidates(matching_candidates)

        db_connection.close()

        bot.close_browser()

    def test(self):
        bot = self.bot
        bot.mark_as_visited("https://www.linkedin.com/in/siddhanth-jayaraman-13a12326/", bot.open_database())
        



if __name__ == '__main__':
    # scrape_tool = webScraper(username, password)
    scrape_tool = webScraper(username, password)
    # scrape_tool.discover_new_people(20)
    # scrape_tool.get_personalized_information(num_profiles=5, add_mode=False)
    # scrape_tool.update_matches()
    scrape_tool.get_personalized_information(num_profiles=5, add_mode=True)
    # new_scraper.reach_out()
    # new_scraper.test()

# print(new_scraper)
