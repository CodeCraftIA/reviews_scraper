import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
import re
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import TimeoutException
from selenium.common.exceptions import TimeoutException, NoSuchElementException

options = uc.ChromeOptions()
driver = uc.Chrome(options=options)

url = "https://www.cornbreadhemp.com/products/full-spectrum-cbd-gummies?_ab=0&_fd=0&_sc=1&selling_plan=1184432308"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]
# Function to click the "Load more" button


def click_next_page():
    try:
        # Scroll to the pagination section
        pagination_element = driver.find_element(By.CSS_SELECTOR, "div.yotpo-pager")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_element)

        # Wait for the page to scroll and load properly
        time.sleep(0.7)

        # Find the "Next Page" button and click it
        next_button = driver.find_element(By.CSS_SELECTOR, "a.yotpo-icon-right-arrow.yotpo_next")
        if "yotpo-disabled" in next_button.get_attribute("class"):
            return False  # No more pages to click

        # Scroll to the next button to ensure it's in view
        actions = ActionChains(driver)
        actions.move_to_element(next_button).click().perform()

        # Wait for the next page to load after clicking
        time.sleep(0.3)
        
        return True
    except Exception as e:
        print(f"Error clicking the next page: {e}")
        return False

def scrape_page():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.yotpo-reviews.yotpo-active")
    except Exception as e:
        return
    cards = content.find_elements(By.CSS_SELECTOR, "div.yotpo-review.yotpo-regular-box")
    for card in cards:
        rate_num = ""
        header = ""
        review = ""
        # find rating
        try:
            rating_cont = card.find_element(By.CSS_SELECTOR, "div.yotpo-review-stars")
            rate = rating_cont.find_element(By.CSS_SELECTOR, "span.sr-only").text.strip()
            rate_num = rate.replace("star rating", "")
        except Exception as e:
            rate_num = ""
        # find review - header
        try:
            review_cont = card.find_element(By.CSS_SELECTOR, "div.yotpo-main")
            
        except Exception as e:
            review_cont = None
        if review_cont:
            # header
            try:
                header = review_cont.find_element(By.CSS_SELECTOR, "div.content-title.yotpo-font-bold").text.strip()
            except Exception as e:
                header = ""
            # review
            try:
                review_wraper = review_cont.find_element(By.CSS_SELECTOR, "div.yotpo-review-wrapper")
                review = review_wraper.find_element(By.CSS_SELECTOR, "div.content-review").text.strip()
            except Exception as e:
                review = ""
        ratings.append(rate_num)
        titles.append(header)
        ratings_texts.append(review)

'''
# Click the "Load more" button until it disappears or is unclickable
while click_load_more():
    time.sleep(5)
    pass
'''
for i in tqdm(range(1000)):
    scrape_page()
    click_next_page()
    time.sleep(0.5)

# Close the WebDriver
driver.quit()

def write_excel(path):
    # Create DataFrame
    df = pd.DataFrame({
        'Rating': ratings,
        'Title header': titles,
        'Review message': ratings_texts,
    })
    # Write DataFrame to Excel
    with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        print("Data scraped successfully and saved.")
        print("Processing complete. Check the generated files.")

write_excel('URL1_CORNB.xlsx')