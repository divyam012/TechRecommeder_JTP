import requests

def get_gsmarena_info(brand, model):
    try:
        # Remove anything in parentheses and extra spaces
        base_model = model.split('(')[0].strip()
        query = base_model  # Only use the cleaned model name
        print(f"Querying GSMArena for: {query}")
        resp = requests.get("http://localhost:3001/gsmarena", params={"q": query}, timeout=3)
        print("GSMArena status:", resp.status_code)
        if resp.ok:
            data = resp.json()
            print("GSMArena data:", data)
            if data and len(data) > 0:
                return {
                    "img": data[0].get("img"),
                    "description": data[0].get("description"),
                    "external_link": f"https://www.gsmarena.com/{data[0]['id']}.php"
                }
    except Exception as e:
        print("GSMArena API error:", e)
    return None