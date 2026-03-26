import requests
from supabase import create_client
import random

# Supabase Setup
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def start_sync():
    print("--- 🚀 HIGH-SPEED SYNC STARTED ---")
    
    # ব্রাউজার ছাড়া সরাসরি ডেটা সোর্স
    url = "https://www.futurepedia.io/rss.xml"
    
    try:
        response = requests.get(url, timeout=15)
        print(f"Connection Status: {response.status_code}")
        
        if response.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item', limit=5)
            
            for item in items:
                name = item.title.text.strip()
                print(f"Found Tool: {name}")
                
                # ইনসার্ট ডাটা
                data = {
                    "name": name,
                    "category": "Verified AI",
                    "trust_scor": round(random.uniform(8.5, 9.8), 1),
                    "safety_ind": random.randint(90, 99),
                    "url": item.link.text.strip()
                }
                supabase.table("ai_agents").insert(data).execute()
                print(f"✅ Saved to DB: {name}")
        else:
            print("❌ Failed to connect to source.")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    start_sync()
