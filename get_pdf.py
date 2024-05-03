
from datetime import datetime
from pymongo import MongoClient
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_pdf import PdfPages
import io

mongodb_uri = os.environ.get('MONGODB_URI')


# MongoDB URI

# Print database connection status
print("Connecting to MongoDB...")
client = MongoClient(mongodb_uri)
print("Connected to MongoDB successfully!")

# Get the database
db = client.mydatabase  # You can replace 'mydatabase' with your desired database name

# Get the collection
collection_name = 'asinc_profits'
print("Retrieving data from collection '{}'...".format(collection_name))
collection_data = list(db[collection_name].find())

# Convert ObjectId to string for each document
for document in collection_data:
    document['_id'] = str(document['_id'])

# Parse JSON string to Python object
data = json.dumps(collection_data, indent=4)
data = json.loads(data)

current_year = datetime.now().year
# Preprocess data
for item in data:
    # Modify profit column
    item['profit'] = item['rentability']
    profit_str = item['profit']
    # Extracting only the numerical value
    try:
        profit_num = float(profit_str.split('$')[1].split('/')[0])
    except IndexError:
        # Handle cases where the format doesn't match expected pattern
        profit_num = None
    item['profit'] = profit_num

    # Convert timestamp to datetime object
    timestamp_str = item['updated_timestamp']
    timestamp_datetime = datetime.strptime(timestamp_str, "%A, %b %d, %Y, %I %p")
    # Check if timestamp contains year, if not, replace with current year
    if timestamp_datetime.year == 1900:
        timestamp_datetime = timestamp_datetime.replace(year=current_year)
    # Format timestamp to include only the hour part
    timestamp_hour = timestamp_datetime.strftime('%Y-%m-%d %H')
    item['timestamp'] = timestamp_hour

# Filter out entries with None profit values
data = [item for item in data if item['profit'] is not None]

# Create a dictionary to store data grouped by machine name
machine_data_dict = {}
for item in data:
    name = item['name']
    if name not in machine_data_dict:
        machine_data_dict[name] = []
    machine_data_dict[name].append(item)

# Combine all the machine data into a single dictionary
combined_data = {}
for idx, (name, items) in enumerate(machine_data_dict.items()):
    combined_data[f"Sheet_{idx}"] = items

print("Data saving to object type.")
all_data = json.dumps(combined_data, indent=4)
print("Data storing completed.")

# Load combined data from JSON string
combined_data = json.loads(all_data)

# Define a function to categorize hours into six-hour intervals
def categorize_hour(hour):
    if hour >= 0 and hour < 6:
        return '00:00 - 05:59'
    elif hour >= 6 and hour < 12:
        return '06:00 - 11:59'
    elif hour >= 12 and hour < 18:
        return '12:00 - 17:59'
    else:
        return '18:00 - 23:59'

# Define color map
try:
    cmap = cm.get_cmap('tab10', 4)
except ValueError:
    cmap = cm.tab10


# Sort the combined data by profit in descending order
sorted_combined_data = {k: v for k, v in sorted(combined_data.items(), key=lambda item: max(item[1], key=lambda x: x['profit'])['profit'], reverse=True)}

# Create a PDF object to save plots
with PdfPages("all_plots_sorted.pdf") as pdf:
    # Iterate over each sheet in sorted_combined_data
    for idx, (sheet_name, sheet_data) in enumerate(sorted_combined_data.items(), start=1):
        # Create a new figure for each sheet
        plt.figure(figsize=(24, 11))

        # Convert sheet data to DataFrame
        df = pd.DataFrame(sheet_data)

        # Convert timestamp to datetime if it's not already in datetime format
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        # Apply the function to create a new column 'hour_category'
        df['hour_category'] = df['timestamp'].dt.hour.apply(categorize_hour)

        # Plot scatter plot
        # Iterate over each hour category
        for category, group in df.groupby('hour_category'):
            
            plt.scatter(group['timestamp'], group['profit'], label=category, color=cmap(group['timestamp'].dt.hour.iloc[0] // 6), alpha=0.5)

            


        plt.title(f"{df['name'][0]} {sheet_name} Profits")
        plt.xlabel('Timestamp')
        plt.ylabel('Profit ( $ )')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability

        # Customize x-axis ticks to display only specific dates or intervals
        plt.gca().get_xaxis().set_major_locator(plt.MaxNLocator(6))  # Display only 6 ticks
        plt.gca().get_xaxis().set_major_formatter(DateFormatter('%Y-%m-%d'))  # Format the tick labels as desired

        plt.legend(title='Hour Category', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Save the current figure to the PDF
        pdf.savefig()
        plt.close()

        # Print completion message for every 10 images
        if idx % 10 == 0:
            print(f"{idx} out of {len(sorted_combined_data)} sheets processed.")

    # Print completion message
    print("Plots for all sheets sorted by profits merged into PDF.")
# After saving the PDF, proceed to save it into MongoDB
# Define the filename for the PDF
pdf_filename = "all_plots_sorted.pdf"

collection = db.pdf_data  # Define the collection to store PDF data

# Check if a document with the same filename exists
existing_pdf = collection.find_one({"filename": pdf_filename})

# If a document with the same filename exists, delete it
if existing_pdf:
    print(f"A PDF with the filename '{pdf_filename}' already exists. Deleting existing document...")
    collection.delete_one({"_id": existing_pdf["_id"]})

# Read the PDF file content
with open(pdf_filename, 'rb') as file:
    pdf_binary_data = file.read()

# Insert the PDF binary data and filename into the collection
pdf_document = {
    "filename": pdf_filename,
    "data": pdf_binary_data
}
collection.insert_one(pdf_document)

print("PDF file saved to MongoDB collection.")
