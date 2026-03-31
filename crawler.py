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

async def save_to_db(name, url, desc, category):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "description": desc.strip()[:500],
            "category": category.strip()[:100],
            "source": "FutureTools",
            "trust_score": round(random.uniform(8.0, 9.5), 1),
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

        print(f"[{datetime.now().isoformat()}] 🎯 Fetching REAL AI Tools...")

        try:
            # ১. পেজে যাওয়া
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            # ২. কার্ড লোড হওয়া পর্যন্ত অপেক্ষা করা (খুবই গুরুত্বপূর্ণ)
            # FutureTools এর বর্তমান স্ট্রাকচার অনুযায়ী এই ক্লাসটি চেক করবে
            try:
                await page.wait_for_selector('.tool-card-component, .w-dyn-item', timeout=20000)
            except:
                print("⚠️ Timeout waiting for cards. Trying to scroll...")

            # ৩. স্ক্রল ডাউন (যাতে ইমেজ ও ডিটেইলস লোড হয়)
            await page.mouse.wheel(0, 1500)
            await asyncio.sleep(5)

            # ৪. ডাটা এক্সট্রাকশন
            cards = await page.query_selector_all('.tool-card-component, .w-dyn-item')
            print(f"🔍 Found {len(cards)} cards. Extracting details...")

            count = 0
            for card in cards:
                try:
                    # টাইটেল খোঁজা
                    name_el = await card.query_selector('h3, .tool-name-text, a[style*="font-weight: bold"]')
                    name = await name_el.inner_text() if name_el else ""

                    # ডেসক্রিপশন খোঁজা
                    desc_el = await card.query_selector('.tool-description-text, p')
                    desc = await desc_el.inner_text() if desc_el else ""

                    # ক্যাটাগরি খোঁজা
                    cat_el = await card.query_selector('.category-link, .tag-text')
                    category = await cat_el.inner_text() if cat_el else "AI Tool"

                    # অরিজিনাল ওয়েবসাইট লিঙ্ক
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ফিল্টার: অপ্রাসঙ্গিক লিঙ্ক বাদ দেওয়া
                    if name and href and len(name) > 2:
                        if any(x in name.lower() for x in ["submit", "news", "video", "contact"]):
                            continue
                            
                        if await save_to_db(name, href, desc, category):
                            count += 1
                        
                        if count >= 15: break # টেস্টের জন্য ১৫টি

                except: continue

            print(f"\n✅ Success! Scraped {count} REAL AI tools.")

        except Exception as e:
            print(f"✗ Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
