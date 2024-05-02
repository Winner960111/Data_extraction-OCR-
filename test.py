import json
import requests

headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjM1MjUxOTQtMTUyMy00OTNhLTkxNzMtODNkYjcwOTc1NGM0IiwidHlwZSI6ImFwaV90b2tlbiJ9.plqIfgXVVxTvIuVrv-zGV1Vn-QCc7lbADOpFUeKPEao"}

url = "https://api.edenai.run/v2/ocr/ocr"
data = {
    "providers": "google",
    "language": "en",
    "fallback_providers": "amazon"
}
files = {"file": open("./data/visa.jpg", 'rb')}

response = requests.post(url, data=data, files=files, headers=headers)
result = json.loads(response.text)
print(result["google"]["text"])
