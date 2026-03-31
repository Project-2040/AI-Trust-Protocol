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
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ Saved: {name}")
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

        print(f"[{datetime.now().isoformat()}] 🚀 Scraping Mode: God Level (Images Enabled)")

        try:
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            # ইমেজ লোড করানোর জন্য স্মার্ট স্ক্রলিং
            for _ in range(5):
                await page.mouse.wheel(0, 800)
                await asyncio.sleep(1)

            # কার্ড সিলেকশন
            cards = await page.query_selector_all('.w-dyn-item, .tool-card-component')
            print(f"🔍 Found {len(cards)} tools. Syncing with Supabase...")

            count = 0
            for card in cards:
                try:
                    name_el = await card.query_selector('h3, .tool-name-text')
                    name = await name_el.inner_text() if name_el else ""
                    
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ইমেজ ইউআরএল এক্সট্রাকশন (খুবই গুরুত্বপূর্ণ)
                    img_el = await card.query_selector('img')
                    img_url = await img_el.get_attribute('src') if img_el else ""

                    desc_el = await card.query_selector('.tool-description-text, p')
                    desc = await desc_el.inner_text() if desc_el else ""
                    
                    cat_el = await card.query_selector('.category-link, .tag-text')
                    category = await cat_el.inner_text() if cat_el else "AI Tool"

                    if name and href and len(name) > 2:
                        # ফিল্টার
                        if any(x in name.lower() for x in ["submit", "news", "video"]): continue
                        
                        if await save_to_db(name, href, desc, category, img_url):
                            count += 1
                        
                        if count >= 30: break 

                except: continue

            print(f"\n✅ All set! {count} AI tools are now live in your database.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
