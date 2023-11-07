from flask import Flask, request, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from typing import Any


app = Flask(__name__)

# database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:mysecretpassword@localhost/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 
db=SQLAlchemy(app)
app.app_context().push()


# Define the model representing your PostgreSQL table
@dataclass
class FileData(db.Model):
    __tablename__ = 'file_data'

    id: int
    userId:str 
    fileName:str
    timeStamp:str
    fileDump:Any

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    fileName = db.Column(db.String)
    timeStamp = db.Column(db.String)
    fileDump = db.Column(db.JSON)


# ========================================= Service Layer



# =========================================


# API to get receipt
@app.route('/receipt/<userId>', methods=['GET'])
def get_receipt(userId):
    timestamp = request.args.get('date')
    # Implement logic to fetch receipt for the given user and date
    # For demonstration, let's just return a sample response

    if timestamp:
        # Fetch data by timestamp and user ID
        data = FileData.query.filter_by(userId=userId, timeStamp=timestamp).first()
        if data:
            return jsonify(data)  # Assuming you have a serialize method in your model
        else:
            return jsonify({'message': 'Data not found for provided userId and timestamp'})
    else:
        # Fetch data only by user ID
        data = FileData.query.filter_by(userId=userId).all()
        if data:
            return jsonify(data)  # Assuming you have a serialize method in your model
        else:
            return jsonify({'message': 'No data found for the provided userId'})

# API to delete receipt
@app.route('/receipt/<receiptNumber>', methods=['DELETE'])
def delete_receipt(receiptNumber):
    # Implement logic to delete receipt by receipt number
    # For demonstration, let's just return a sample response
    return jsonify({"message": f"Receipt {receiptNumber} deleted"})

# API to extract data from image
@app.route('/extract/<userId>', methods=['POST'])
def extract_data_from_image(userId):
    if 'file' in request.files:
        # store file to server
        file = request.files["file"]
        if file.filename == "":
            return "No selected file",400
        
        timeStamp=datetime.now().isoformat()
        fileName=file.filename+"-"+timeStamp
        file.save('files/'+fileName)

        # TODO: call python function
        mlResponse={"dummy":123}
        extractedData={"userId":userId,"fileName":fileName,"timeStamp":timeStamp,"fileDump":mlResponse}

        new_file_data = FileData(
            userId=userId,
            fileName=fileName,
            timeStamp=timeStamp,
            fileDump=mlResponse
        )

        db.session.add(new_file_data)
        db.session.commit()

        return jsonify(new_file_data)
    else:
        return jsonify({"error": "No image found in the request"}), 400

# API to save receipt
@app.route('/receipt', methods=['POST'])
def save_receipt():
    if request.json:
        receipt_data = request.json
        # Logic to save the receipt data
        # For demonstration, let's just add to the receipts list
        print(receipt_data)
        return jsonify({"message": "Receipt saved"})
    else:
        return jsonify({"error": "No data received"}), 400

# API to edit receipt
@app.route('/receipt', methods=['PUT'])
def edit_receipt():
    if request.json:
        receipt_data = request.json
        # Logic to edit the receipt data
        # For demonstration, let's just return the edited data
        return jsonify({"message": "Receipt edited", "edited_receipt": receipt_data})
    else:
        return jsonify({"error": "No data received"}), 400

if __name__ == '__main__':
    app.run(debug=True)
    db.create_all()  # Create tables based on the models
