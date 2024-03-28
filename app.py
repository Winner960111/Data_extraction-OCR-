import json
import requests
from dotenv import load_dotenv
import os
from openai import OpenAI
import json
load_dotenv()
client = OpenAI()

openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_client = OpenAI(api_key = openai_api_key)

file_name = ["t6.png", "t7.png", "t8.png"]

for index, item in enumerate(file_name):
    print(f"this is {item}")
    files = {"file": open(f"./data/{item}", 'rb')}
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
    print(f"this is extracted data from image===>{data}")
    with open(f"./data/extracted_data{index+1}.txt", 'w', encoding="utf-8") as file:
        # Write the text content to the file
        file.write(data)
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
                        "birthday": {
                            "type": "string",
                            "description": "extract the birthday or date of birth from given information",
                        },
                        "english_sex_letter":{
                            "type":"string",
                            "description":"extract the gender or sex from given information. You should answer with only 'M' or 'F'."
                        }
                    },
                    "required": ["english_name", "birthday", "english_gender_letter"]
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

    print(f"this is response====>{response.choices[0].message.tool_calls[0].function.arguments}")
    with open(f"./data/answer{index+1}.txt", 'w', encoding='utf-8') as file:
        file.write(
            response.choices[0].message.tool_calls[0].function.arguments)
