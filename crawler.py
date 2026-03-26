import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random

# আপনার সুপাবেস তথ্য
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

def start_crawling():
    # সরাসরি RSS Feed ব্যবহার (এটি ব্লক করা কঠিন)
    feed_url = "https://www.futurepedia.io/rss.xml" 
    print("Connecting to RSS...")
    
    try:
        response = requests.get(feed_url, timeout=20)
        # 'html.parser' ব্যবহার করছি যাতে lxml এর ঝামেলা না থাকে
        soup = BeautifulSoup(response.content, 'html.parser') 
        items = soup.find_all('item')
        
        print(f"Found {len(items)} items.")
        added = 0

        for item in items[:5]: # প্রথম ৫টি এআই টুল
            name = item.title.text.strip()
            # ডাটাবেজে আগে থেকে আছে কি না চেক
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if not check.data:
                data = {
                    "name": name,
                    "category": "AI Tool",
                    "trust_scor": round(random.uniform(7.0, 9.5), 1),
                    "safety_ind": random.randint(80, 99),
                    "url": "https://www.futurepedia.io"
                }
                supabase.table("ai_agents").insert(data).execute()
                print(f"Done: {name}")
                added += 1
        
        print(f"Total Added: {added}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_crawling()
