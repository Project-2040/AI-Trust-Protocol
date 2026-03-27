import os
import requests
import time
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def calculate_trust_score(link):
    """লিংকের সিকিউরিটি এবং পারফরম্যান্স চেক করে স্কোর দেওয়া"""
    start_time = time.time()
    security = 10.0 if link.startswith('https') else 2.0
    
    try:
        response = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        latency = time.time() - start_time
        # লেটেন্সি যত কম, পারফরম্যান্স স্কোর তত বেশি
        performance = max(1.0, 10.0 - (latency * 2)) 
    except:
        performance = 1.0
        security = 1.0

    # গাণিতিক ফর্মুলা (Security 40% + Performance 20% + Default Privacy 40%)
    final_score = (security * 0.4) + (8.0 * 0.4) + (performance * 0.2)
    return round(final_score, 1), round(security, 1), round(performance, 1)

def save_to_db(name, link, source_name):
    try:
        trust_score, sec, perf = calculate_trust_score(link)
        data = {
            "name": name,
            "url": link,
            "category": "AI Agent",
            "trust_score": trust_score,
            "security_score": sec,
            "performance_score": perf,
            "privacy_score": 8.0,
            "is_verified": False
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"[{source_name}] Added: {name} (Score: {trust_score})")
    except:
        pass

def run_mega_crawler():
    print("AI Trust Protocol: Mega Crawler চালু হচ্ছে...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # সোর্স লিস্ট
    sources = [
        ("https://www.futurepedia.io/rss.xml", "Futurepedia"),
        ("https://topai.tools/new-ai-tools", "TopAI Tools"),
        ("https://opentools.ai/rss", "OpenTools")
    ]

    for s_url, s_name in sources:
        try:
            r = requests.get(s_url, headers=headers, timeout=15)
            if "rss" in s_url:
                soup = BeautifulSoup(r.content, features="xml")
                for item in soup.find_all('item'):
                    save_to_db(item.title.text, item.link.text, s_name)
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                for a in soup.find_all('a', href=True):
                    if "/t/" in a['href'] or "/tool/" in a['href']:
                        name = a.text.strip()
                        if len(name) > 2:
                            link = a['href'] if a['href'].startswith('http') else f"https://topai.tools{a['href']}"
                            save_to_db(name, link, s_name)
        except Exception as e:
            print(f"{s_name} Error: {e}")

if __name__ == "__main__":
    run_mega_crawler()
