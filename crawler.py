import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import playwright_stealth
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
        print(f"  ✓ Saved to Database: {name[:30]}")
        return True
    except Exception as e:
        print(f"  ✗ DB Error: {e}")
        return False

async def run_god_crawler():
    async with async_playwright() as p:
        # ব্রাউজার লঞ্চ
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # Stealth Mode
        await playwright_stealth.stealth_async(page)
        print(f"[{datetime.now().isoformat()}] 🚀 God-Level Human Simulation Active...")

        # সোর্স লিস্ট - আপনি চাইলে এখানে আরও লিঙ্ক যোগ করতে পারেন
        sources = [
            {'name': 'FutureTools', 'url': 'https://www.futuretools.io/'}
        ]
        
        total_saved = 0
        for source in sources:
            try:
                print(f"📍 Visiting {source['name']}...")
                await page.goto(source['url'], wait_until="domcontentloaded", timeout=60000)
                
                # হিউম্যান বিহেভিয়ার: র্যান্ডম স্ক্রলিং
                for _ in range(3):
                    await page.mouse.wheel(0, random.randint(300, 700))
                    await asyncio.sleep(random.uniform(1, 3))

                # এলিমেন্ট খুঁজে বের করা
                elements = await page.query_selector_all('a')
                count = 0
                for el in elements:
                    try:
                        title = await el.inner_text()
                        href = await el.get_attribute('href')
                        
                        if title and href and len(title) > 10 and href.startswith('http') and count < 15:
                            if await save_to_db(title, href, source['name']):
                                count += 1
                                await asyncio.sleep(random.uniform(0.5, 1.5))
                    except:
                        continue
                
                total_saved += count
                print(f"✅ {source['name']} finished. Added: {count}")

            except Exception as e:
                print(f"✗ Error scraping {source['name']}: {e}")

        # সেফলি ক্লোজ করা
        await context.close()
        await browser.close()
        print(f"\n🏆 Final Report: Total {total_saved} items synchronized.")

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
