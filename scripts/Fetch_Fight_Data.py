# Python

import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from constants.config import UFC_STATS_URL, TIMEOUT
from constants.logging_config import get_logger
import time
import logging

# Suppress Selenium logs
logging.getLogger('selenium').setLevel(logging.ERROR)

# Function to create a new Chrome instance
def create_chrome_instance(adblocker_flag:bool = False):
    chrome_options = Options()
    #chrome_options.add_argument("--headless")  # Headless mode

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")  # Suppress most logs (error-level only)
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])  # Suppress DevTools logs

    
    if adblocker_flag:
        # Path to the Chrome extension .crx file
        extension_path = "./CJPALHDLNBPAFIAMEJDNHCPHJBKEIAGM_1_60_0_0.crx"
        chrome_options.add_extension(extension_path)

    # Set up Chrome WebDriver
    service = Service(ChromeDriverManager().install(), log_path=os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Set implicit wait
    driver.implicitly_wait(10)  # Wait for up to 10 seconds for elements to be found
    
    return driver

# Create two instances of ChromeDriver
driver1 = create_chrome_instance()
driver2 = create_chrome_instance(adblocker_flag=True)

# Set up Logger
logger = get_logger(__name__)

try:
    #Open the UFC Stats URL
    driver1.get(UFC_STATS_URL)

    # Perform actions
    # Example: Find an element and perform an action
    fight_detail_rows = driver1.find_elements(
        By.CLASS_NAME, 
        "b-fight-details__table-row")
    
    if len(fight_detail_rows) == 0:
        logger.error("No fight details found")
        exit()
    
    for row in fight_detail_rows:

        #Find all td elements of the current row
        table_data = row.find_elements(By.CLASS_NAME, "b-fight-details__table-col")

        #If the row is perfectly formatted, it should have 10 td elements/columns
        #2nd Column should contain the figher names (Index 1)
        #7th Column should contain the weight class (Index 6)
        #8th Column should contain the method of victory (Index 7)
        #9th Column should contain the round of the fight (Index 8)
        #10th Column should contain the time of the fight (Index 9)

        if len(table_data) != 10:
            logger.debug("Skipping row because it does not have 10 columns")
            continue

        #Extract the fighter names
        fighters = table_data[1].find_elements(By.CLASS_NAME, "b-link")
        
        if len(fighters) < 2:
            logger.debug("Skipping row because two fighter names were not able to be found")
            continue
        
        #Extract the weight class
        weight_class = table_data[6].text.upper()

        if("WEIGHT" not in weight_class.upper()):
            logger.debug("Skipping row because the weight class is not a weight class")
            continue

        #Extract the method of victory
        method_of_victory = table_data[7].find_element(By.CLASS_NAME, "b-fight-details__table-text").text

        # if not("method" in method_of_victory.lower()):
        #     logger.debug("Skipping row because the method of victory is not a method of victory")
        #     continue

        
        for fighter in fighters:
            # Navigate to Tapology
            driver2.get("https://www.tapology.com/fightcenter")

            # Find and click the search bar
            search_bar = driver2.find_element(By.ID, "siteSearch")
            search_bar.click()

            # Enter the fighter name
            search_bar.send_keys(fighter.text)
            
            # Find and click the search button
            search_button = driver2.find_element(By.ID, "search")
            search_button.click()

            # Locate the table element with the class name "fcLeaderboard"
            table_element = driver2.find_element(By.CLASS_NAME, "fcLeaderboard")

            # Find all anchor elements within this table
            anchor_elements = table_element.find_elements(By.TAG_NAME, "a")

            # Optionally, you can iterate over the anchor elements and perform actions
            for anchor in anchor_elements:
                href_link = anchor.get_attribute("href")
                print(href_link)  # Example: Print the href attribute of each anchor
                anchor.click()  # Example: Click on the anchor element  

                #Hide the presence of cancelled bouts
                hide_cancelled_fights_button = driver2.find_elements(By.XPATH, "//button[text()='Shown']")
                driver2.execute_script("arguments[0].scrollIntoView({block: \"center\",inline: \"center\",behavior: \"smooth\"});", hide_cancelled_fights_button[0])
                hide_cancelled_fights_button[0].click()

                #Check for the presence of the latest fight of the fighter
                #professional_bouts = driver2.find_elements(By.XPATH, "//div[@data-division='pro']")
                professional_bouts = driver2.find_elements(By.XPATH, "//div[@data-division='pro']")
                professional_bouts = [bout for bout in professional_bouts if bout.text != ""]
                for bout in professional_bouts:
                    if bout.text == "":
                        continue
                    print(bout.text)
            time.sleep(15)



        # fighter_one = fighters[0].text
        # fighter_two = fighters[1].text
        
        # print(fighter_one + " vs " + fighter_two)
        
    # Wait for results to load and display the title
    driver1.implicitly_wait(10)  # seconds
    print("test")

finally:
    # Close the browser
    driver1.quit()