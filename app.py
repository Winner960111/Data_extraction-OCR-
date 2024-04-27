from langchain_community.document_loaders import PyPDFLoader
from datetime import datetime
import base64
import io
import PyPDF2
import pypdfium2 as pdfium
from flask_cors import CORS
from PIL import Image
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
    if image.mode in ('RGBA', 'LA'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        background.paste(image, mask=image.split()[3])  # 3 is the alpha channel
        image = background
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
    elif decoded_data.startswith(b'\xFF\xD8\xFF') or decoded_data.startswith(b'\x89PNG\r\n\x1a\n'):
        print("image\n")
        return 'Image'
    else:
        return 'other'

def extract_data_sponsor(file_name, id):
        if file_name == 'ID.pdf':
            files = {"file": open(f"./data/{file_name}", 'rb')}
            url = "https://api.edenai.run/v2/ocr/ocr"
            data = {
                "providers": "amazon",
                "language": "en",
                "fallback_providers": ""
            }
            headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjM1MjUxOTQtMTUyMy00OTNhLTkxNzMtODNkYjcwOTc1NGM0IiwidHlwZSI6ImFwaV90b2tlbiJ9.plqIfgXVVxTvIuVrv-zGV1Vn-QCc7lbADOpFUeKPEao"}

            response = requests.post(url, data=data, files=files, headers=headers)

            result = json.loads(response.text)
            data = result["amazon"]["text"]
            print(data)
        elif file_name == 'company.pdf':
            loader = PyPDFLoader(f"./data/{file_name}")
            data = loader.load()[0].page_content
        else:
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
            print(data)
        if id == 'id':
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "english_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information.",
                                },
                                "ID_number":{
                                    "type":"string",
                                    "description":"Extract the ID number from given information.",
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
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "company_name": {
                                    "type": "string",
                                    "description": "Extract the trade name from given information.",
                                },
                                "trading_license_number":{
                                    "type":"string",
                                    "description":"Extract the license number from given information.",
                                },
                                "expiry_date":{
                                    "type":"string",
                                    "description":"Extract the expiry date from given information.",
                                }
                            },
                            "required": ["company_name", "trading_license_number", "expiry_date"]
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
def extract_data_member(file_name, id):
        if file_name == 'visa.pdf' or file_name == 'passport.pdf' or file_name == 'ID.pdf':
            loader = PyPDFLoader(f"./data/{file_name}")
            data = loader.load()[0].page_content
            if data == '':
                files = {"file": open(f"./data/{file_name}", 'rb')}
                url = "https://api.edenai.run/v2/ocr/ocr"
                data = {
                    "providers": "amazon",
                    "language": "en",
                    "fallback_providers": ""
                }
                headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjM1MjUxOTQtMTUyMy00OTNhLTkxNzMtODNkYjcwOTc1NGM0IiwidHlwZSI6ImFwaV90b2tlbiJ9.plqIfgXVVxTvIuVrv-zGV1Vn-QCc7lbADOpFUeKPEao"}

                response = requests.post(url, data=data, files=files, headers=headers)

                result = json.loads(response.text)
                data = result["amazon"]["text"]
                # print(f"this is amazon data +++++>{data}")

        else:
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
            if file_name == 'visa.jpg':
                data = data.replace(" ","\n")
            print(f"this is data +++++>{data}")

        if id == 'visa':
            if 'U.I.D' not in data.replace("\n","").replace(" ",""):
                return 'no'
        elif id == 'id':
            if 'IDNumber' not in data.replace("\n","").replace(" ",""):
                return 'no'
        elif id == 'pass':
            if 'passport' in data.replace("\n","").replace(" ","").lower():
                if 'U.I.D' in data.replace("\n","").replace(" ",""):
                    return 'no'
            else:
                return 'no'
            
        if id == 'pass':
            print("I'm here")
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "surname": {
                                    "type": "string",
                                    "description": "Extract the surname from given information.",
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the birthday or date of birth from given information.",
                                },
                                "country_name":{
                                    "type":"string",
                                    "description":"extract the country name from given information."
                                },
                                "passport_number":{
                                    "type":"string",
                                    "description":"extract only current passport number from given information."
                                },
                                
                            },
                            "required": ["surname", "date_of_birth", "country_name", "passport_number"]
                        },
                    }
                }
            ]
        elif id == 'id':
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ID_number":{
                                    "type":"string",
                                    "description":"extract only current ID card number from given information."
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the birthday or date of birth from given information.",
                                },  
                                 "full_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information. You can reference that full name is comprised by only capital letters.",
                                },                             
                            },
                            "required": ["ID_number", "date_of_birth", "full_name"]
                        },
                    }
                }
            ]
        elif file_name == 'visa.pdf':
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the birthday or date of birth from given information. You should output only date information."
                                },
                                 "uid_number":{
                                    "type":"string",
                                    "description":"extract the U.I.D No from given information."
                                },
                                "full_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information.",
                                }, 
                            },
                            "required": ["date_of_birth", "uid_number", "full_name"]
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
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the date of birth from given information. You should output only date information."
                                },
                                "uid_number":{
                                    "type":"string",
                                    "description":"Extract the identity number from the given information. Refernece following format of identity number:'34523412'."
                                },
                                "full_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information. You can reference that full name is comprised by only capital letters.",
                                }, 
                            },
                            "required": ["date_of_birth", "uid_number", "full_name"]
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
        print(f"\nthis is return value===>{response.choices[0].message.tool_calls[0].function.arguments}")
        return response.choices[0].message.tool_calls[0].function.arguments

