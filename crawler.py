import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
# ইমপোর্ট করার পদ্ধতি পরিবর্তন করা হয়েছে
from playwright_stealth import stealth
from supabase import create_client, Client

# --- SETUP ---
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
            "trust_score": round(random.uniform(7.5, 9.2), 1),
            "is_verified": False
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ Saved: {name[:30]}")
        return True
    except Exception as e:
        print(f"  ✗ DB Error: {e}")
        return False

async def run_god_crawler():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        # Stealth Mode চালু করার সঠিক উপায়
        await stealth(page)
        
        print(f"[{datetime.now().isoformat()}] 🚀 Scraper is now Human-Like...")

        # টেস্ট সোর্স
        url = "https://www.futuretools.io/"
        
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5) 

            # ডাটা সংগ্রহ
            links = await page.query_selector_all('a')
            count = 0
            for link in links:
                try:
                    title = await link.inner_text()
                    href = await link.get_attribute('href')
                    
                    if title and href and 'http' in href and count < 15:
                        if await save_to_db(title, href, "FutureTools"):
                            count += 1
                except: continue
            
            print(f"✅ Success! Added {count} items.")

        except Exception as e:
            print(f"✗ Error: {e}")

        # সেফলি ক্লোজ করা
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
