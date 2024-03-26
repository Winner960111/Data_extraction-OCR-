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

headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjM1MjUxOTQtMTUyMy00OTNhLTkxNzMtODNkYjcwOTc1NGM0IiwidHlwZSI6ImFwaV90b2tlbiJ9.plqIfgXVVxTvIuVrv-zGV1Vn-QCc7lbADOpFUeKPEao"}

url = "https://api.edenai.run/v2/ocr/ocr"
data = {
    "providers": "google",
    "language": "en",
    "fallback_providers": ""
}
files = {"file": open("./112.jpg", 'rb')}

response = requests.post(url, data=data, files=files, headers=headers)

result = json.loads(response.text)
data = result["google"]["text"]
print(f"this is extracted data from image===>{data}")
extract_info = [
    {
        "type": "function",
        "function": {
            "name": "extracte_info",
            "description": "extract the essetial information from given text",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "extract the name from given information.",
                    },
                    "birthday": {
                        "type": "string",
                        "description": "extract the birthday or date of birth from given information",
                    },
                    "gender":{
                        "type":"string",
                        "description":"extract the gender from given information"
                    }
                },
                "required": ["name", "birthday", "gender"]
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
