import pypdfium2 as pdfium

# Load a document
pdf = pdfium.PdfDocument("./data/ID.pdf")

# Loop over pages and render
for i in range(len(pdf)):
    page = pdf[i]
    image = page.render(scale=4).to_pil()
    image.save(f"./data/ID_{i}.jpg")