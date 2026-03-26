import requests
import random
from supabase import create_client

# Supabase Setup
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def sync_data():
    print("--- 🚀 STARTING FORCE SYNC ---")
    try:
        # RSS সোর্স থেকে ডাটা আনা
        res = requests.get("https://www.futurepedia.io/rss.xml", timeout=10)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(res.content, 'xml')
        items = soup.find_all('item', limit=3)
        
        for item in items:
            name = item.title.text.strip()
            print(f"Found: {name}")
            payload = {
                "name": name,
                "category": "High Quality",
                "trust_scor": 9.2,
                "safety_ind": 95,
                "url": item.link.text.strip()
            }
            supabase.table("ai_agents").insert(payload).execute()
            print(f"✅ Saved: {name}")
            
    except Exception as e:
        print(f"❌ Error Detail: {str(e)}")

if __name__ == "__main__":
    sync_data()
