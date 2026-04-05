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
        # Supabase execute() typically returns a response, ensure it's handled
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ Saved: {name}")
        return True
    except Exception as e:
        print(f"  ✗ DB Error: {e}")
        return False

async def run_god_crawler():
    async with async_playwright() as p:
        # Headless=False দিয়ে চেক করুন যদি ব্লক করে তবে
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        await stealth(page)

        print(f"[{datetime.now().isoformat()}] 🚀 Scraping Mode: Enhanced Level")

        try:
            # wait_until="domcontentloaded" ব্যবহার করা নিরাপদ
            await page.goto("https://www.futuretools.io/", wait_until="domcontentloaded", timeout=90000)
            
            # --- স্মার্ট স্ক্রলিং (যতক্ষণ নতুন কন্টেন্ট লোড হয়) ---
            last_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2) # লোড হওয়ার জন্য সময় দিন
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
                # খুব বেশি স্ক্রল হলে ব্রেক করুন (অপশনাল)
                if last_height > 20000: break 

            # কার্ড সিলেকটর আপডেট করা হয়েছে (বেশি জেনেরিক করা হয়েছে)
            cards = await page.query_selector_all('div[class*="tool-card"], .w-dyn-item')
            print(f"🔍 Found {len(cards)} potential tools. Syncing with Supabase...")

            count = 0
            for card in cards:
                try:
                    # টেক্সট এক্সট্রাকশনের জন্য try-except ব্লক
                    name_el = await card.query_selector('h3, [class*="name"]')
                    name = await name_el.inner_text() if name_el else ""
                    
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # ইমেজ ইউআরএল-এর জন্য 'src' এবং 'data-src' চেক করুন (Lazy loading-এর জন্য)
                    img_el = await card.query_selector('img')
                    img_url = ""
                    if img_el:
                        img_url = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')

                    desc_el = await card.query_selector('p, [class*="description"]')
                    desc = await desc_el.inner_text() if desc_el else ""
                    
                    cat_el = await card.query_selector('a[class*="category"], .tag-text')
                    category = await cat_el.inner_text() if cat_el else "AI Tool"

                    if name and href and len(name) > 2:
                        if any(x in name.lower() for x in ["submit", "news", "video"]): continue
                        
                        if await save_to_db(name, href, desc, category, img_url):
                            count += 1
                        
                        if count >= 50: break 

                except Exception as e:
                    continue

            print(f"\n✅ All set! {count} AI tools are now live in your database.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
