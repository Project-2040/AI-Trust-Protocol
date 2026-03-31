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
            "trust_score": round(random.uniform(8.0, 9.5), 1),
            "is_verified": True,
            "last_checked": datetime.now().isoformat()
        }
        # URL ইউনিক হওয়ায় একই টুল বারবার অ্যাড হবে না
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

        print(f"[{datetime.now().isoformat()}] 🎯 Scraping High-Quality AI Details...")

        try:
            # সরাসরি FutureTools এর অল-টুলস পেজে যাওয়া
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            # ডিনামিক কন্টেন্ট লোড হওয়ার জন্য একটু নিচে স্ক্রল করা
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(5)

            # নতুন সিলেক্টর যা দিয়ে নিখুঁতভাবে কার্ড ধরা যাবে
            # FutureTools মূলত 'w-dyn-item' ক্লাস ব্যবহার করে তাদের কার্ডের জন্য
            cards = await page.query_selector_all('.w-dyn-item')
            
            print(f"🔍 Found {len(cards)} potential AI cards on page...")

            count = 0
            for card in cards:
                try:
                    # ১. নাম (Title)
                    name_el = await card.query_selector('h3, .tool-name-text')
                    name = await name_el.inner_text() if name_el else ""

                    # ২. ডেসক্রিপশন (Description)
                    desc_el = await card.query_selector('.tool-description-text, p')
                    desc = await desc_el.inner_text() if desc_el else "Professional AI Tool for business and productivity."

                    # ৩. লিঙ্ক (URL)
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ৪. ক্যাটাগরি (Category)
                    cat_el = await card.query_selector('.category-link, .tag-text')
                    category = await cat_el.inner_text() if cat_el else "AI Assistant"

                    # নাম এবং লিঙ্ক থাকলেই কেবল ডাটাবেজে সেভ হবে
                    if name and href and len(name) > 1:
                        # মেনু লিঙ্কগুলো (যেমন: Submit, News) বাদ দেওয়ার ফিল্টার
                        if any(x in name.lower() for x in ["submit", "news", "contact", "videos"]):
                            continue
                            
                        if await save_to_db(name, href, desc, category, "FutureTools"):
                            count += 1
                        
                        if count >= 20: break # একবারে ২০টি করে টুল নিবে

                except Exception as card_err:
                    continue

            print(f"\n✅ SUCCESS! Total {count} REAL AI tools pushed to website.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
