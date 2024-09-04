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

url = "https://hellobatch.com/products/thc-gummies"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]


def click_next_page():
    try:
        # Scroll to the pagination section
        pagination_element = driver.find_element(By.CSS_SELECTOR, "div.jdgm-paginate")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_element)

        # Wait for the page to scroll and load properly
        time.sleep(0.7)

        # Find the next page element using the next button
        next_page_button = driver.find_element(By.CSS_SELECTOR, "a.jdgm-paginate__page.jdgm-paginate__next-page")

        # If the next page is not the last page
        if "jdgm-paginate__last-page" not in next_page_button.get_attribute("class"):
            actions = ActionChains(driver)
            actions.move_to_element(next_page_button).click().perform()

            # Wait for the next page to load after clicking
            time.sleep(0.3)

            return True
        else:
            return False  # Reached the last page
    except Exception as e:
        print(f"Error clicking the next page: {e}")
        return False

def scrape_page():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.jdgm-rev-widg__reviews")
    except Exception as e:
        return
    cards = content.find_elements(By.CSS_SELECTOR, "div.jdgm-rev.jdgm-divider-top.jdgm--done-setup")
    for card in cards:
        rate_num = ""
        header = ""
        review = ""
        try:
            # Locate the star rating div
            rating_element = card.find_element(By.CSS_SELECTOR, "div.jdgm-rev__header")
            rating = rating_element.find_element(By.CSS_SELECTOR, "span.jdgm-rev__rating")
            # Get the value of the title attribute, which contains the star rating
            rate_num = rating.get_attribute("data-score")
        except Exception as e:
            rate_num = ""
        # find review - header
        try:
            text_content = card.find_element(By.CSS_SELECTOR, "div.jdgm-rev__content")
        except Exception as e:
            text_content = ""
        # header
        try:
            header = text_content.find_element(By.CSS_SELECTOR, "b.jdgm-rev__title").text.strip()
        except Exception as e:
            header = ""
        # review
        try:
            review = text_content.find_element(By.CSS_SELECTOR, "div.jdgm-rev__body").text.strip()
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
for i in tqdm(range(138)): #138
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

write_excel('hello_batch_thc-gummies_reviews.xlsx')