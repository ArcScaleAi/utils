import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from docx import Document
from docx.shared import Inches
import pyautogui


# to save in excel instead of word

import pandas as pd

# to save in json instead of excel
import json



# Your Google credentials
google_username = 'xyz15122004@gmail.com'
google_password = 'MayankKul@123'

# Path to the folder containing images
IMAGE_FOLDER = "D:\Image"

# Initialize WebDriver with detailed logging
def initialize_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # Run in headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-insecure-localhost')
    options.add_argument('--disable-web-security')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--remote-debugging-port=9222')
    options.add_argument('--disable-extensions')
    options.add_argument('--log-level=0')  # Detailed logging
    options.add_argument('--v=1')  # Verbose logging level
    # google profile
    

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

driver = initialize_driver()
cnt=0
# Retry decorator
def retry(retries=3, delay=5, backoff=2):
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = retries, delay
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except (TimeoutException, WebDriverException) as e:
                    print(f"Retrying due to {str(e)}. {mtries-1} tries left...")
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            raise Exception("Max retries exceeded")
        return f_retry
    return deco_retry

def process(detail):
    detail=detail.split("\n")
    if len(detail)<=1:
        return ["No fashion details found"]
    ans=[]
    category=""
    for i in range(len(detail)):
        if '%' in detail[i]: 
            print(category+' '+detail[i-1]+"="+detail[i])
            ans.append(category+' '+detail[i-1]+"="+detail[i])
        elif '%' not in detail[i] and '%' not in detail[i+1]:
            category=detail[i]
    return ans

@retry(retries=3, delay=5)
def login_with_google(driver):
    try:
        print("Opening login page...")
        driver.get('https://dashboard.dragoneye.ai/login')

        print("Clicking 'Sign in with Google' button...")
        google_signin_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[2]/div/div[3]/div/div/div[1]/form/ul/li[1]/button'))
        )
        google_signin_button.click()

        print("Waiting for Google login window...")
        WebDriverWait(driver, 20).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])

        print("Entering email...")
        email_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'identifierId'))
        )
        email_field.send_keys(google_username)
        driver.find_element(By.ID, 'identifierNext').click()

        print("Waiting for password field...")
        pswxpath='//*[@id="password"]/div[1]/div/div[1]/input'
        password_field = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, pswxpath))
        )

        print("Entering password...")
        password_field.send_keys(google_password)
        driver.find_element(By.ID, 'passwordNext').click()

        print("Waiting for login to complete...")
        WebDriverWait(driver, 20).until(
            EC.number_of_windows_to_be(1)
        )
        driver.switch_to.window(driver.window_handles[0])

        print("Verifying login success...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div/div[3]/div[1]/div/h2'))
        )

        print("Navigating to demo page...")
        demo_page_link = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="__next"]/div[2]/main/div[1]/div/div[3]/div[1]/div/a'))
        )
        demo_page_link.click()

    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()  # Ensure to close the browser session on error
        raise

@retry(retries=3, delay=5)
def upload_image_and_get_details(driver, image_path):
    try:
        print(f"Uploading image: {image_path}")
        # shift to another tab
        driver.switch_to.window(driver.window_handles[1])
        xpath=""
        if cnt==0:
            xpath = '//*[@id="demo"]/div/div/div[1]'
        else:
            xpath = '//*[@id="demo"]/div/div[1]/div/div[2]/div[2]'
        print(xpath)
        select_image_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        select_image_button.click()
        # image select browser box opened
        time.sleep(3)
        pyautogui.write(image_path)
        pyautogui.press('enter')
        
        
        print("Waiting for processing...")
        time.sleep(10)  # Adjust based on actual time needed for processing

        print("Retrieving details...")
        details_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="demo"]/div/div[2]'))
        )
        details_text = details_element.text

        return details_text

    except Exception as e:
        print(f"Error uploading {image_path}: {e}")
        return None
try:
    # Log in to the website
    login_with_google(driver)

    # Initialize a json file
    with open("Image_Details.json", "w") as json_file:
        json_file.write("[")
        # Process each image in the folder
        imageslist=os.listdir(IMAGE_FOLDER)
        for i in range(len(imageslist)):
            image_name = imageslist[i]
            if image_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                image_path = os.path.join(IMAGE_FOLDER, image_name)
                
                # Upload image and get details from Dragoneye.ai
                details = upload_image_and_get_details(driver, image_path)
                cnt+=1
                if details:
                    # Save the details in the json file
                    json_file.write(json.dumps({image_name: process(details)}, indent=4))
                    if (i!=len(imageslist)-1):
                        json_file.write(",")
                    print(f"Details for {image_name} added to the json file")
                else:
                    print(f"Details for {image_name} could not be retrieved")
        json_file.write("]")    
    # Save the json file
    print("Image details saved in Image_Details.json")

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Close the browser
    if driver:
        driver.quit()
