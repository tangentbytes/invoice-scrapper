import pytesseract
from PIL import Image
import re
import spacy

nlp = spacy.load("en_core_web_sm")
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

# Open an image
image = Image.open('img.jpeg')

# Use Pytesseract to extract text
ocr_text = pytesseract.image_to_string(image)

# Print the extracted text
print(ocr_text)


def extract_invoice_info(ocr_text, patterns):
    extracted_info = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, ocr_text)
        if match:
            extracted_info[key] = match.group(1)

    return extracted_info


# Define regex patterns for different types of information
patterns = {
    "Invoice Number": r"Loren (\d+)",
    "Amount": r"SALE AMOUNT GBP (\d+\.\d{2})",
    "Auth Code": r"Auth Code : (\d+)",
    "Date": r"(\d{2}-\d{2}-\d{4} \d{2}:\d{2}:\d{2})",
    # Add more patterns for other information as needed
}

doc = nlp(ocr_text)
for ent in doc.ents:
    print(f"Entity: {ent.text}, Label: {ent.label_}")

# extracted_info = extract_invoice_info(ocr_text, patterns)

# # Print the extracted information
# for key, value in extracted_info.items():
#     print(f"{key}: {value}")
