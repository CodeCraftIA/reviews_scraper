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

url = "https://advanced.gg/products/haikyu-advanced-yubari-burst"

driver.get(url)

time.sleep(20)
ratings=[]
titles= []
ratings_texts=[]
# Function to click the "Load more" button
def click_load_more():
    try:
        # Wait until the "Load more" button is present in the DOM
        load_more_button = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'yotpo-reviews-pagination-item'))
        )
        # Scroll the button into view and click it using JavaScript
        driver.execute_script("arguments[0].scrollIntoView();", load_more_button)
        time.sleep(0.5)  # Give it a moment to scroll into view
        driver.execute_script("arguments[0].click();", load_more_button)
        return True
    #except (TimeoutException, NoSuchElementException):
    except Exception as e:
        return False

'''
# Click the "Load more" button until it disappears or is unclickable
while click_load_more():
    time.sleep(5)
    pass
'''
for i in tqdm(range(250)):
    res = click_load_more()
    time.sleep(3)
    if not res:
        break

time.sleep(10)
# After all reviews are loaded, you can scrape the data
reviews = driver.find_elements(By.CSS_SELECTOR, 'div.yotpo-review-card')  # Adjust the class name to match your review elements
print(len(reviews))
print("")
print("Starting the real process ")
print("")
# Extracting rating, title, and review text from each review
for review in tqdm(reviews):
    try:
        card_cont = review.find_element(By.CSS_SELECTOR, "div.card-container")
    except Exception as e:
        continue
    # Extract rating
    try:
        rating_element = card_cont.find_element(By.CSS_SELECTOR, "div.content-header")
        rating1 = rating_element.find_element(By.CSS_SELECTOR, "div.yotpo-star-rating")
        rate = rating1.find_element(By.CSS_SELECTOR, "span.sr-only").text.strip()
        rating = rate.replace("star rating", "")
    except NoSuchElementException:
        rating = 'N/A'
    
    # Extract title
    try:
        title_element = card_cont.find_element(By.CSS_SELECTOR, 'div.yotpo-review-title.yotpo-review-bold-title')
        title = title_element.text
    except NoSuchElementException:
        title = 'N/A'
    
    # Extract review text
    try:
        review_text_element = card_cont.find_element(By.CSS_SELECTOR, 'div.yotpo-review-content')
        review_text = review_text_element.text
    except NoSuchElementException:
        review_text = 'N/A'
    

    ratings.append(rating)
    titles.append(title)
    ratings_texts.append(review_text)
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

write_excel('advanced_URL4.xlsx')