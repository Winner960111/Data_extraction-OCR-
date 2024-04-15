import fitz  # Import the fitz library

# Open the provided PDF file
doc = fitz.open("./data/visa1.pdf")

# Iterate through each page in the document
for i in range(len(doc)):
    # Get the list of image references on the current page
    for img in doc.getPageImageList(i):
        xref = img[0]  # The xref number for the current image
        pix = fitz.Pixmap(doc, xref)  # Create a Pixmap object with the image data
        
        if pix.n < 5:  # Check if the image is GRAY or RGB
            # Save the image as a PNG file
            pix.writePNG(f"p{i}-{xref}.png")
        else:  # The image is CMYK; convert to RGB first
            pix1 = fitz.Pixmap(fitz.csRGB, pix)
            # Save the converted image as a PNG file
            pix1.writePNG(f"p{i}-{xref}.png")
            pix1 = None  # Free the Pixmap resources
            
        pix = None  # Free the Pixmap resources