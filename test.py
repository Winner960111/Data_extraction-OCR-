import base64
import io
from PIL import Image

def create_image_from_base64(base64_string, output_file):
    # Decode base64 string into bytes
    image_data = base64.b64decode(base64_string)
    
    # Create image from bytes
    image = Image.open(io.BytesIO(image_data))
    
    # Save the image to a file
    image.save(output_file)

# Example base64 encoded string
base64_string = ""

# Output file path for the image
output_file = "ID.jpg"

# Call the function to create the image from base64 string
create_image_from_base64(base64_string, output_file)