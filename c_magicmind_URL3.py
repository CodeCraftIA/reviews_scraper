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

url = "https://magicmind.com/products/magic-mind?selling_plan=445022342"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]

def click_load_more():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.learn-reviews__container")
    except Exception as e:
        return False
    try:
        # Wait until the "Load more" button is present in the DOM
        load_more_button = WebDriverWait(content, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.jdgm-all-reviews-page__load-more"))
        )
        # Scroll the button into view and click it using JavaScript
        driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        time.sleep(2.5)  # Give it a moment to scroll into view
        driver.execute_script("arguments[0].click();", load_more_button)
        return True
    #except (TimeoutException, NoSuchElementException):
    except Exception as e:
        print("Could not click the load button")
        return False
    

def scrape_page():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.learn-reviews__container")
    except Exception as e:
        return
    cards = content.find_elements(By.CSS_SELECTOR, "div.jdgm-rev.jdgm-divider-top.jdgm--done-setup")
    for card in cards:
        rate_num = ""
        header = ""
        review = ""
        # find rating
        try:
            rating_con = card.find_element(By.CSS_SELECTOR, "div.jdgm-rev__header")
            # Locate the rating span element by class name
            rating_element = rating_con.find_element(By.CSS_SELECTOR, "span.jdgm-rev__rating")
        
            # Extract the rating value from the 'data-score' attribute
            rate_num = rating_element.get_attribute("data-score")
        except Exception as e:
            rate_num = ""
        # find review - header
        try:
            review_cont = card.find_element(By.CSS_SELECTOR, "div.jdgm-rev__content")
            
        except Exception as e:
            review_cont = None
        if review_cont:
            # header
            try:
                header = review_cont.find_element(By.CSS_SELECTOR, "b.jdgm-rev__title").text.strip()
            except Exception as e:
                header = ""
            # review
            try:
                review = review_cont.find_element(By.CSS_SELECTOR, "div.jdgm-rev__body").text.strip()
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
for i in tqdm(range(60)):
    resp = click_load_more()
    if not resp:
        break
    time.sleep(10)

scrape_page()
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

write_excel('URL3_MAGICM.xlsx')