def re_extract(data, id):
    if id == 'visa':

        extract_info = [
                    {
                        "type": "function",
                        "function": {
                            "name": "extracte_info",
                            "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "date_of_birth": {
                                        "type": "string",
                                        "description": "extract the birthday or date of birth from given information. You should output only date information. Reference following date format:11/01/1999."
                                    },
                                    "uid_number":{
                                        "type":"string",
                                        "description":"Extract the identity number from the given text. Refernece following identity number format:'34523412'"
                                    },
                                    "full_name": {
                                        "type": "string",
                                        "description": "Extract the full name from given information. You can reference that full name is comprised by only capital letters.",
                                    }, 
                                },
                                "required": ["date_of_birth", "uid_number", "full_name"]
                            },
                        }
                    }
                ]
    elif id == 'id':
            extract_info = [
                {
                    "type": "function",
                    "function": {
                        "name": "extracte_info",
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "ID_number":{
                                    "type":"string",
                                    "description":"extract only current ID card number from given information."
                                },
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the birthday or date of birth from given information.",
                                },  
                                 "full_name": {
                                    "type": "string",
                                    "description": "Extract the full name from given information. You can reference that full name is comprised by only capital letters.",
                                },                             
                            },
                            "required": ["ID_number", "date_of_birth", "full_name"]
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
                        "description": "extract the essetial information from given text. You should extract only information that is written by english. If the same content is repeated, ignore that.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                               
                                "date_of_birth": {
                                    "type": "string",
                                    "description": "extract the birthday or date of birth from given information.",
                                },
                                "country_name":{
                                    "type":"string",
                                    "description":"extract the country name from given information."
                                },
                                "passport_number":{
                                    "type":"string",
                                    "description":"extract only current passport number from given information."
                                },
                                
                                
                            },
                            "required": ["date_of_birth", "country_name", "passport_number"]
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
    print(f"\nthis is reextract value===>{response.choices[0].message.tool_calls[0].function.arguments}")
    return response.choices[0].message.tool_calls[0].function.arguments

def page_number(file_name):

    # Use a context manager to ensure the file is properly closed after its block finishes execution
    with open(file_name, 'rb') as file:
        # Create a PdfReader object from the file data
        pdfReader = PyPDF2.PdfReader(file)
        
        # Get the total number of pages in the PDF by taking the length of the pages list
        totalPages = len(pdfReader.pages)
    print(f"this is totalpage====>{totalPages}")
    return totalPages

