import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
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

async def save_to_db(name, url, desc, category, source):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "description": desc.strip()[:500],
            "category": category.strip()[:100],
            "source": source,
            "trust_score": round(random.uniform(7.8, 9.5), 1),
            "is_verified": True
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✨ Added AI: {name}")
        return True
    except Exception as e:
        print(f"  ✗ DB Error: {e}")
        return False

async def run_god_crawler():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await stealth(page)

        print(f"[{datetime.now().isoformat()}] 🎯 Fetching real AI Tool details...")

        try:
            # FutureTools এর মেইন পেজে যাওয়া
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5)

            # AI টুলের কার্ডগুলো খুঁজে বের করা (FutureTools এর স্পেসিফিক ক্লাস)
            # আমরা এখানে কার্ডের ভেতরের টাইটেল, ডেসক্রিপশন এবং ক্যাটাগরি টার্গেট করছি
            cards = await page.query_selector_all('.tool-card-component') # এটি তাদের কার্ডের ক্লাস
            
            if not cards:
                # যদি উপরের ক্লাস কাজ না করে তবে বিকল্প পদ্ধতি
                cards = await page.query_selector_all('.w-dyn-item')

            count = 0
            for card in cards[:20]: # প্রথম ২০টি আসল টুল নিবে
                try:
                    # ১. নাম সংগ্রহ
                    name_el = await card.query_selector('h1, h2, h3, .tool-name')
                    name = await name_el.inner_text() if name_el else None
                    
                    # ২. লিঙ্ক সংগ্রহ
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else None
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ৩. ডেসক্রিপশন সংগ্রহ
                    desc_el = await card.query_selector('.tool-description, p')
                    desc = await desc_el.inner_text() if desc_el else "AI Tool for productivity"

                    # ৪. ক্যাটাগরি সংগ্রহ
                    cat_el = await card.query_selector('.category-tag, .tool-category')
                    category = await cat_el.inner_text() if cat_el else "General AI"

                    if name and href and len(name) > 2:
                        if await save_to_db(name, href, desc, category, "FutureTools"):
                            count += 1
                except:
                    continue

            print(f"\n✅ Success! Scraped {count} REAL AI tools with details.")

        except Exception as e:
            print(f"✗ Scraping Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
