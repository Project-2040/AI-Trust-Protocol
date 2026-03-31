import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
# ইমপোর্ট করার পদ্ধতি আপডেট করা হলো
from playwright_stealth import stealth
from supabase import create_client, Client

PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
]

async def save_to_db(name, url, source):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "source": source,
            "category": "AI Tool",
            "trust_score": round(random.uniform(7.0, 9.0), 1),
            "security_score": 8.0,
            "performance_score": 8.0,
            "privacy_score": 7.5,
            "is_verified": False
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ Saved: {name[:30]}")
        return True
    except: return False

async def run_god_crawler():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        proxy = os.environ.get("RESIDENTIAL_PROXY")
        context_args = {"user_agent": random.choice(USER_AGENTS)}
        if proxy: context_args["proxy"] = {"server": proxy}
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        # Stealth Mode চালু করা (নতুন সিনট্যাক্স)
        await stealth(page)

        print(f"[{datetime.now().isoformat()}] 🚀 God-Level Scraper Starting...")

        # টেস্ট করার জন্য FutureTools ব্যবহার করছি (ব্লক হওয়ার ভয় কম)
        source = {'name': 'FutureTools', 'url': 'https://www.futuretools.io/'}
        
        try:
            await page.goto(source['url'], wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(random.uniform(5, 8)) # মানুষের মতো ওয়েট

            # ডাটা খুঁজে বের করা
            links = await page.query_selector_all('a')
            total_saved = 0
            
            for link in links[:30]: # প্রথম ৩০টি লিঙ্ক চেক করবে
                title = await link.inner_text()
                href = await link.get_attribute('href')
                
                if title and href and len(title) > 10 and 'http' in href:
                    if await save_to_db(title, href, source['name']):
                        total_saved += 1
                
            print(f"\n✅ COMPLETED! Items added: {total_saved}")

        except Exception as e:
            print(f"✗ Error: {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
