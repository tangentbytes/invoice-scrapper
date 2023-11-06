# getReceiptApi(emailOrPhone:String,date:String(iso-format))

Method: GET
API: /receipt/<userId>
Query Param: ?date=(ISOString)

# deleteReceipt(receiptNumber:Long)

Method: DELETE
API: /receipt/<receiptNumber>

# extractDataFromImage(image:File)

METHOD: POST
API: /extract
BODY(formData): {image: ....}

# saveReceipt(receiptData:ReceiptModel)

METHOD: POST
API: /receipt
BODY(json): receipt_data

# editReceipt(receiptDate:ReceiptModel)

METHOD: PUT
API: /receipt
BODY(json): receipt_data
