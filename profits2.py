from bs4 import BeautifulSoup
import json
from datetime import datetime
import pytz
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from pymongo import MongoClient

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

# List to store formatted data
formatted_data = []

# Iterate through each <li> element
for li in li_elements:
    try:
        # Extracting machine name
        machine_name = li.find('div', class_='deviceHeader2').text.strip()

        # Extracting original profits, calculated profits, calculated revenue, and currency for highest profit
        highest_profit_table = li.find_all('table')[0]
        highest_profit_data = highest_profit_table.find_all('td')
        highest_profit_original_profits = highest_profit_data[1].text.strip()
        highest_profit_calculated_profits = highest_profit_data[2].text.strip()
        highest_profit_calculated_revenue = str(
            float(highest_profit_original_profits[1:].replace(',', '')) - float(
                highest_profit_calculated_profits[1:].replace(',', '')))
        highest_profit_currency = highest_profit_data[0].text.strip()

        # Extracting original profits, calculated profits, calculated revenue, and currency for profit 24h
        profit_24h_table = li.find_all('table')[3]
        profit_24h_data = profit_24h_table.find_all('td')
        profit_24h_original_profits = profit_24h_data[1].text.strip()
        profit_24h_calculated_profits = profit_24h_data[2].text.strip()
        profit_24h_calculated_revenue = str(
            float(profit_24h_original_profits[1:].replace(',', '')) - float(
                profit_24h_calculated_profits[1:].replace(',', '')))
        profit_24h_currency = profit_24h_data[0].text.strip()

        # Constructing the final dictionary
        data = {
            "timestamp": timestamp,
            "machine_name": machine_name,
            "highest_profit": {
                "original_profits": highest_profit_original_profits,
                "calculated_profits": highest_profit_calculated_profits,
                "calculated_revenue": f"${highest_profit_calculated_revenue}",
                "currency": highest_profit_currency
            },
            "profit_24h": {
                "original_profits_24h": profit_24h_original_profits,
                "calculated_profits_24h": profit_24h_calculated_profits,
                "calculated_revenue_24h": f"${profit_24h_calculated_revenue}",
                "currency": profit_24h_currency
            }
        }
        formatted_data.append(data)
    except AttributeError:
        print("Error: 'deviceHeader2' element not found. Skipping this entry.")

try:
    mongodb_uri = os.environ.get('MONGODB_URI')

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
    if formatted_data:
        collection.insert_one({'formatted_data': formatted_data,"timestamp":timeframe})
    
        print("Data saved to MongoDB.")
    else:
        print("Data empty, do not saved to mongodb")

except Exception as e:
    print("Error occurred while connecting to MongoDB:", e)
