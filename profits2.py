# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options as ChromeOptions
# from bs4 import BeautifulSoup
# import json
# from pymongo import MongoClient
# from datetime import datetime
# import os
# import pytz

# # Set the path to chromedriver.exe
# chrome_driver_path = r"chromedriver"

# # Set up Chrome options
# chrome_options = ChromeOptions()
# chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

# # Set up Chrome service
# chrome_service = ChromeService(executable_path=chrome_driver_path)

# # Create a new instance of the Chrome webdriver
# browser = webdriver.Chrome(service=chrome_service, options=chrome_options)

# # Load the webpage
# url = "https://hashrate.no/asics"
# browser.get(url)

# # Extract HTML content
# html_content = browser.page_source

# # Close the browser
# browser.quit()

# # Parse HTML using BeautifulSoup
# soup = BeautifulSoup(html_content, 'html.parser')

# # Find the <ul> element with id="myUL"
# ul_element = soup.find('ul', id='myUL')

# # Extract data from <li> elements and organize into labeled fields
# data_list = []
# for li_element in ul_element.find_all('li'):
#     # Extracting data from specific elements within <li>
#     item_name = li_element.find('div', class_='block deviceLink').find('a').text.strip()
#     estimated_roi = li_element.find('div', string='Estimated ROI:').find_next('div').text.strip()
#     profit = li_element.find('div', string='Profit').find_next('div').text.strip()
#     revenue = li_element.find('div', string='Revenue').find_next('div').text.strip()
#     # Constructing a dictionary for each item
#     item_data = {
#         'miner_name': item_name,
#         'estimated_roi': estimated_roi,
#         'profit': profit,
#         'revenue': revenue
#     }
#     data_list.append(item_data)

# # Connect to MongoDB
# mongodb_uri = os.environ.get('MONGODB_URI')
# if mongodb_uri is None:
#     raise ValueError("MongoDB URI not found in environment variables")
# client = MongoClient(mongodb_uri)

# # Select the database
# db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

# # Select the collection
# collection = db.profits_2  # Collection name as 'profits_2'

# # Insert data_list into the collection without removing existing data
# collection.insert_many(data_list, ordered=False)

# print("Data extracted and saved to MongoDB collection 'profits_2'")
