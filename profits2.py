import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
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

# Dictionary to store extracted data by labels
data_dict = {}

# Get current time in Indian timezone
indian_timezone = pytz.timezone('Asia/Kolkata')
now = datetime.now(indian_timezone)
timestamp = now.strftime('%Y-%m-%d %I:%M %p')  # Format: YYYY-MM-DD HH:MM AM/PM

# Iterate through each <li> element
for li in li_elements:
    # Extract text from the <li> element
    li_text = li.get_text(separator="\n", strip=True)
    
    # Find the currency label, assuming it's the first line of the <li> text
    lines = li_text.split('\n')
    label = lines[0].strip()
    
    # Check if the label exists in the dictionary, if not, create a new list
    if label not in data_dict:
        data_dict[label] = []
    
    # Append the text and timestamp to the list under the label
    data_dict[label].append({"data": li_text, "timestamp": timestamp})

# Connect to MongoDB
mongodb_uri = os.environ.get('MONGODB_URI')
if mongodb_uri is None:
    raise ValueError("MongoDB URI not found in environment variables")

try:
    client = MongoClient(mongodb_uri)
    db = client.mydatabase # Get the default database
    collection = db.profits_2  # Collection name as 'profits_2'

    # Insert data_dict into the collection without removing existing data
    collection.insert_many(json.loads(json.dumps(data_dict)), ordered=False)
    print("Data extracted and saved to MongoDB collection 'profits_2'")
except Exception as e:
    print("Error occurred while connecting to MongoDB:", e)
