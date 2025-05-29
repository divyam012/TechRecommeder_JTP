import requests

API_KEY = "8e80ec01-b88a-45a1-bad9-b3ed01826726"
API_ID = "6837328d42e183816e48b6b7"
BASE_URL = "https://api.techspecs.io/v5/product/search"

def search_phone(query):
    headers = {
        "accept": "application/json",
        "X-API-KEY": API_KEY,
        "X-API-ID": API_ID
    }
    params = {
        "query": query,
        "category": "smartphones"
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    print(response.status_code)
    print(response.json())

# Example usage:
search_phone("iPhone 15 Pro")