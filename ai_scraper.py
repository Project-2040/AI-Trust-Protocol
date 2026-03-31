#!/usr/bin/env python3
"""
AI Trust Protocol - Complete Web Scraper
Scrapes AI tools from multiple sources and stores in Supabase
"""

import os
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Initialize Supabase
PROJECT_URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
SUPABASE_KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"

print(f"[{datetime.now().isoformat()}] 🤖 AI Trust Protocol Scraper Starting...")

try:
    supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)
    print("✓ Supabase connected!")
except Exception as e:
    print(f"✗ Supabase connection failed: {e}")
    exit(1)

# Headers to avoid 403
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def save_to_db(name, url, source, description=""):
    """Save AI tool to Supabase"""
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
        
        result = supabase.table('ai_agents').upsert(
            data,
            on_conflict='url'
        ).execute()
        
        print(f"  ✓ {name} from {source}")
        return True
    except Exception as e:
        print(f"  ✗ Error: {str(e)[:80]}")
        return False

def scrape_futurepedia():
    """Scrape from Futurepedia RSS"""
    print("\n📍 Scraping Futurepedia...")
    try:
        response = requests.get('https://www.futurepedia.io/rss.xml', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        count = 0
        for item in items[:30]:
            try:
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                
                if title and link:
                    name = title.text.strip()
                    url = link.text.strip()
                    desc = description.text.strip() if description else ""
                    
                    if save_to_db(name, url, "Futurepedia", desc):
                        count += 1
                    time.sleep(0.3)
            except:
                pass
        
        print(f"  Total from Futurepedia: {count}")
        return count
    except Exception as e:
        print(f"  ✗ Futurepedia error: {e}")
        return 0

def scrape_topai():
    """Scrape from TopAI Tools"""
    print("\n📍 Scraping TopAI Tools...")
    try:
        response = requests.get('https://topai.tools/', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all tool links
        links = soup.find_all('a', href=True)
        
        count = 0
        for link in links:
            try:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Filter for tool links
                if ('/t/' in href or '/tool/' in href) and len(text) > 2:
                    url = href if href.startswith('http') else f'https://topai.tools{href}'
                    
                    if save_to_db(text, url, "TopAI"):
                        count += 1
                    time.sleep(0.3)
                    
                    if count >= 30:
                        break
            except:
                pass
        
        print(f"  Total from TopAI: {count}")
        return count
    except Exception as e:
        print(f"  ✗ TopAI error: {e}")
        return 0

def scrape_opentools():
    """Scrape from OpenTools"""
    print("\n📍 Scraping OpenTools...")
    try:
        response = requests.get('https://opentools.ai/rss', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        count = 0
        for item in items[:30]:
            try:
                title = item.find('title')
                link = item.find('link')
                description = item.find('description')
                
                if title and link:
                    name = title.text.strip()
                    url = link.text.strip()
                    desc = description.text.strip() if description else ""
                    
                    if save_to_db(name, url, "OpenTools", desc):
                        count += 1
                    time.sleep(0.3)
            except:
                pass
        
        print(f"  Total from OpenTools: {count}")
        return count
    except Exception as e:
        print(f"  ✗ OpenTools error: {e}")
        return 0

def scrape_producthunt():
    """Scrape from ProductHunt"""
    print("\n📍 Scraping ProductHunt...")
    try:
        response = requests.get('https://www.producthunt.com/feed', headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'xml')
        items = soup.find_all('item')
        
        count = 0
        for item in items[:30]:
            try:
                title = item.find('title')
                link = item.find('link')
                
                if title and link:
                    name = title.text.strip()
                    url = link.text.strip()
                    
                    # Only add if it's AI related
                    if any(keyword in name.lower() for keyword in ['ai', 'ml', 'gpt', 'chat', 'tool']):
                        if save_to_db(name, url, "ProductHunt"):
                            count += 1
                        time.sleep(0.3)
            except:
                pass
        
        print(f"  Total from ProductHunt: {count}")
        return count
    except Exception as e:
        print(f"  ✗ ProductHunt error: {e}")
        return 0

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🤖 AI TRUST PROTOCOL - WEB SCRAPER")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*70)
    
    total = 0
    
    # Scrape from all sources
    total += scrape_futurepedia()
    time.sleep(2)
    
    total += scrape_topai()
    time.sleep(2)
    
    total += scrape_opentools()
    time.sleep(2)
    
    total += scrape_producthunt()
    
    # Print summary
    print("\n" + "="*70)
    print(f"✓ SCRAPING COMPLETED!")
    print(f"  Total items added: {total}")
    print(f"  Finished: {datetime.now().isoformat()}")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠ Scraper interrupted")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        exit(1)
