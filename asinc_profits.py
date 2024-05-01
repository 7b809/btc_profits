import re
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from pymongo import MongoClient
from datetime import datetime
import os
import pytz

# Retrieve MongoDB URI from environment variables
mongodb_uri = os.environ.get('MONGODB_URI')

# Check if the URI is provided
if mongodb_uri is None:
    raise ValueError("MongoDB URI not found in environment variables")

# Set Indian timezone
indian_timezone = pytz.timezone('Asia/Kolkata')

# Set the path to chromedriver.exe
chrome_driver_path = r"chromedriver"

# Set up Chrome options
chrome_options = ChromeOptions()
chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

# Set up Chrome service
chrome_service = ChromeService(executable_path=chrome_driver_path)

# Create a new instance of the Chrome webdriver
browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# URL of the webpage containing the table
url = "https://www.asicminervalue.com/"

# Load the webpage
browser.get(url)

# Wait for the page to load (adjust the time according to your needs)
time.sleep(2)

# Get the HTML content of the page
html_content = browser.page_source

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Find the table element by its ID
table = soup.find('table', {'id': 'datatable_profitability'})

# Initialize an empty list to store the data
data = []

# Get current time in Indian timezone
now = datetime.now(indian_timezone)
updated_timestamp = now.strftime('%A, %b %d, %Y, %I %p')  # Updated timestamp format

# Iterate over each row in the table
for row in table.find_all('tr'):
    # Initialize an empty dictionary for each row
    row_data = {}

    # Iterate over each cell in the row
    cells = row.find_all('td')
    if cells:
        row_data['name'] = cells[0].text.strip()
        row_data['date'] = cells[1].text.strip()
        row_data['hash_rate'] = cells[2].text.strip()
        row_data['power_consumption'] = cells[3].text.strip()
        row_data['noise_level'] = cells[4].text.strip()
        row_data['algorithm'] = cells[5].text.strip()
        row_data['rentability'] = cells[6].text.strip()
        row_data['updated_timestamp'] = updated_timestamp  # Add updated timestamp field

        # Append the row data to the list
        data.append(row_data)

# Close the browser
browser.quit()

# Connect to MongoDB
client = MongoClient(mongodb_uri)

# Select the database
db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

# Select the collection
collection = db.asinc_profits  # You can replace 'asinc_profits' with your desired collection name

# Insert data_list into the collection without removing existing data
collection.insert_many(data, ordered=False)

print("Data saved to MongoDB.")
