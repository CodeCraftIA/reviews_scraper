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

url = "https://forwellness.com/products/the-good-stuff-focus"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]
# Function to click the "Load more" button


def click_next_page():
    try:
        # Scroll to the pagination section
        pagination_element = driver.find_element(By.CSS_SELECTOR, "div.R-PaginationControls")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", pagination_element)

        # Wait for the page to scroll and load properly
        time.sleep(0.7)

        # Find the active page
        active_page = driver.find_element(By.CSS_SELECTOR, "div.R-PaginationControls__item.isActive")
        
        # Find the next sibling element to the active page
        next_page = active_page.find_element(By.XPATH, "following-sibling::div[1]")
        
        # Check if the next page is a number or the ellipsis (which indicates more pages)
        if next_page.get_attribute("data-type") == "text":
            return False  # Reached the end or needs a different approach to handle ellipsis

        # Scroll to the next button to ensure it's in view
        actions = ActionChains(driver)
        actions.move_to_element(next_page).click().perform()

        # Wait for the next page to load after clicking
        time.sleep(0.3)
        
        return True
    except Exception as e:
        print(f"Error clicking the next page: {e}")
        return False

def scrape_page():
    try: 
        content = driver.find_element(By.CSS_SELECTOR, "div.ElementsWidget__list")
    except Exception as e:
        return
    cards = content.find_elements(By.CSS_SELECTOR, "div.R-ContentList__item.u-textLeft--all")
    for card in cards:
        rate_num = ""
        header = ""
        review = ""
        try:
            review_tab = card.find_element(By.CSS_SELECTOR, "div.item__review")
        except Exception as e:
            continue

        try:
            # Locate the star rating div
            rating_element = review_tab.find_element(By.CSS_SELECTOR, "div.R-RatingStars__stars")
            
            # Get the value of the title attribute, which contains the star rating
            star_rating = rating_element.get_attribute("title")
            
            rate_num = star_rating.replace(" Stars", "")  # e.g., "5 Stars"
        except Exception as e:
            rate_num = ""
        # find review - header
        # header
        try:
            header = review_tab.find_element(By.CSS_SELECTOR, "div.R-TextHeading.R-TextHeading--xxs.u-textLeft--all").text.strip()
        except Exception as e:
            header = ""
        # review
        try:
            review = review_tab.find_element(By.CSS_SELECTOR, "div.R-TextBody.R-TextBody--xs.u-textLeft--all.u-whiteSpace--prewrap").text.strip()
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
for i in tqdm(range(62)):
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

write_excel('URL2_forwellness.xlsx')