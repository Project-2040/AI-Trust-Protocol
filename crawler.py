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

if not PROJECT_URL or not SUPABASE_KEY:
    print("❌ Error: PROJECT_URL or SUPABASE_KEY not found!")
    exit(1)

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
        # Headless=True keep for GitHub Actions
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        
        try:
            if hasattr(playwright_stealth, 'stealth_async'):
                await playwright_stealth.stealth_async(page)
            else:
                playwright_stealth.stealth(page)
        except:
            pass

        print(f"[{datetime.now().isoformat()}] 🚀 Scraping Mode: Hyper Level")

        try:
            # Increase timeout and use networkidle
            await page.goto("https://www.futuretools.io/", wait_until="networkidle", timeout=90000)
            
            # Wait a bit for JS to fully render
            await asyncio.sleep(5)

            print("📜 Scrolling to load tools...")
            for i in range(8):
                await page.evaluate("window.scrollBy(0, 1000)")
                await asyncio.sleep(2)

            # --- ULTIMATE SELECTOR STRATEGY ---
            # We try multiple ways to find the tools
            cards = await page.query_selector_all('div[data-w-id], .w-dyn-item, [class*="card"], [class*="tool"]')
            
            if not cards:
                # Last resort: Find all <a> tags that look like tool links
                cards = await page.query_selector_all('a[href*="/tool/"]')
                print("⚠️ Using fallback link-based selection...")

            print(f"🔍 Found {len(cards)} potential items. Syncing with Supabase...")

            count = 0
            for card in cards:
                try:
                    # If we found <a> tags, we need to go to the parent container
                    container = card if card.evaluate("el => el.tagName !== 'A'") else await card.evaluate_handle("el => el.parentElement")
                    
                    # Try to find name (usually inside h3 or a strong tag)
                    name_el = await container.query_selector('h3, .tool-name, [class*="name"], b')
                    name = await name_el.inner_text() if name_el else ""
                    
                    # Link
                    link_el = await container.query_selector('a')
                    href = await link_el.get_attribute('href') if link_el else ""
                    if href and not href.startswith('http'):
                        href = "https://www.futuretools.io" + href

                    # Image
                    img_el = await container.query_selector('img')
                    img_url = ""
                    if img_el:
                        img_url = await img_el.get_attribute('src') or await img_el.get_attribute('data-src')

                    # Description
                    desc_el = await container.query_selector('p, [class*="description"], [class*="text"]')
                    desc = await desc_el.inner_text() if desc_el else ""
                    
                    # Category
                    cat_el = await container.query_selector('[class*="category"], [class*="tag"]')
                    category = await cat_el.inner_text() if cat_el else "AI Tool"

                    if name and href and len(name) > 2:
                        if any(x in name.lower() for x in ["submit", "news", "video"]): continue
                        if await save_to_db(name, href, desc, category, img_url):
                            count += 1
                        if count >= 50: break 

                except Exception:
                    continue

            print(f"\n✅ All set! {count} AI tools are now live in your database.")

        except Exception as e:
            print(f"✗ Global Error: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
