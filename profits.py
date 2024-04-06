from bs4 import BeautifulSoup
import requests
from pymongo import MongoClient
from datetime import datetime
import pytz  # Import pytz for timezone handling

indian_timezone = pytz.timezone('Asia/Kolkata')  # Set Indian timezone

url = "https://minerstat.com/hardware/asics"

try:
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for non-200 status codes
    html_content = response.text

    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

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
        updated_timestamp = now.strftime('%A, %b %d, %I %p')  # Updated timestamp format

        # Append extracted data to list
        data_list.append({
            'date': date_,
            'hour': f"{hour_} {am_pm}",
            'order': order,
            'title': title,
            'hashrate': hashrate,
            'power': power,
            'profit': profit_data,
            'formated_timestamp': updated_timestamp  # Add updated timestamp field
        })

    # MongoDB Connection URI
    uri = "mongodb+srv://ej818793:D9Lc0tVzhDSWHb8E@cluster0.n39bk48.mongodb.net/mydatabase?retryWrites=true&w=majority"

    # Create a new client and connect to the server
    client = MongoClient(uri)

    # Select the database
    db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

    # Select the collection
    collection = db.my_collection  # You can replace 'my_collection' with your desired collection name

    # Insert data_list into the collection without removing existing data
    collection.insert_many(data_list)

    print("Data saved to MongoDB.")

except requests.RequestException as e:
    print(f"Failed to retrieve data: {e}")

except Exception as e:
    print(f"An error occurred: {e}")
