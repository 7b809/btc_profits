from datetime import datetime
from pymongo import MongoClient
import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.dates import DateFormatter
from matplotlib.backends.backend_pdf import PdfPages
import io
import os


# MongoDB URI
mongodb_uri = os.environ.get('MONGODB_URI')

# Connect to MongoDB
print("Connecting to MongoDB...")
client = MongoClient(mongodb_uri)
print("Connected to MongoDB successfully!")

# Get the database
db = client.mydatabase

# Retrieve data from MongoDB collection
collection_name = 'profits_4'
print("Retrieving data from collection '{}'...".format(collection_name))
collection_data = list(db[collection_name].find())

# Convert ObjectId to string for each document
for document in collection_data:
    document['_id'] = str(document['_id'])

# Convert JSON string to Python object
data = json.dumps(collection_data, indent=4)
data = json.loads(data)

# Preprocess data
for entry in data:
    entry_data = entry.get('Data', [])
    for item in entry_data:
        # Convert profit to float
        profit_str = item.get('PROFIT', '0')
        item['PROFIT'] = float(profit_str.replace('$', '').replace(',', ''))

        # Calculate full profit
        power_consumption_str = item.get('POWER', '0W')
        try:
            power_consumption = float(power_consumption_str.strip('W').replace(',', '')) / 1000  # Convert to kW
            electricity_cost = power_consumption * 24 * 0.12  # Assuming electricity cost of $0.12 per kWh
            item['Full Profit'] = item['PROFIT'] + electricity_cost
        except ValueError:
            item['Full Profit'] = 0.0

# Group data by model name
model_data_dict = {}
for entry in data:
    entry_data = entry.get('Data', [])
    for item in entry_data:
        model_name = item.get('MODEL', 'Unknown')
        if model_name not in model_data_dict:
            model_data_dict[model_name] = []
        model_data_dict[model_name].append(item)

# Create PDF file
pdf_filename = "profits_4.pdf"
total_models = len(model_data_dict)
completed_models = 0

with PdfPages(pdf_filename) as pdf:
    for model_name, model_data in model_data_dict.items():
        # Increment counter for completed models
        completed_models += 1

        # Create scatter plots for profit and full profit
        fig, axs = plt.subplots(2, figsize=(24, 16))
        fig.suptitle(f"{model_name}\n{model_data[0]['POWER']}, {model_data[0]['BEST PRICE']}", fontsize=16)

        for ax, (label, data_key) in zip(axs, [('Profit', 'PROFIT'), ('Full Profit', 'Full Profit')]):
            x = [datetime.strptime(item['Timestamp'], "%Y-%m-%d %I:%M %p") for item in model_data]
            y = [item[data_key] for item in model_data]
            
            # Extract hour from the timestamp
            hours = [int(datetime.strptime(item['Timestamp'], "%Y-%m-%d %I:%M %p").strftime("%H")) for item in model_data]
            colors = cm.tab10([hour // 6 for hour in hours])  # Use hour to determine colors
            
            ax.scatter(x, y, label=label, color=colors)
            ax.set_ylabel('Profit ($)')
            ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
            ax.grid(True)

        axs[0].set_title('Profit')
        axs[1].set_title('Full Profit')

        # Add legend and adjust layout
        axs[0].legend(loc='upper left')
        axs[1].legend(loc='upper left')
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])

        # Save plot to PDF
        pdf.savefig()
        plt.close()

        # Print progress message for every 10 models completed
        if completed_models % 10 == 0:
            print(f"{completed_models} out of {total_models} models completed.")


print("PDF file saved to object data.")

# Save the PDF to MongoDB collection
collection = db.pdf_data

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