def split_pdf(file_path):

    with open(file_path, 'rb') as file:
        pdf = PyPDF2.PdfReader(file)

        pdf_writer = PyPDF2.PdfWriter()

        pdf_writer.add_page(pdf.pages[0])

        with open("./data/company.pdf", 'wb') as new_file:
            pdf_writer.write(new_file)

def generate_image(file_name):
    pdf = pdfium.PdfDocument(file_name)

    # Loop over pages and render
    for i in range(len(pdf)):
        page = pdf[i]
        image = page.render(scale=4).to_pil()
        image.save(f"./data/ID_{i}.jpg")

@app.route('/sponsor', methods = ['GET', 'POST'])
def compare_id():
    try:
        full_name = request.json['full_name']
        eid_number = request.json['eid_number']
        eid_file_base64 = request.json['eid_file_base64']
        company_name = request.json['company_name']
        trading_license_number = request.json['trading_license_number']
        company_trading_copy_base64 = request.json['company_trading_copy_base64']
        print(f"\nthis is data ===>{full_name}\n{eid_number}\n{company_name}\n{trading_license_number}")

        if company_trading_copy_base64:
            company_file = "./data/company.jpg"
            company_pdf = "./data/company.pdf"
            res = classify_base64_code(company_trading_copy_base64)

            if res == 'PDF':
                print("this is company PDF")
                create_pdf_from_base64(company_trading_copy_base64, company_pdf)
                split_pdf(company_pdf)
                company_data = extract_data_sponsor("company.pdf", 'company')

            elif res == 'Image':
                print("this is company image")
                create_image_from_base64(company_trading_copy_base64, company_file)
                company_data = extract_data_sponsor("company.jpg", 'company')
            else:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"The file has not been processed - wrong type ( .jpg, .png, .pdf)"
                    }
                return json_data
            
            company_data_json = json.loads(company_data)
            compare_company_name = company_data_json['company_name']
            compare_trading_number = company_data_json['trading_license_number']
            percent = 0
            error = ""
            if company_name.replace(" ", "").lower() in compare_company_name.replace(" ","").lower():
                percent += 1
            else:
                error = "company name"
            if compare_trading_number == trading_license_number:
                percent += 1
            else:
                error = "trading license number"

            date_formats = [
                    '%d %b %Y',  # e.g., "25 Dec 2020"
                    '%d %b %y',  # e.g., "25 Dec 20"
                    '%d %m %Y',  # e.g., "25 12 2020"
                    '%d/%m/%Y',   # e.g., "25/12/2020"
                    '%d-%m-%Y',
                    '%d/%m/%y',
                    '%Y/%m/%d'
                ]

            birthday_date = None

            # Try each date format until successful
            for date_format in date_formats:
                try:
                    birthday_date = datetime.strptime(company_data_json['expiry_date'], date_format)
                    break  # Date parsed successfully; exit the loop
                except ValueError:
                    continue
            formatted_birthday = str(birthday_date.strftime('%Y-%m-%d'))
            current_date = str(datetime.now().date())
            print(f"this is date===>{formatted_birthday}\n{current_date}")

            if formatted_birthday > current_date:
                percent += 1
            else:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"Trading license expired!"
                    }
                return json_data

            percent = int(percent/3*100)
            if percent == 100:
                json_data = {
                    "score":percent,
                    "status":'processed',
                    "error_msg":"The information are correct."
                }
            else:
                json_data = {
                    "score":percent,
                    "status":'processed',
                    "error_msg":f"The inserted information is NOT MATCHING. Specifically, : {error}"
                }
            print(f"percent===>{json_data}")
            return json_data

        else:
            # Output file path for the image
            eid_file = "./data/ID.jpg"
            eid_pdf = "./data/ID.pdf"
            res = classify_base64_code(eid_file_base64)
            
            if res == 'PDF':
                print("this is ID PDF")
                create_pdf_from_base64(eid_file_base64, eid_pdf)
                page_res = page_number('./data/ID.pdf')
                if page_res > 2:
                    json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"Wrong file selected, please select another one"
                    }
                    return json_data
                if page_res == 2:
                    generate_image(eid_pdf)
                    id_data = extract_data_sponsor("ID_0.jpg","id")
                else:
                    id_data = extract_data_sponsor("ID.pdf", 'id')

            elif res == 'Image':
                print("this is ID image")
                create_image_from_base64(eid_file_base64, eid_file)
                id_data = extract_data_sponsor("ID.jpg", 'id')
            else:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"The file has not been processed - wrong type ( .jpg, .png, .pdf)"
                    }
                return json_data

            id_data_json = json.loads(id_data)
            compare_full_name = id_data_json['english_name']

            compare_eid_number = id_data_json['ID_number']

            percent = 0
            error = ""
            if compare_full_name.replace(" ","").lower() in full_name.replace(" ", "").lower():
                percent += 1
            else:
                error = "full name"
            if eid_number == compare_eid_number:
                percent += 1
            else:
                error = "eid number"

            percent = int(percent/2*100)
            if percent == 100:
                json_data = {
                    "score":percent,
                    "status":'processed',
                    "error_msg":"The information are correct."
                }
            else:
                json_data = {
                    "score":percent,
                    "status":'processed',
                    "error_msg":f"The inserted information is NOT MATCHING. Specifically, : {error}"
                }
            print(f"percent===>{json_data}")
            return json_data
    except Exception as e:
        print(e)
        return 'Failed'

