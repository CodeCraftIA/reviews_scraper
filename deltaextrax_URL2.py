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

url = "https://www.deltaextrax.com/product/delta-9-thc-250mg-gummies-resin-series/"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]
# Function to click the "Load more" button


def click_next_page():
    try:
        # Scroll to the pagination section
        pagination_element = driver.find_element(By.CSS_SELECTOR, "div.R-PaginationControls.u-marginBottom--sm")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_element)

        # Wait for the page to scroll and load properly
        time.sleep(0.8)

        # Find the active page number element
        current_page = driver.find_element(By.CSS_SELECTOR, "div.R-PaginationControls__item.isActive")

        # Find the next sibling element that represents the next page
        next_page = current_page.find_element(By.XPATH, "following-sibling::div[contains(@class, 'R-PaginationControls__item') and not(contains(@class, 'isActive'))]")

        # Check if next_page exists and is clickable
        if next_page and next_page.get_attribute("role") == "button":
            # Scroll to the next button to ensure it's in view
            actions = ActionChains(driver)
            actions.move_to_element(next_page).click().perform()

            # Wait for the next page to load after clicking
            time.sleep(0.4)
            
            return True
        else:
            return False  # No more pages to click

    except Exception as e:
        print(f"Error clicking the next page: {e}")
        return False


def scrape_page():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.ElementsWidget__inner")
    except Exception as e:
        return
    cards = content.find_elements(By.CSS_SELECTOR, "div.R-ContentList__item.u-textLeft--all")
    for card in cards:
        rating_value = ""
        header_title_text = ""
        review_text = ""
        # Extract rating value
        try:
            rating_element = card.find_element(By.CSS_SELECTOR, "div.R-RatingStars__stars")
            rating_value = rating_element.get_attribute("title").split()[0]  # Extracting '5' from '5 Stars'
        except Exception as e:
            rating_value = None

        # Extract header-title text
        try:
            doubles = card.find_element(By.CSS_SELECTOR, "div.c-item__attributesGroup")
            header_title_element = doubles.find_elements(By.CSS_SELECTOR, "div.R-TextBody.R-TextBody--xxxs.u-marginBottom--none.u-textSentenceCase")
            header_title_text = header_title_element[1].text.strip()
        except Exception as e:
            header_title_text = None

        # Extract review text
        try:
            review_element = card.find_element(By.CSS_SELECTOR, "div.R-TextBody.R-TextBody--xs")
            review_text = review_element.text.strip()
        except Exception as e:
            review_text = None
        ratings.append(rating_value)
        titles.append(header_title_text)
        ratings_texts.append(review_text)

'''
# Click the "Load more" button until it disappears or is unclickable
while click_load_more():
    time.sleep(5)
    pass
'''
for i in tqdm(range(105)):
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

write_excel('URL2_DELTAEXTRAX.xlsx')