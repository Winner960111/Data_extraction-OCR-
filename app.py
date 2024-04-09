import json
import base64
import io
from PIL import Image
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI
from flask import Flask, request
import json
load_dotenv()
client = OpenAI()

app = Flask(__name__)
CORS(app, origins = '*')
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key = openai_api_key)

def create_image_from_base64(base64_string, output_file):

    # Decode base64 string into bytes
    image_data = base64.b64decode(base64_string)
    
    # Create image from bytes
    image = Image.open(io.BytesIO(image_data))
    
    # Save the image to a file
    image.save(output_file)

def create_pdf_from_base64(base64_string, output_file):
    # Decode the base64 string
    decoded_data = base64.b64decode(base64_string)
    
    # Write the decoded data to a PDF file
    with open(output_file, 'wb') as pdf_file:
        pdf_file.write(decoded_data)

def classify_base64_code(base64_code):
    # Decode the base64 string
    decoded_data = base64.b64decode(base64_code)
    
    # Check if it represents a PDF file
    if decoded_data[:4] == b'%PDF':
        return 'PDF'
    else: 
        return 'Image'

def extract_data_image(file_name, id):

        files = {"file": open(f"./data/{file_name}", 'rb')}
        url = "https://api.edenai.run/v2/ocr/ocr"
        data = {
            "providers": "google",
            "language": "en",
            "fallback_providers": ""
        }
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjM1MjUxOTQtMTUyMy00OTNhLTkxNzMtODNkYjcwOTc1NGM0IiwidHlwZSI6ImFwaV90b2tlbiJ9.plqIfgXVVxTvIuVrv-zGV1Vn-QCc7lbADOpFUeKPEao"}

        response = requests.post(url, data=data, files=files, headers=headers)

        result = json.loads(response.text)
        data = result["google"]["text"]

        if id == 'id':
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "english_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information.",
                                },
                                # "birthday": {
                                #     "type": "string",
                                #     "description": "extract the birthday or date of birth from given information",
                                # },
                                # "english_sex_letter":{
                                #     "type":"string",
                                #     "description":"extract the gender or sex from given information. You should answer with only 'M' or 'F'."
                                # }
                                "ID_number":{
                                    "type":"string",
                                    "description":"Extract the ID number from given information",
                                }
                            },
                            "required": ["english_name", "ID_number"]
                        },
                    }
                }
            ]
        else:
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "english_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information.",
                                },
                            },
                            "required": ["name"]
                        },
                    }
                }
            ]

        messages = [
            {"role": "system", "content": "Please extract the essential information from the data that is inputted by user. You should answer in all of question."},
            {"role": "user", "content": data}
            ]

        response = openai_client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=messages,
            temperature=0,
            tools=extract_info,
        )
        print(f"this is return value===>{response.choices[0].message.tool_calls[0].function.arguments}")
        return response.choices[0].message.tool_calls[0].function.arguments

@app.route('/sponsor', methods = ['GET', 'POST'])
def compare_id():
    try:
        full_name = request.json['full_name']
        eid_number = request.json['eid_number']
        eid_file_base64 = request.json['eid_file_base64']
        passport_id_base64 = request.json['passport_id_base64']

        print(f"this is data ===>{full_name}\n{eid_number}")

        # Output file path for the image
        eid_file = "./data/ID.jpg"
        passport_file = "./data/passport.jpg"

        # Call the function to create the image from base64 string
        if passport_id_base64 == '':

            print("this is passport out\n")
            create_image_from_base64(eid_file_base64, eid_file)
        
            id_data = extract_data_image("ID.jpg", 'id')
            id_data_json = json.loads(id_data)
            compare_full_name = id_data_json['english_name']
            compare_eid_number = id_data_json['ID_number']

            percent = 0
            if full_name == compare_full_name:
                percent += 1
            if eid_number == compare_eid_number:
                percent += 1

            percent = int(percent/2*100)

        else:
            
            print("this is passport in\n")
            
            create_image_from_base64(eid_file_base64, eid_file)
            id_data = extract_data_image("ID.jpg", 'id')
            id_data_json = json.loads(id_data)
            compare_full_name = id_data_json['english_name']
            compare_eid_number = id_data_json['ID_number']
            create_image_from_base64(passport_id_base64, passport_file)
            res_passport = extract_data_image("passport.jpg", 'pass')
            data_passport = json.loads(res_passport)
            compare_pass_name = data_passport["english_name"]
            percent = 0
            if full_name == compare_full_name:
                percent += 1
            if eid_number == compare_eid_number:
                percent += 1
            if full_name == compare_pass_name:
                percent += 1

            percent = int(percent/3*100)

        return str(percent)
    except Exception as e:
        print(e)
        return 'Failed'

@app.route('/member', methods = ['GET', 'POST'])
def compare_member_id():
    try:
        emirates_id = request.json['emirates_id']
        emirates_id_app_no = request.json['emirates_id_app_no']
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        member_uid = request.json['member_uid']
        member_type = request.json['member_type']
        date_of_birth = request.json['date_of_birth']
        gender = request.json['gender']
        nationality = request.json['nationality']
        marital_status = request.json['marital_status']
        passport_number = request.json['passport_number']
        upload_visa_copy_base64 = request.json['upload_visa_copy_base64']
        upload_passport_copy_base64 = request.json['upload_passport_copy_base64']
        upload_emirates_id_base64 = request.json['upload_emirates_id_base64']

        visa_img = "./data/visa.jpg"
        passport = "./data/passport.jpg"
        # Output file path for the PDF file
        visa_pdf = "./data/visa.pdf"
        if upload_visa_copy_base64:
            res = classify_base64_code(upload_visa_copy_base64)
            if res == 'PDF':
                print("this is PDF")
                create_pdf_from_base64(upload_visa_copy_base64, visa_pdf)
            else:
                print("this is image")
                create_image_from_base64(upload_visa_copy_base64, visa_img)         

        create_image_from_base64(upload_passport_copy_base64, passport)
        if upload_emirates_id_base64:
            eid_file = "./data/ID.jpg"
            create_image_from_base64(upload_emirates_id_base64, eid_file)
        return "OK"
    except Exception as e:
        print(e)
        return 'Failed'
    
if __name__ == '__main__':
    app.run(debug=True, port = 5050, host='0.0.0.0')