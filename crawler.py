import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random
import sys

# সুপাবেস ক্রেডেনশিয়াল
url = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
key = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(url, key)

def start_crawling():
    # সরাসরি RSS Feed ব্যবহার (এটি ব্লক হওয়া কঠিন)
    feed_url = "https://www.futurepedia.io/rss.xml" 
    print(f"Connecting to: {feed_url}...")

    try:
        response = requests.get(feed_url, timeout=20)
        print(f"Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to fetch data from source.")
            return

        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item', limit=5)
        print(f"Found {len(items)} potential items.")

        added_count = 0
        for item in items:
            name = item.title.text.strip()
            link = item.link.text.strip()
            
            # ডাটাবেজে চেক করা
            print(f"Checking: {name}...")
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if not check.data:
                data = {
                    "name": name,
                    "category": "Automated",
                    "trust_scor": round(random.uniform(7.5, 9.8), 1),
                    "safety_ind": random.randint(80, 99),
                    "url": link
                }
                # ডাটাবেজে পুশ করা
                response_db = supabase.table("ai_agents").insert(data).execute()
                print(f"Inserted: {name}")
                added_count += 1
            else:
                print(f"Skipped (Already Exists): {name}")
        
        print(f"Total new items added: {added_count}")

    except Exception as e:
        print(f"Critical Error: {str(e)}")

if __name__ == "__main__":
    start_crawling()
