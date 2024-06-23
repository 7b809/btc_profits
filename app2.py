from flask import Flask, send_file
import os
import pymongo
import zipfile
import shutil

app = Flask(__name__)

# Function to connect to MongoDB and download zip files
def download_zip_files(target_mongo_url, target_db_name, collections_names):
    # Connect to the MongoDB client
    client = pymongo.MongoClient(target_mongo_url)
    db = client[target_db_name]

    for target_collection_name in collections_names:
        collection = db[target_collection_name]
        print(f"Connected to MongoDB collection '{target_collection_name}' in database '{target_db_name}'.")

        # Directory to save the downloaded zip files
        download_folder = f"{target_collection_name}_zip"
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)

        # Fetch all documents in the collection
        documents = list(collection.find())
        total_documents = len(documents)
        print(f"Total documents found: {total_documents}")

        # Download each zip file
        for idx, doc in enumerate(documents):
            filename = doc["filename"]
            filedata = doc["filedata"]

            # Save the file locally
            output_path = os.path.join(download_folder, filename)
            with open(output_path, "wb") as file:
                file.write(filedata)

            print(f"Downloaded '{filename}' ({idx + 1}/{total_documents}).")

    # Close the MongoDB connection
    client.close()
    print("MongoDB connection closed.")

# Function to extract zip files and find common files
def process_zip_files(collections_names):
    file_dict = {}

    for target_collection_name in collections_names:
        download_folder = f"{target_collection_name}_zip"
        extracted_folder = f"{target_collection_name}_extracted"
        if not os.path.exists(extracted_folder):
            os.makedirs(extracted_folder)

        for zip_file in os.listdir(download_folder):
            zip_file_path = os.path.join(download_folder, zip_file)
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extracted_folder)

            for extracted_file in os.listdir(extracted_folder):
                file_name, file_extension = os.path.splitext(extracted_file)
                if file_name not in file_dict:
                    file_dict[file_name] = {}
                file_dict[file_name][target_collection_name] = os.path.join(extracted_folder, extracted_file)

    # Create folders for common files and move them
    output_base_folder = "common_files"
    if not os.path.exists(output_base_folder):
        os.makedirs(output_base_folder)

    for file_name, file_paths in file_dict.items():
        if len(file_paths) == len(collections_names):
            common_folder = os.path.join(output_base_folder, f"{file_name}_files")
            if not os.path.exists(common_folder):
                os.makedirs(common_folder)

            for collection_name, file_path in file_paths.items():
                os.rename(file_path, os.path.join(common_folder, os.path.basename(file_path)))


    return output_base_folder

# Route to display a welcoming message
@app.route('/')
def index():
    return 'Welcome to your Flask application!'

# Route to fetch and return common files as a zip
@app.route('/get_cfiles_zip', methods=['GET'])
def get_cfiles_zip():
    # Read MongoDB URI from file
    with open('data2.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Download zip files from MongoDB
    target_db_name = "zip_files"
    collections_names = ["json_files", "excel_files", "img_files"]
    download_zip_files(mongodb_uri, target_db_name, collections_names)

    # Process zip files and find common files
    output_base_folder = process_zip_files(collections_names)

    # Create the final zip file containing all the common files
    final_zip_path = 'common_files.zip'
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(output_base_folder):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), output_base_folder))
    print(f"All common files have been zipped into {final_zip_path}.")

    # Clean up the common files directory
    shutil.rmtree(output_base_folder)

    # Return the combined zip file as an attachment
    return send_file(
        final_zip_path,
        as_attachment=True,
        download_name='common_files.zip',
        mimetype='application/zip'
    )

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0', port=5000)
