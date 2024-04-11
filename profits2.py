import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
from pymongo import MongoClient

# Connect to MongoDB
mongodb_uri = os.environ.get('MONGODB_URI')

if mongodb_uri is None:
    raise ValueError("MongoDB URI not found in environment variables")

# Set the path to chromedriver.exe
chrome_driver_path = r"chromedriver"

# Set up Chrome options
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

# Set up Chrome service
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# URL to scrape
url = "https://hashrate.no/asics"

# Open the URL in the browser
browser.get(url)

# Get the page source
page_source = browser.page_source

# Close the browser
browser.quit()

# Parse the HTML content
soup = BeautifulSoup(page_source, 'html.parser')

# Find all the <li> elements within the specified <ul> with id="myUL"
li_elements = soup.find('ul', id='myUL').find_all('li')

# Get current time in Indian timezone
indian_timezone = pytz.timezone('Asia/Kolkata')
now = datetime.now(indian_timezone)
timestamp = now.strftime('%Y-%m-%d %I:%M %p')  # Format: YYYY-MM-DD HH:MM AM/PM

# List to store formatted data strings
formatted_data = []

# Iterate through each <li> element
for li in li_elements:
    # Extract text from the <li> element
    li_text = li
    # Format the data string with timestamp
    formatted_data.append(f"Timestamp: {timestamp}, Data: {li_text}")

try:
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)

    # Select the database
    db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

    # Select the collection
    collection = db.profits_2  # Use your desired collection name
    indian_timezone = pytz.timezone('Asia/Kolkata')
    now = datetime.now(indian_timezone)
    timeframe = now.strftime('%Y-%m-%d %I:%M %p') 
    # Insert formatted data list into MongoDB
    collection.insert_one({'formatted_data': formatted_data,"timestamp":timeframe})

    print("Data saved to MongoDB.")

except Exception as e:
    print("Error occurred while connecting to MongoDB:", e)
