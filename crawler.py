import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random

# আপনার সুপাবেস তথ্য
url = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
key = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(url, key)

def start_crawling():
    # RSS Feed ব্যবহার করছি
    feed_url = "https://www.futurepedia.io/rss.xml" 
    
    try:
        response = requests.get(feed_url, timeout=15)
        soup = BeautifulSoup(response.content, 'xml') 
        items = soup.find_all('item', limit=5)
        
        for item in items:
            name = item.title.text.strip()
            link = item.link.text.strip()
            
            # ডাটাবেজে আগে থেকে আছে কি না চেক করা
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if not check.data:
                data = {
                    "name": name,
                    "category": "AI Tool",
                    "trust_scor": round(random.uniform(7.5, 9.8), 1), # বানান ঠিক আছে
                    "safety_ind": random.randint(85, 99),            # বানান ঠিক আছে
                    "url": link
                }
                supabase.table("ai_agents").insert(data).execute()
                print(f"Added: {name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_crawling()
