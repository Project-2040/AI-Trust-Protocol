import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def save_to_db(name, link, source_name):
    """ডাটাবেসে ডাটা সেভ করার ফাংশন"""
    try:
        # ক্লিনিং এবং ফরম্যাটিং
        clean_name = name.strip()
        if not link.startswith('http'):
            return False
            
        data = {
            "name": clean_name,
            "url": link,
            "category": "AI Agent",
            "trust_score": 7.0, # প্রাথমিক স্কোর
            "safety_index": 7.5
        }
        
        # upsert ব্যবহার করা হয়েছে যাতে একই URL বারবার না ঢুকে
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"[{source_name}] সফলভাবে যুক্ত হয়েছে: {clean_name}")
        return True
    except Exception as e:
        return False

def fetch_from_sources():
    print("Mega Crawler চালু হচ্ছে...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    # সোর্স ১: Futurepedia RSS
    try:
        r = requests.get("https://www.futurepedia.io/rss.xml", headers=headers, timeout=15)
        soup = BeautifulSoup(r.content, features="xml")
        for item in soup.find_all('item'):
            save_to_db(item.title.text, item.link.text, "Futurepedia")
    except: print("Futurepedia সোর্সটি কাজ করছে না।")

    # সোর্স ২: TopAI.tools (New Tools Page)
    try:
        r = requests.get("https://topai.tools/new-ai-tools", headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, 'html.parser')
        # এই সাইটের স্ট্রাকচার অনুযায়ী সব লিংক খুজছি
        for a in soup.find_all('a', href=True):
            if "/t/" in a['href'] or "/tool/" in a['href']:
                name = a.text.strip()
                if len(name) > 2:
                    link = a['href'] if a['href'].startswith('http') else f"https://topai.tools{a['href']}"
                    save_to_db(name, link, "TopAI")
    except: print("TopAI সোর্সটি কাজ করছে না।")

if __name__ == "__main__":
    fetch_from_sources()
    print("ক্রলিং শেষ!")
