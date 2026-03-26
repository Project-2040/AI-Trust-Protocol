import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random

# সুপাবেস ক্রেডেনশিয়াল
url = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
key = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(url, key)

def start_crawling():
    # আমরা সরাসরি RSS Feed ব্যবহার করছি যা ব্লক করা যায় না
    feed_url = "https://www.futurepedia.io/rss.xml" 
    
    try:
        response = requests.get(feed_url, timeout=15)
        soup = BeautifulSoup(response.content, 'xml') # XML পার্সার
        
        # আইটেম খুঁজে বের করা
        items = soup.find_all('item', limit=5)
        
        added_count = 0
        for item in items:
            name = item.title.text.strip()
            link = item.link.text.strip()
            
            # ডাটাবেজে চেক করা
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if not check.data:
                data = {
                    "name": name,
                    "category": "AI Discovery",
                    "trust_scor": round(random.uniform(7.5, 9.7), 1), # আপনার কলামের নাম
                    "safety_ind": random.randint(85, 98),            # আপনার কলামের নাম
                    "url": link
                }
                supabase.table("ai_agents").insert(data).execute()
                print(f"AUTOMATED ADD: {name}")
                added_count += 1
        
        if added_count == 0:
            print("No new data found right now.")
            
    except Exception as e:
        print(f"Critical Error: {e}")

if __name__ == "__main__":
    start_crawling()
