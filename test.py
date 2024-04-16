import pytesseract
from PIL import Image

# Path to the scanned ID card PDF file
pdf_file_path = "visa1.pdf"

# Open the PDF file and convert the first page to an image
image = Image.open(pdf_file_path)

# Perform OCR on the image to extract text
extracted_text = pytesseract.image_to_string(image)

print(extracted_text)