import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
import playwright_stealth  # মডিউল হিসেবে ইমপোর্ট করছি
from supabase import create_client, Client

# --- SETUP ---
PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not PROJECT_URL or not SUPABASE_KEY:
    print("❌ Error: PROJECT_URL or SUPABASE_KEY not found in environment variables!")
    exit(1)

supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
        
        # --- Stealth Fix: সব ভার্সনের জন্য নিরাপদ পদ্ধতি ---
        try:
            # প্রথমে stealth_async চেষ্টা করবে, না হলে সাধারণ stealth ব্যবহার করবে
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(page)
            else:
                await playwright_stealth.stealth_async(page) if hasattr(playwright_stealth, 'stealth_async') else playwright_stealth.stealth(page)
        except Exception as e:
            print(f"⚠️ Stealth warning: {e}. Continuing without stealth...")

        print(f"[{datetime.now().isoformat()}] 🚀 Scraping Mode: God Level")

        try:
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            print("📜 Scrolling to load tools...")
            last_height = await page.evaluate("document.body.scrollHeight")
            for i in range(10):
                await page.mouse.wheel(0, 1500)
                await asyncio.sleep(1.5)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            cards = await page.query_selector_all('.w-dyn-item, [class*="tool-card"], .tool-card-component')
            print(f"🔍 Found {len(cards)} potential tools. Syncing with Supabase...")

            count = 0
            for card in cards:
                try:
                    name_el = await card.query_selector('h3, .tool-name-text, [class*="name"]')
                    name = await name_el.inner_text() if name_el else ""
                    
                    link_el = await card.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    img_el = await card.query_selector('img')
                    img_url = ""
                    if img_el:
                        img_url = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')

                    desc_el = await card.query_selector('.tool-description-text, p, [class*="description"]')
                    desc = await desc_el.inner_text() if desc_el else ""
                    
                    cat_el = await card.query_selector('.category-link, .tag-text, [class*="category"]')
                    category = await cat_el.inner_text() if cat_el else "AI Tool"

                    if name and href and len(name) > 2:
                        if any(x in name.lower() for x in ["submit", "news", "video"]): 
                            continue
                        
                        if await save_to_db(name, href, desc, category, img_url):
                            count += 1
                        
                        if count >= 50:
                            break 

                except Exception:
                    continue

            print(f"\n✅ All set! {count} AI tools are now live in your database.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
