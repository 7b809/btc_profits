import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import pytz
from pymongo import MongoClient
import os

# Connect to MongoDB
# Connect to MongoDB
mongodb_uri = os.environ.get('MONGODB_URI')

if mongodb_uri is None:
    raise ValueError("MongoDB URI not found in environment variables")
indian_timezone = pytz.timezone('Asia/Kolkata')
now = datetime.now(indian_timezone)
timestamp = now.strftime('%Y-%m-%d %I:%M %p')  # Format: YYYY-MM-DD HH:MM AM/PM

#
# URL of the webpage to scrape
url = "https://minetheasic.com/"

# Send a GET request to the URL
response = requests.get(url)

# Parse the HTML content
soup = BeautifulSoup(response.content, "html.parser")

# Find all <div> elements with class="thread"
threads = soup.find_all("div", class_="thread")

# Find all <a> elements
links = soup.find_all("a")

# Initialize an empty list to store the extracted data
data = []

# Loop through each <a> tag
for link in links:
    # Initialize an empty dictionary for each entry
    entry = {}
    
    # Extract data from <div> elements with class="col" (labels)
    labels = []
    for thread in threads:
        cols = thread.find_all("div", class_="col")
        for col in cols:
            label = col.get_text(strip=True)
            labels.append(label)
    
    # Extract data from <a> elements (values)
    values = []
    details = link.find_all("div", class_="col")
    for detail in details:
        value = detail.get_text(strip=True)
        values.append(value)
    
    # Combine labels and values into entry
    for label, value in zip(labels, values):
        # Separate profit and payback time
        if label == "PROFIT":
            profit_match = re.search(r"\$\s*(\d+\.\d+)", value)
            if profit_match:
                profit = profit_match.group(1)
                entry[label] = profit
                entry['Timestamp'] = timestamp
            else:
                entry[label] = ""
            
            # Extract payback time separately
            payback_time_match = re.search(r"Payback Time([\d. ]+mo\.)", value)
            if payback_time_match:
                payback_time = payback_time_match.group(1)
                entry["PAYBACK TIME"] = payback_time
            else:
                entry["PAYBACK TIME"] = ""
        elif label == "#":
            entry["POSITION"] = value
        else:
            entry[label] = value
    
    # Append the entry to the main list
    data.append(entry)

# Remove the empty entries
data = [entry for entry in data if entry]


try:
    # Connect to MongoDB
    client = MongoClient(mongodb_uri)

    # Select the database
    db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

    # Select the collection
    collection = db.profits_4  # Use your desired collection name
    
    # Insert formatted data list into MongoDB
    collection.insert_one({'Data': data})

    print("Data saved to MongoDB.")

except Exception as e:
    print("Error occurred while connecting to MongoDB:", e)
