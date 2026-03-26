import requests
from supabase import create_client
import random
import os
from bs4 import BeautifulSoup

URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase = create_client(URL, KEY)

def mission_start():
    print("--- 🚀 MISSION 2040: STARTING ---")
    try:
        response = requests.get("https://www.futurepedia.io/rss.xml", timeout=20)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=5)

        if not items:
            print("❌ No data found in RSS!")
            return

        for item in items:
            name = item.title.text.strip()
            print(f"Syncing: {name}")

            # Link সঠিকভাবে নেওয়া
            link_tag = item.find('link')
            url = link_tag.next_sibling.strip() if link_tag else ""

            data = {
                "name": name,
                "category": "AI Protocol",
                "trust_score": round(random.uniform(8.5, 9.8), 1),  # ✅ ঠিক নাম
                "safety_index": random.randint(90, 99),              # ✅ ঠিক নাম
                "url": url
            }

            supabase.table("ai_agents").insert(data).execute()
            print(f"✅ Success: {name}")

    except Exception as e:
        print(f"❌ Error Detail: {str(e)}")

if __name__ == "__main__":
    mission_start()
