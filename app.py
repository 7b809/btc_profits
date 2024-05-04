from flask import Flask, request, send_file
from pymongo import MongoClient
import os
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to your Flask application!'


@app.route('/get_pdf', methods=['GET'])
def get_pdf():
    filename = request.args.get('filename')
    if not filename:
        return 'Error: Missing filename parameter', 400
    
    # Read MongoDB URI from file
    with open('data.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.mydatabase  # Replace 'mydatabase' with your database name
    collection = db.pdf_data

    # Download the PDF File from MongoDB Atlas
    query = {"filename": filename}
    pdf_document = collection.find_one(query)
    if pdf_document:
        pdf_data = pdf_document["data"]
        
        # Convert the PDF data from bytes to a file-like object
        pdf_stream = BytesIO(pdf_data)
        
        # Return response with a message and the PDF file
        return f"""
            <html>
            <head>
                <title>PDF Download</title>
            </head>
            <body>
                <h1>Downloading PDF</h1>
                <p>Please wait while your PDF (<strong>{filename}</strong>) is being downloaded...</p>
            </body>
            </html>
        """, 200, {'Content-Type': 'application/pdf'}
    else:
        return 'Error: PDF document not found', 404
