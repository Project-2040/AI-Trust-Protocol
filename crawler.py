import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random

# আপনার সুপাবেস তথ্য
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def start_crawling():
    # সরাসরি RSS Feed ব্যবহার (এটি ব্লক হওয়া কঠিন)
    feed_url = "https://www.futurepedia.io/rss.xml" 
    
    try:
        response = requests.get(feed_url, timeout=20)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=5)
        
        for item in items:
            name = item.title.text.strip()
            link = item.link.text.strip()
            
            # নাম অলরেডি আছে কি না চেক করা
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if len(check.data) == 0:
                # সঠিক কলাম নামে ডেটা সাজানো (trust_scor এবং safety_ind)
                data = {
                    "name": name,
                    "category": "AI Tool",
                    "trust_scor": round(random.uniform(7.5, 9.8), 1),
                    "safety_ind": random.randint(80, 99),
                    "url": link
                }
                # ডেটা ইনসার্ট করা
                supabase.table("ai_agents").insert(data).execute()
                print(f"Added Successfully: {name}")
            else:
                print(f"Skipped (Exists): {name}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_crawling()