@app.route('/member', methods = ['GET', 'POST'])
def compare_member_id():
    try:
        input_data = {"emirates_id":"","member_uid":"", "last_name":"", "date_of_birth":"", "nationality":"", "passport_number":""}
        visa_data_obj = {"emirates_id":"", "member_uid":"","last_name":"", "date_of_birth":"", "nationality":"", "passport_number":""}
        id_data_obj = {"emirates_id":"", "member_uid":"","last_name":"", "date_of_birth":"", "nationality":"", "passport_number":""}
        passport_data_obj = {"emirates_id":"", "member_uid":"", "last_name":"", "date_of_birth":"", "nationality":"", "passport_number":""}
        upload_visa_copy_base64 = request.json['upload_visa_id_base64']
        upload_passport_copy_base64 = request.json['upload_passport_copy_base64']
        upload_emirates_id_base64 = request.json['upload_emirates_id_base64']
        input_data["emirates_id"] = request.json['emirates_id']
        input_data["member_uid"] = request.json['member_uid']
        input_data["last_name"] = request.json['last_name']
        input_data["date_of_birth"] = request.json['date_of_birth']
        input_data["nationality"] = request.json['nationality']
        input_data["passport_number"] = request.json['passport_number']
        if not upload_emirates_id_base64 and not upload_visa_copy_base64:
            json_data = {
                        "score":0,
                        "status":'not processed',
                        "error_msg":"Neither EID nor Visa file are inserted"
                        }
            return json_data
        print(f"\nthis is input info ====>{input_data}")
        visa_img = "./data/visa.jpg"
        passport = "./data/passport.jpg"
        passport_pdf = "./data/passport.pdf"
        # Output file path for the PDF file
        visa_pdf = "./data/visa.pdf"
        eid_file = "./data/ID.jpg"
        eid_pdf = "./data/ID.pdf"

        if upload_visa_copy_base64:
            res = classify_base64_code(upload_visa_copy_base64)
            if res == 'PDF':
                print("this is PDF")
                create_pdf_from_base64(upload_visa_copy_base64, visa_pdf)

                page_res = page_number(visa_pdf)
                if page_res > 1:
                    json_data = {
                        "score":0,
                        "status":'not processed',
                        "error_msg":"Wrong file selected, please select another one"
                        }
                    return json_data
                while True:
                    try:
                        extract_info = extract_data_member("visa.pdf","visa")
                        if extract_info == 'no':
                            json_data = {
                                "score":0,
                                "status":'not processed',
                                "error_msg":"Visa file is not correct"
                                }
                            return json_data
                        temp = json.loads(extract_info)

                        new_data = temp['date_of_birth'].replace(" ", "\n") + '\n' + temp["full_name"].replace(" ", "\n") + '\n' + temp['uid_number'].replace(" ","\n")
                        break
                    except:
                        print("re-attempt")
                while True:
                    try:
                        visa_data = json.loads(re_extract(new_data, 'visa'))
                        date_formats = [
                            '%d %b %Y',  # e.g., "25 Dec 2020"
                            '%d %b %y',  # e.g., "25 Dec 20"
                            '%d %m %Y',  # e.g., "25 12 2020"
                            '%d/%m/%Y',   # e.g., "25/12/2020"
                            '%d-%m-%Y',
                            '%d/%m/%y',
                            '%Y/%m/%d'
                        ]

                        birthday_date = None

                        # Try each date format until successful
                        for date_format in date_formats:
                            try:
                                birthday_date = datetime.strptime(visa_data['date_of_birth'], date_format)
                                break  # Date parsed successfully; exit the loop
                            except ValueError:
                                continue
                        formatted_birthday = birthday_date.strftime('%Y-%m-%d')
                        visa_data_obj["date_of_birth"] = str(formatted_birthday)
                        visa_data_obj["member_uid"] = visa_data['uid_number']
                        visa_data_obj["last_name"] = visa_data['full_name']
                        break
                    except:
                        print("re-attempt")

                print(f"\nthis is visa object===>{visa_data_obj}") 

            elif res == 'Image':
                print("this is image")
                create_image_from_base64(upload_visa_copy_base64, visa_img) 

                while True:
                    try:
                       extract_info = extract_data_member("visa.jpg","visa") 
                       if extract_info == 'no':
                           json_data = {
                                "score":0,
                                "status":'not processed',
                                "error_msg":"Visa file is not correct"
                                }
                           return json_data
                       temp = json.loads(extract_info)

                       new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp["full_name"].replace(" ", "\n") + ', ' + temp['uid_number'].replace(" ","\n")
                       break
                    except:
                        print("re-attempt")
                while True:
                    try:

                        visa_data = json.loads(re_extract(new_data, 'visa'))
                        date_formats = [
                            '%d %b %Y',  # e.g., "25 Dec 2020"
                            '%d %b %y',  # e.g., "25 Dec 20"
                            '%d %m %Y',  # e.g., "25 12 2020"
                            '%d/%m/%Y',   # e.g., "25/12/2020"
                            '%d-%m-%Y',
                            '%d/%m/%y',
                            '%Y/%m/%d'
                        ]

                        birthday_date = None

                        # Try each date format until successful
                        for date_format in date_formats:
                            try:
                                birthday_date = datetime.strptime(visa_data['date_of_birth'], date_format)
                                break  # Date parsed successfully; exit the loop
                            except ValueError:
                                continue   
                        formatted_birthday = birthday_date.strftime('%Y-%m-%d')
                        visa_data_obj["date_of_birth"] = str(formatted_birthday)
                        visa_data_obj["member_uid"] = visa_data['uid_number']
                        visa_data_obj["last_name"] = visa_data['full_name']
                        break
                    except:
                        print("re-attempt")
                print(f"\nthis is visa object===>{visa_data_obj}")  
            else:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"The file has not been processed - wrong type ( .jpg, .png, .pdf)"
                    }
                return json_data
            
        if upload_emirates_id_base64:
            res = classify_base64_code(upload_emirates_id_base64)

            if res == 'PDF':
                print("this is ID PDF")
                create_pdf_from_base64(upload_emirates_id_base64, eid_pdf)

                page_res = page_number(eid_pdf)
                if page_res > 2:
                    json_data = {
                        "score":0,
                        "status":'not processed',
                        "error_msg":"Wrong file selected, please select another one"
                        }
                    return json_data
                if page_res == 2:
                    generate_image(eid_pdf)
                    while True:
                        try:
                            extract_info = extract_data_member("ID_0.jpg","id")
                            if extract_info == 'no':
                                json_data = {
                                    "score":0,
                                    "status":'not processed',
                                    "error_msg":"ID file is not correct"
                                    }
                                return json_data
                            temp = json.loads(extract_info)
                            new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp["full_name"].replace(" ", "\n") + ', ' + temp['ID_number'].replace(" ","\n")
                            break
                        except:
                            print("re-attempt")
                else:
                    while True:
                        try:
                            extract_info = extract_data_member("ID.pdf","id")
                            if extract_info == 'no':
                                json_data = {
                                    "score":0,
                                    "status":'not processed',
                                    "error_msg":"ID file is not correct"
                                    }
                                return json_data
                            temp = json.loads(extract_info)
                            new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp["full_name"].replace(" ", "\n") + ', ' + temp['ID_number'].replace(" ","\n")
                            break
                        except:
                            print("re-attempt")

            elif res == 'Image':
                print("this is ID image")
                create_image_from_base64(upload_emirates_id_base64, eid_file)
                while True:
                        try:
                            extract_info = extract_data_member("ID.jpg","id")
                            if extract_info == 'no':
                                    json_data = {
                                        "score":0,
                                        "status":'not processed',
                                        "error_msg":"ID file is not correct"
                                        }
                                    return json_data
                            temp = json.loads(extract_info)
                            new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp["full_name"].replace(" ", "\n") + ', ' + temp['ID_number'].replace(" ","\n")
                            break
                        except:
                            print("re-attempt")
            else:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"The file has not been processed - wrong type ( .jpg, .png, .pdf)"
                    }
                return json_data
            while True:
                try:

                    id_data = json.loads(re_extract(new_data, 'id'))
                    date_formats = [
                        '%d %b %Y',  # e.g., "25 Dec 2020"
                        '%d %b %y',  # e.g., "25 Dec 20"
                        '%d %m %Y',  # e.g., "25 12 2020"
                        '%d/%m/%Y',   # e.g., "25/12/2020"
                        '%d-%m-%Y',
                        '%d/%m/%y',
                        '%Y/%m/%d'
                    ]

                    birthday_date = None

                    # Try each date format until successful
                    for date_format in date_formats:
                        try:
                            birthday_date = datetime.strptime(id_data['date_of_birth'], date_format)
                            break  # Date parsed successfully; exit the loop
                        except ValueError:
                            continue   
                    formatted_birthday = birthday_date.strftime('%Y-%m-%d')
                    id_data_obj["emirates_id"] = id_data['ID_number']
                    id_data_obj["last_name"] = id_data['full_name'].replace('\n', ' ')
                    id_data_obj["date_of_birth"] = str(formatted_birthday)
                    break
                except:
                    print("re-attempt")

            print(f"\nthis is id object===>{id_data_obj}")
            
        res = classify_base64_code(upload_passport_copy_base64)

        if res == 'PDF':
            print("this is passport PDF")
            create_pdf_from_base64(upload_passport_copy_base64, passport_pdf)

            page_res = page_number(passport_pdf)
            if page_res > 1:
                json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"Wrong file selected, please select another one"
                    }
                return json_data
            while True:
                try:
                    extract_info = extract_data_member("passport.pdf","pass")
                    if extract_info == 'no':
                        json_data = {
                            "score":0,
                            "status":'not processed',
                            "error_msg":"Passport file is not correct"
                            }
                        return json_data
                    temp = json.loads(extract_info)
                    new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp['country_name'].replace(" ", "\n") + ', ' + temp['passport_number']
                    break
                except:
                    print("re-attempt")
            
        elif res == 'Image':
            print("this is passport image")
            create_image_from_base64(upload_passport_copy_base64, passport)
            while True:
                try:
                    extract_info = extract_data_member("passport.jpg","pass")
                    if extract_info == 'no':
                        json_data = {
                            "score":0,
                            "status":'not processed',
                            "error_msg":"Passport file is not correct"
                            }
                        return json_data
                    temp = json.loads(extract_info)
                    new_data = temp['date_of_birth'].replace(" ", "\n") + ', ' + temp['country_name'].replace(" ", "\n") + ', ' + temp['passport_number']
                    break
                except:
                    print("re-attempt")
        else:
            json_data = {
                    "score":0,
                    "status":'not processed',
                    "error_msg":"The file has not been processed - wrong type ( .jpg, .png, .pdf)"
                    }
            return json_data
        while True:
            try:

                passport_data = json.loads(re_extract(new_data, 'pass'))

                date_formats = [
                    '%d %b %Y',  # e.g., "25 Dec 2020"
                    '%d %b %y',  # e.g., "25 Dec 20"
                    '%d %m %Y',  # e.g., "25 12 2020"
                    '%d/%m/%Y',   # e.g., "25/12/2020"
                    '%d-%m-%Y',
                    '%d/%m/%y',
                    '%Y/%m/%d'
                ]

                birthday_date = None

                # Try each date format until successful
                for date_format in date_formats:
                    try:
                        birthday_date = datetime.strptime(passport_data['date_of_birth'], date_format)
                        break  # Date parsed successfully; exit the loop
                    except ValueError:
                        # This except block catches the ValueError if parsing fails,
                        # and continues to the next iteration.
                        continue                

                formatted_birthday = birthday_date.strftime('%Y-%m-%d')
                passport_data_obj["last_name"] =temp['surname']
                passport_data_obj["date_of_birth"] = str(formatted_birthday)
                passport_data_obj["nationality"] = passport_data['country_name']
                passport_data_obj["passport_number"] = passport_data['passport_number'].replace(" ","")
                break
            except:
                print("re-attempt")

        print(f"\nthis is passport object===>{passport_data_obj}")

        array = ['emirates_id','member_uid','last_name','nationality', 'date_of_birth', 'passport_number']
        success = 0
        error = ''
        for item in array:
            if visa_data_obj[item] == '' and passport_data_obj[item] == '' and id_data_obj[item]:
                success += 1
                continue
            count = 0
            if visa_data_obj[item]:
                if item == 'last_name' or item == 'nationality':
                    if input_data[item].replace(" ", "").lower() in visa_data_obj[item].replace(" ", "").lower():
                        count += 1
                    else:
                        error = item.replace("_", " ")
                else:
                    if input_data[item] == visa_data_obj[item]:
                        count += 1
                    else:
                        error = item.replace("_", " ")

            else:
                count += 1
                
            if id_data_obj[item]:
                if item == 'last_name' or item == 'nationality':
                    if input_data[item].replace(" ", "").lower() in id_data_obj[item].replace(" ", "").lower():
                        count += 1
                    else:
                        error = item.replace("_", " ")
                else:
                    if input_data[item] == id_data_obj[item]:
                        count += 1
                    else:
                        error = item.replace("_", " ")
            else:
                count += 1

            if passport_data_obj[item]:
                if item == 'passport_number' or item == 'last_name' or item == 'nationality':
                    if input_data[item].replace(" ", "").lower() in passport_data_obj[item].replace(" ", "").lower():
                        count +=1
                    else:
                        error = item.replace("_", " ")
                else:
                    if input_data[item] == passport_data_obj[item]:
                        count += 1
                    else:
                        error = item.replace("_", " ")
            else:
                count += 1
            if count == 3:
                success += 1

        print(f"this is success ==>{success}")
        percent = int(success/6*100)
        
        if percent == 100:
            json_data = {
                "score":percent,
                "status":'processed',
                "error_msg":"The information are correct."
            }
        else:
            json_data = {
                "score":percent,
                "status":'processed',
                "error_msg":f"The inserted information is NOT MATCHING. Specifically, {error}"
            }
        print(f"this is percent===>{json_data}")
        return json_data
    except Exception as e:
        json_data = {
                "score":0,
                "status":'error',
                "error_msg":'Failed'
            }
        print(e)
        return json_data
    
if __name__ == '__main__':
    app.run(debug=True, port = 5050, host='0.0.0.0')