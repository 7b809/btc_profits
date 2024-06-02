from flask import Flask, request, send_file
from pymongo import MongoClient
import os
from io import BytesIO
from gridfs import GridFS

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to your Flask application!'

@app.route('/zip_files')
def zip_files():
    # Read MongoDB URI from file
    with open('data1.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.zip_files  # The database name is 'zip_files'

    # Get all collection names in the database
    collection_names = db.list_collection_names()
    
    # Generate HTML to display links for each zip file
    html = "<h1>Available Zip Files</h1>"
    for collection_name in collection_names:
        html += f'<p><a href="/get_zip?filename={collection_name}">{collection_name}</a></p>'
    
    return html

@app.route('/get_zip', methods=['GET'])
def get_zip():
    filename = request.args.get('filename')
    if not filename:
        return 'Error: Missing filename parameter', 400
    
    # Read MongoDB URI from file
    with open('data1.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.zip_files  # The database name is 'zip_files'
    fs = GridFS(db, collection=filename)  # The collection name is the filename
    
    # Find the zip file in the specified collection
    zip_file = fs.find_one({"filename": filename})
    if zip_file:
        zip_data = zip_file.read()
        
        # Convert the zip data from bytes to a file-like object
        zip_stream = BytesIO(zip_data)
        
        # Return the zip file as an attachment
        return send_file(
            zip_stream,
            as_attachment=True,
            download_name=f"{filename}.zip",
            mimetype='application/zip'
        )
    else:
        return 'Error: Zip file not found', 404

@app.route('/download_all_zips', methods=['GET'])
def download_all_zips():
    # Read MongoDB URI from file
    with open('data1.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.zip_files  # The database name is 'zip_files'

    # Create a BytesIO stream to store all zips
    all_zips_stream = BytesIO()

    with zipfile.ZipFile(all_zips_stream, 'w', zipfile.ZIP_DEFLATED) as all_zips:
        # Get all collection names in the database
        collection_names = db.list_collection_names()

        for collection_name in collection_names:
            fs = GridFS(db, collection=collection_name)
            zip_file = fs.find_one({"filename": collection_name})
            if zip_file:
                zip_data = zip_file.read()
                # Write the zip data to the zip file in the stream
                all_zips.writestr(f"{collection_name}.zip", zip_data)
    
    # Seek to the start of the BytesIO stream
    all_zips_stream.seek(0)
    
    # Return the combined zip file as an attachment
    return send_file(
        all_zips_stream,
        as_attachment=True,
        download_name='all_zips.zip',
        mimetype='application/zip'
    )

if __name__ == "__main__":
    app.run(debug=True)
