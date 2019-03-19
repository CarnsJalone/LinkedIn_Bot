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
        return "This is a bad ass class"

    def scrape(self, num_pages):
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


    def connect(self):
        bot = self.bot
        urls = bot.format_stored_people(bot.find_unvisited())

        # Open up linked in
        bot.create_browser()

        # To to Linkin Homepage
        bot.navigate_to_url("https://www.linkedin.com", 2)

        # Enter credentials to log on 
        bot.login()

        # Go to each page
        bot.add_friends(urls)

        # Close the browser
        bot.close_browser()

    def update_matches(self):
        bot = self.bot

        # Gather people who's job description has been updated
        matches = bot.find_updated_job_descriptions()
        for match in matches:
            print(match)

        # # Update the database with those who fit the criteria
        # bot.update_db_with_matches(matches, True)

        # # Update the database with those who don't fit the criteria
        # bot.update_db_with_matches(non_matches, False)

    def reach_out(self):
        bot = self.bot

        bot.create_browser()

        bot.navigate_to_url("https://www.linkedin.com", 2)

        bot.login()

        bot.message_candidates()

        bot.close_browser()

    def test(self):
        bot = self.bot
        bot.mark_as_visited("https://www.linkedin.com/in/siddhanth-jayaraman-13a12326/", bot.open_database())
        



if __name__ == '__main__':
    new_scraper = webScraper(username, password)
    # new_scraper.scrape(50)
    # new_scraper.connect()
    new_scraper.update_matches()
    # new_scraper.reach_out()
    # new_scraper.test()

# print(new_scraper)
