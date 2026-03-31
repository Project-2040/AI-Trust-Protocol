#!/usr/bin/env python3
import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from supabase import create_client, Client

# --- SETUP ---
# GitHub Secrets থেকে ডাটা পড়ার জন্য os.environ ব্যবহার করা হয়েছে
PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

print(f"[{datetime.now().isoformat()}] 🤖 AI Trust Protocol Scraper Starting...")

# ভ্যারিয়েবল চেক
if not PROJECT_URL or not SUPABASE_KEY:
    print("✗ Error: PROJECT_URL or SUPABASE_KEY is missing in GitHub Secrets!")
    exit(1)

try:
    supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)
    print("✓ Supabase connected successfully!")
except Exception as e:
    print(f"✗ Supabase connection failed: {e}")
    exit(1)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def save_to_db(name, url, source, description=""):
    """Supabase এ ডাটা সেভ করার ফাংশন"""
    if not name or not url:
        return False
    
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
        
        # টেবিলের নাম ai_agents হতে হবে। যদি অন্য নাম হয় তবে এখানে পরিবর্তন করুন।
        result = supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ Added: {name[:30]}... from {source}")
        return True
    except Exception as e:
        # এখানে আসল এররটি প্রিন্ট হবে যদি টেবিল না থাকে বা RLS অন থাকে
        print(f"  ✗ Database Error: {str(e)}")
        return False

def scrape_futurepedia():
    print("\n📍 Scraping Futurepedia...")
    try:
        response = requests.get('https://www.futurepedia.io/rss.xml', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        count = 0
        for item in items[:15]:
            title = item.find('title')
            link = item.find('link')
            if title and link:
                if save_to_db(title.text, link.text, "Futurepedia"):
                    count += 1
            time.sleep(0.5)
        return count
    except Exception as e:
        print(f"  ✗ Futurepedia error: {e}")
        return 0

def scrape_producthunt():
    print("\n📍 Scraping ProductHunt...")
    try:
        response = requests.get('https://www.producthunt.com/feed', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        count = 0
        for item in items[:15]:
            title = item.find('title')
            link = item.find('link')
            if title and link and any(k in title.text.lower() for k in ['ai', 'gpt', 'bot']):
                if save_to_db(title.text, link.text, "ProductHunt"):
                    count += 1
            time.sleep(0.5)
        return count
    except Exception as e:
        print(f"  ✗ ProductHunt error: {e}")
        return 0

def main():
    print("\n" + "="*50)
    print(f"🚀 Job Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total = 0
    total += scrape_futurepedia()
    total += scrape_producthunt()
    
    print("="*50)
    print(f"✅ COMPLETED! Total items added/updated: {total}")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
