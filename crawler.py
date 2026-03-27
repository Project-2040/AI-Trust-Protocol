import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def fetch_and_save(source_url, source_name):
    print(f"{source_name} থেকে ডাটা খোঁজা হচ্ছে...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(source_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.content, features="xml" if "rss" in source_url else "html.parser")
        
        found = 0
        # RSS ফিড এর জন্য
        if "rss" in source_url:
            items = soup.find_all('item')
            for item in items:
                name = item.title.text
                link = item.link.text
                if save_to_db(name, link): found += 1
        
        # সাধারণ HTML সাইট এর জন্য (উদাহরণ: TopAI)
        else:
            for link_tag in soup.find_all('a', href=True):
                if "/tools/" in link_tag['href'] and len(link_tag.text.strip()) > 3:
                    name = link_tag.text.strip()
                    link = link_tag['href']
                    if save_to_db(name, link): found += 1
        
        print(f"{source_name} থেকে {found} টি নতুন টুল পাওয়া গেছে।")
    except Exception as e:
        print(f"{source_name} এরর: {e}")

def save_to_db(name, link):
    try:
        data = {
            "name": name,
            "url": link,
            "category": "AI Tool",
            "trust_score": 5.0, # ডিফল্ট স্কোর
            "safety_index": 5.0
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        return True
    except:
        return False

def run_mega_crawler():
    # সোর্স লিস্ট - এখানে আপনি যত খুশি সাইট যোগ করতে পারেন
    sources = [
        ("https://www.futurepedia.io/rss.xml", "Futurepedia"),
        ("https://topai.tools/new-ai-tools", "TopAI Tools"),
        ("https://opentools.ai/rss", "OpenTools")
    ]
    
    for s_url, s_name in sources:
        fetch_and_save(s_url, s_name)

if __name__ == "__main__":
    run_mega_crawler()
