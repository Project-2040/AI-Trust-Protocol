import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random
import os

# আপনার সুপাবেস তথ্য
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def start_crawling():
    # সরাসরি একটি সহজ সোর্স ব্যবহার করছি যা ব্লক হয় না
    target_url = "https://www.futurepedia.io/rss.xml" 
    print("Fetching data from RSS...")
    
    try:
        response = requests.get(target_url, timeout=20)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=5)
        
        if not items:
            print("No items found in RSS.")
            return

        for item in items:
            name = item.title.text.strip()
            link = item.link.text.strip()
            
            # নাম অলরেডি আছে কি না চেক
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if len(check.data) == 0:
                data = {
                    "name": name,
                    "category": "AI Tool",
                    "trust_scor": round(random.uniform(7.5, 9.8), 1),
                    "safety_ind": random.randint(80, 99),
                    "url": link
                }
                # ডেটা ইনসার্ট
                supabase.table("ai_agents").insert(data).execute()
                print(f"Added Successfully: {name}")
            else:
                print(f"Skipped (Exists): {name}")

    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    start_crawling()
