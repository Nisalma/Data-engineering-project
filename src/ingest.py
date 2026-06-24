import os
import requests

# We are choosing Tokyo as a clean, major market example
CITY_PATH = "japan/kanto/tokyo/2024-12-28" 
BASE_URL = f"https://data.insideairbnb.com/{CITY_PATH}/data/"

FILES = ["listings.csv.gz", "calendar.csv.gz", "reviews.csv.gz", "neighbourhoods.csv"]
DATA_DIR = "./data"

os.makedirs(DATA_DIR, exist_ok=True)

for file in FILES:
    print(f"🤖 Fetching: {file}...")
    response = requests.get(f"{BASE_URL}{file}", stream=True)
    if response.status_code == 200:
        with open(os.path.join(DATA_DIR, file), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Saved {file} successfully!")
    else:
        print(f"❌ Could not download {file}.")