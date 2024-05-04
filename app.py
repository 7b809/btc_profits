from flask import Flask, request, send_file
from pymongo import MongoClient
import os
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to your Flask application!'

@app.route('/pdfs')
def pdfs():
    # Read MongoDB URI from file
    with open('data.txt', 'r') as file:
        mongodb_uri = file.read().strip()
    
    # Connect to MongoDB Atlas
    client = MongoClient(mongodb_uri)
    db = client.mydatabase  # Replace 'mydatabase' with your database name
    collection = db.pdf_data

    # Retrieve all PDF documents from MongoDB Atlas
    pdf_documents = collection.find({})
    
    # Generate HTML to display links for each PDF file
    html = "<h1>Available PDFs</h1>"
    for pdf_document in pdf_documents:
        filename = pdf_document["filename"]
        html += f'<p><a href="/get_pdf?filename={filename}">{filename}</a></p>'
    
    return html

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

    # Download the requested PDF File from MongoDB Atlas
    query = {"filename": filename}
    pdf_document = collection.find_one(query)
    if pdf_document:
        pdf_data = pdf_document["data"]
        
        # Convert the PDF data from bytes to a file-like object
        pdf_stream = BytesIO(pdf_data)
        
        # Return the PDF file as an attachment
        return send_file(
            pdf_stream,
            as_attachment=True,
            attachment_filename=f'{filename}.pdf',
            mimetype='application/pdf'
        )
    else:
        return 'Error: PDF document not found', 404

if __name__ == "__main__":
    app.run(debug=True)
