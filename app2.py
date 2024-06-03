from flask import Flask, send_file
from pymongo import MongoClient
import os
import zipfile
import shutil
from gridfs import GridFS

app = Flask(__name__)

# Function to fetch and save a zip file from MongoDB GridFS
def fetch_and_save_zip(collection_name, filename, db):
    try:
        grid_fs = GridFS(db, collection_name)
        grid_out = grid_fs.find_one({})
        if grid_out:
            with open(filename, 'wb') as f:
                f.write(grid_out.read())
            print(f"Saved {filename} locally.")
        else:
            print(f"No file found in collection {collection_name}.")
    except Exception as e:
        print(f"Error fetching file from collection {collection_name}: {e}")

# Function to create the final zip file containing all fetched zip files
def create_final_zip(final_zip_path, final_zip_dir):
    with zipfile.ZipFile(final_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(final_zip_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), final_zip_dir))
    print(f"All files have been zipped into {final_zip_path}.")

@app.route('/')
def index():
    return 'Welcome to your Flask application!'

@app.route('/download_all_zips', methods=['GET'])
def download_all_zips():
    # Read MongoDB URI from file
    with open('data2.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB using URI from file
    client = MongoClient(mongodb_uri)
    db = client.zip_files

    # Directory to save individual zip files
    final_zip_dir = "final_zip"
    if not os.path.exists(final_zip_dir):
        os.makedirs(final_zip_dir)

    # Fetch and save each zip file
    fetch_and_save_zip("json_files", os.path.join(final_zip_dir, 'json_files.zip'), db)
    fetch_and_save_zip("excel_files", os.path.join(final_zip_dir, 'excel_files.zip'), db)
    fetch_and_save_zip("img_files", os.path.join(final_zip_dir, 'img_files.zip'), db)

    # Create the final zip file containing all the fetched zip files
    final_zip_path = 'all_files.zip'
    create_final_zip(final_zip_path, final_zip_dir)

    # Clean up temporary directory
    shutil.rmtree(final_zip_dir)

    # Return the combined zip file as an attachment
    return send_file(
        final_zip_path,
        as_attachment=True,
        download_name='all_files.zip',
        mimetype='application/zip'
    )

if __name__ == "__main__":
    app.run(debug=True)
