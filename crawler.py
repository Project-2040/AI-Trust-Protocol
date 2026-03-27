import os
import requests
import time
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")

if not url or not key:
    print("ERROR: PROJECT_URL or SUPABASE_KEY not set!")
    exit(1)

try:
    supabase: Client = create_client(url, key)
    print("✓ Supabase connection successful!")
except Exception as e:
    print(f"✗ Supabase connection failed: {e}")
    exit(1)

def calculate_trust_score(link):
    """লিংকের সিকিউরিটি এবং পারফরম্যান্স চেক করে স্কোর দেওয়া"""
    start_time = time.time()
    security = 10.0 if link.startswith('https') else 2.0
    
    try:
        response = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        latency = time.time() - start_time
        performance = max(1.0, 10.0 - (latency * 2)) 
    except Exception as e:
        print(f"  Warning: Could not reach {link}: {e}")
        performance = 1.0
        security = 1.0

    final_score = (security * 0.4) + (8.0 * 0.4) + (performance * 0.2)
    return round(final_score, 1), round(security, 1), round(performance, 1)

def save_to_db(name, link, source_name):
    """Database এ ডেটা সেভ করা"""
    if not name or not link:
        return
    
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
        print(f"[✓ {source_name}] Added: {name} | Score: {trust_score}")
    except Exception as e:
        print(f"[✗ {source_name}] Error saving {name}: {e}")

def run_mega_crawler():
    print("\n" + "="*50)
    print("AI Trust Protocol: Mega Crawler শুরু হচ্ছে...")
    print("="*50 + "\n")
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    sources = [
        ("https://www.futurepedia.io/rss.xml", "Futurepedia"),
        ("https://topai.tools/new-ai-tools", "TopAI Tools"),
        ("https://opentools.ai/rss", "OpenTools")
    ]

    total_added = 0
    
    for s_url, s_name in sources:
        print(f"\n📍 Processing: {s_name}")
        print("-" * 40)
        try:
            r = requests.get(s_url, headers=headers, timeout=15)
            r.raise_for_status()
            
            if "rss" in s_url.lower():
                soup = BeautifulSoup(r.content, features="xml")
                items = soup.find_all('item')
                print(f"  Found {len(items)} items")
                
                for item in items:
                    try:
                        title = item.find('title')
                        link = item.find('link')
                        
                        if title and link and title.text and link.text:
                            save_to_db(title.text.strip(), link.text.strip(), s_name)
                            total_added += 1
                    except Exception as e:
                        print(f"  Error processing item: {e}")
                        continue
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                links = soup.find_all('a', href=True)
                print(f"  Found {len(links)} links")
                
                for a in links:
                    try:
                        if "/t/" in a['href'] or "/tool/" in a['href']:
                            name = a.text.strip()
                            if len(name) > 2:
                                link = a['href'] if a['href'].startswith('http') else f"https://topai.tools{a['href']}"
                                save_to_db(name, link, s_name)
                                total_added += 1
                    except Exception as e:
                        print(f"  Error processing link: {e}")
                        continue
                        
        except requests.exceptions.RequestException as e:
            print(f"✗ {s_name} Error: {e}")
        except Exception as e:
            print(f"✗ {s_name} Unexpected Error: {e}")
    
    print("\n" + "="*50)
    print(f"✓ Crawler completed! Total items added: {total_added}")
    print("="*50 + "\n")

if __name__ == "__main__":
    run_mega_crawler()