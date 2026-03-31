import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client
from datetime import datetime

PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)

# ব্লকিং এড়াতে উন্নত হেডার
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/rss+xml, application/xml, text/xml, */*'
}

def save_to_db(name, url, source):
    try:
        data = {
            "name": name[:200],
            "url": url,
            "source": source,
            "category": "AI Tool",
            "trust_score": 7.5,
            "is_verified": False
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        return True
    except Exception as e:
        print(f"  ✗ Save Error: {e}")
        return False

def scrape_rss(url, source_name):
    print(f"\n📍 Scraping {source_name}...")
    try:
        # ভেরিফিকেশন এড়াতে এবং ব্লকিং কমাতে সেশন ব্যবহার
        session = requests.Session()
        response = session.get(url, headers=HEADERS, timeout=20)
        
        if response.status_code != 200:
            print(f"  ✗ Failed: Status Code {response.status_code}")
            return 0
            
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        print(f"  ✓ Found {len(items)} items")
        
        count = 0
        for item in items[:15]:
            title = item.find('title').text if item.find('title') else ""
            link = item.find('link').text if item.find('link') else ""
            if title and link:
                if save_to_db(title, link, source_name):
                    count += 1
        return count
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return 0

def main():
    print(f"🚀 Started at: {datetime.now()}")
    
    # Futurepedia ব্লক করলে আমরা Thermostat বা অন্য RSS ব্যবহার করতে পারি
    # আপাতত Futurepedia এর বিকল্প একটি ফিড ট্রাই করছি
    total = 0
    total += scrape_rss('https://www.futuretools.io/feed.xml', 'FutureTools')
    
    print(f"\n✅ COMPLETED! Total items added/updated: {total}")

if __name__ == "__main__":
    main()
