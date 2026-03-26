import requests
from supabase import create_client
import random
from bs4 import BeautifulSoup

# Supabase Credentials
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def mission_start():
    print("--- 🚀 MISSION 2040: STARTING ---")
    try:
        # সরাসরি RSS সোর্স (জাভাস্ক্রিপ্ট ঝামেলা নেই)
        response = requests.get("https://www.futurepedia.io/rss.xml", timeout=20)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=5) # প্রথম ৫টি নিয়ে টেস্ট
        
        if not items:
            print("❌ No data found in RSS!")
            return

        for item in items:
            name = item.title.text.strip()
            print(f"Syncing: {name}")
            
            data = {
                "name": name,
                "category": "AI Protocol",
                "trust_scor": round(random.uniform(8.5, 9.8), 1),
                "safety_ind": random.randint(90, 99),
                "url": item.link.text.strip()
            }
            # ডাটাবেজে পাঠানো
            supabase.table("ai_agents").insert(data).execute()
            print(f"✅ Success: {name}")

    except Exception as e:
        print(f"❌ Error Detail: {str(e)}")

if __name__ == "__main__":
    mission_start()
