import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from supabase import create_client, Client

PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print(f"[{datetime.now().isoformat()}] 🤖 AI Trust Protocol Scraper Starting...")

try:
    supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)
    print("✓ Supabase connected successfully!")
except Exception as e:
    print(f"✗ Supabase connection failed: {e}")
    exit(1)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def save_to_db(name, url, source, description=""):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "category": "AI Agent",
            "description": description.strip()[:500],
            "trust_score": 7.5,
            "security_score": 8.0,
            "performance_score": 8.0,
            "privacy_score": 7.5,
            "source": source,
            "is_verified": False
        }
        # ডাটাবেজে পাঠানোর আগে প্রিন্ট করে দেখা
        print(f"  Attempting to save: {name}")
        result = supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        return True
    except Exception as e:
        print(f"  ✗ Save Error: {e}")
        return False

def scrape_futurepedia():
    print("\n📍 Scraping Futurepedia...")
    try:
        response = requests.get('https://www.futurepedia.io/rss.xml', headers=HEADERS, timeout=15)
        print(f"  Response Code: {response.status_code}") # ওয়েবসাইট থেকে রেসপন্স আসছে কি না
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        print(f"  Found {len(items)} items in RSS feed") # কয়টি আইটেম পাওয়া গেল
        
        count = 0
        for item in items[:10]:
            title = item.find('title')
            link = item.find('link')
            if title and link:
                if save_to_db(title.text, link.text, "Futurepedia"):
                    count += 1
        return count
    except Exception as e:
        print(f"  ✗ Futurepedia error: {e}")
        return 0

def main():
    total = 0
    total += scrape_futurepedia()
    print(f"\n✅ COMPLETED! Total items added/updated: {total}")

if __name__ == "__main__":
    main()
