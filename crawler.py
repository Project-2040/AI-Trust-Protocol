import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ (GitHub Secrets থেকে আসবে)
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_ai_crawler():
    print("RSS Feed থেকে AI টুলস খোঁজা শুরু হচ্ছে...")
    
    # ২. সোর্স: Futurepedia RSS Feed (এটি সহজে ব্লক হয় না)
    rss_url = "https://www.futurepedia.io/rss.xml" 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(rss_url, headers=headers, timeout=15)
        # lxml ব্যবহার করে XML ডাটা পড়া হচ্ছে
        soup = BeautifulSoup(response.content, features="xml")

        # ৩. আইটেমগুলো লুপ করা
        items = soup.find_all('item')
        found_count = 0

        for item in items:
            name = item.title.text if item.title else "Unknown AI"
            link = item.link.text if item.link else ""
            
            if link:
                data = {
                    "name": name,
                    "url": link,
                    "category": "Latest AI",
                    "trust_score": 8.0,
                    "safety_index": 8.5
                }
                
                try:
                    # 'url' কলামটি ইউনিক থাকলে ডুপ্লিকেট হবে না
                    supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
                    print(f"সফলভাবে যুক্ত হয়েছে: {name}")
                    found_count += 1
                except Exception as db_e:
                    print(f"ডাটাবেস এরর ({name}): {db_e}")

        if found_count == 0:
            print("নতুন কোনো ডাটা পাওয়া যায়নি।")
        else:
            print(f"অভিনন্দন! মোট {found_count} টি নতুন টুল ডাটাবেসে যুক্ত হয়েছে।")

    except Exception as e:
        print(f"রান করার সময় ভুল হয়েছে: {e}")

if __name__ == "__main__":
    run_ai_crawler()
