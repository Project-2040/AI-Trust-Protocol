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

async def save_to_db(name, url, desc, category, img_url):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "description": desc.strip()[:500],
            "category": category.strip()[:100],
            "image_url": img_url,
            "source": "FutureTools",
            "is_verified": True
        }
        # ডাটাবেজে পাঠানো
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✨ Added: {name}")
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

        print(f"[{datetime.now().isoformat()}] 🚀 Image Scraping Active...")

        try:
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            # ইমেজগুলো লোড হওয়ার জন্য নিচে স্ক্রল করা (Lazy Loading ফিক্স)
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight/2)")
            await asyncio.sleep(5)
            await page.evaluate("window.scrollTo(0, 0)") # আবার উপরে আসা

            # কার্ডগুলো সিলেক্ট করা
            cards = await page.query_selector_all('.w-dyn-item, .tool-card-component')
            
            count = 0
            for card in cards:
                try:
                    # ১. নাম ও লিঙ্ক
                    name_el = await card.query_selector('h3, .tool-name-text')
                    name = await name_el.inner_text() if name_el else ""
                    
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ২. ইমেজ (Thumbnail)
                    img_el = await card.query_selector('img')
                    img_url = await img_el.get_attribute('src') if img_el else ""

                    # ৩. ডেসক্রিপশন ও ক্যাটাগরি
                    desc_el = await card.query_selector('.tool-description-text, p')
                    desc = await desc_el.inner_text() if desc_el else "Amazing AI Tool"
                    
                    cat_el = await card.query_selector('.category-link, .tag-text')
                    category = await cat_el.inner_text() if cat_el else "AI Assistant"

                    # ডাটাবেজে সেভ (যদি নাম ও লিঙ্ক থাকে)
                    if name and href and len(name) > 2:
                        # মেনু লিঙ্ক ফিল্টার
                        if any(x in name.lower() for x in ["submit", "news", "video"]): continue
                        
                        if await save_to_db(name, href, desc, category, img_url):
                            count += 1
                        
                        if count >= 30: break # ৩০টি টুল নিবে

                except: continue

            print(f"\n✅ Mission Success! {count} tools with images synchronized.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
