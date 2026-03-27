import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_ai_crawler():
    print("RSS Feed থেকে AI টুলস খোঁজা শুরু হচ্ছে...")
    
    # ২. বিকল্প সোর্স: RSS Feed (এটি ব্লক করা কঠিন)
    # আমরা একটি পাবলিক AI নিউজ বা টুলস ফিড ব্যবহার করছি
    rss_url = "https://www.futurepedia.io/rss.xml" 
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(rss_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, features="xml")

        # ৩. RSS আইটেমগুলো লুপ করা
        items = soup.find_all('item')
        found_count = 0

        for item in items:
            name = item.title.text if item.title else "Unknown AI"
            link = item.link.text if item.link else ""
            
            if link:
                data = {
                    "name": name,
                    "url": link,
                    "category": "Automated Update",
                    "trust_score": 8.0,
                    "safety_index": 8.0
                }
                
                try:
                    # 'url' ইউনিক থাকলে একই ডাটা বারবার ঢুকবে না
                    supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
                    print(f"সফলভাবে যুক্ত হয়েছে: {name}")
                    found_count += 1
                except Exception as db_e:
                    print(f"Database error for {name}: {db_e}")

        if found_count == 0:
            print("কোনো নতুন ডাটা পাওয়া যায়নি।")
        else:
            print(f"অভিনন্দন! মোট {found_count} টি নতুন টুল যুক্ত হয়েছে।")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    run_ai_crawler()
