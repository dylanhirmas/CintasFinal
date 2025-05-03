import os
import requests

API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

if not API_FOOTBALL_KEY:
    print("API key is missing. Set API_FOOTBALL_KEY in your .env file.")
    exit()

url = "https://v3.football.api-sports.io/teams"
headers = {"x-apisports-key": API_FOOTBALL_KEY}
params = {"search": "Arsenal"}

response = requests.get(url, headers=headers, params=params)

print("Status code:", response.status_code)
print("Response:")
print(response.json())