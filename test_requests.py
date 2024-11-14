import requests
import json

url = "http://localhost:8000/api/auth/token"

payload = json.dumps({
  "username": "admin",
  "password": "admin"
})
headers = {
  'X-Auth-Header': 'd1df92d7-ca1b-4f56-8b08-a0c9a28af385',
  'Content-Type': 'application/json',
  'Cookie': 'csrftoken=z7lDuJygQKxXB9tC1T4TVOX2Nt1hJ8qJ'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
