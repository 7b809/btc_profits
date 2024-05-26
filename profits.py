from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime
import os
import pytz
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

def scrape_and_save_to_mongodb():
    try:
        # Retrieve MongoDB URI from environment variables
        mongodb_uri = os.environ.get('MONGODB_URI')

        # Check if the URI is provided
        if mongodb_uri is None:
            raise ValueError("MongoDB URI not found in environment variables")

        # Set Indian timezone
        indian_timezone = pytz.timezone('Asia/Kolkata')

        url = "https://minerstat.com/hardware/asics"

        # Set the path to chromedriver.exe
        chrome_driver_path = r"chromedriver"

        # Set up Chrome options
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--headless')  # Run Chrome in headless mode (no GUI)

        # Set up Chrome service
        chrome_service = ChromeService(executable_path=chrome_driver_path)

        # Create a new instance of the Chrome webdriver
        browser = webdriver.Chrome(service=chrome_service, options=chrome_options)
        # Open the URL in the browser
        browser.get(url)

        # Get the page source
        page_source = browser.page_source

        # Close the browser
        browser.quit()

        # Parse the HTML content
        soup = BeautifulSoup(page_source, 'html.parser')

        # Initialize list to store extracted data
        data_list = []

        for div_tr in soup.find_all('div', class_='tr'):
            # Extracting data from div with class = tr
            order_element = div_tr.find('div', class_='flexOrder')
            if order_element:
                order = order_element.text.strip()
            else:
                continue  # Skip this entry if order number not found

            title_element = div_tr.find('div', class_='flexHardware').find('a', title=True)
            if title_element:
                title = title_element.get('title')
            else:
                continue  # Skip this entry if title not found

            hashrate_element = div_tr.find('div', class_='flexHashrate')
            if hashrate_element:
                hashrate = hashrate_element.text.strip()
            else:
                continue  # Skip this entry if hashrate not found

            power_element = div_tr.find('div', class_='flexPower')
            if power_element:
                power = power_element.text.strip()
            else:
                continue  # Skip this entry if power not found

            profit_data = {}
            for div_coin in div_tr.find_all('div', class_='coin'):
                coin_title_element = div_coin.find('a', title=True)
                if coin_title_element:
                    coin_title = coin_title_element.get('title')
                else:
                    continue  # Skip this entry if coin title not found

                coin_profit_element = div_coin.find('div', class_='text').find('b')
                if coin_profit_element:
                    coin_profit = coin_profit_element.text
                    # Calculate monthly profit from daily profit
                    usd_profit = float(coin_profit.split()[0])  # Assuming the profit is in USD
                    monthly_profit_usd = usd_profit * 30  # Assuming 30 days in a month
                    monthly_profit_usd_str = "{:.2f} USD".format(monthly_profit_usd)
                else:
                    continue  # Skip this entry if coin profit not found

                profit_data[coin_title] = {
                    'daily_profit': coin_profit,
                    'monthly_profit_usd': monthly_profit_usd_str
                }

            # Get current time in Indian timezone
            now = datetime.now(indian_timezone)
            date_ = now.strftime('%Y-%m-%d')
            hour_ = now.strftime('%I')  # 12-hour format
            am_pm = now.strftime('%p')  # AM/PM indicator
            updated_timestamp = now.strftime('%A, %b %d, %Y, %I %p')  # Updated timestamp format

            # Append extracted data to list
            data_list.append({
                'date': date_,
                'hour': f"{hour_} {am_pm}",
                'order': order,
                'title': title,
                'hashrate': hashrate,
                'power': power,
                'profit': profit_data,
                'updated_timestamp': updated_timestamp  # Add updated timestamp field
            })

        # Connect to MongoDB
        client = MongoClient(mongodb_uri)

        # Select the database
        db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

        # Select the collection
        collection = db.profits_3  # Use your desired collection name

        # Insert data_list into the collection without removing existing data
        collection.insert_many(data_list)

        print("Data saved to MongoDB.")

    except Exception as e:
        print(f"An error occurred: {e}")

# Call the function to scrape and save to MongoDB
scrape_and_save_to_mongodb()
