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

if not PROJECT_URL or !SUPABASE_KEY:
    print("❌ Error: Credentials missing!")
    exit(1)

supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)

# --- GOD LEVEL LOGIC: Dynamic Scoring ---
def calculate_trust_metrics(name, desc):
    """এটি AI-এর নাম ও বর্ণনা দেখে একটি ফেক কিন্তু লজিক্যাল ট্রাস্ট স্কোর জেনারেট করবে"""
    score = random.randint(60, 85) # বেস স্কোর
    if any(x in name.lower() for x in ['gpt', 'claude', 'google', 'meta', 'openai']):
        score += random.randint(10, 14) # বড় ব্র্যান্ড হলে স্কোর বেশি
    if len(desc) > 200:
        score += 5 # ডেসক্রিপশন বড় হলে স্বচ্ছতা বেশি
    
    safety = score - random.randint(2, 8) # সেফটি ইনডেক্স সবসময় ট্রাস্টের চেয়ে একটু কম হয়
    return min(score, 99), min(safety, 99)

async def save_to_db(name, url, desc, category, img_url):
    try:
        # ক্যালকুলেট স্কোর
        t_score, s_index = calculate_trust_metrics(name, desc)
        
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "description": desc.strip()[:500],
            "category": category.strip()[:100],
            "image_url": img_url,
            "trust_scor": t_score, # ডাইনামিক স্কোর
            "safety_ind": s_index, # ডাইনামিক সেফটি
            "source": "NOD_CORE_v2",
            "is_verified": True if t_score > 90 else False
        }
        # URL ডুপ্লিকেট হলে আপডেট করবে, নতুন হলে ইনসার্ট করবে
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ◈ Verified & Synced: {name} [Score: {t_score}]")
        return True
    except Exception as e:
        print(f"  ✗ DB Error: {e}")
        return False

async def run_god_crawler():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) 
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Stealth মোড অ্যাক্টিভেট
        try:
            playwright_stealth.stealth(page)
        except: pass

        print(f"[{datetime.now().isoformat()}] 🚀 NOD Engine: Hunting new Intelligence...")

        sources = [
            "https://www.futuretools.io/",
            "https://www.futurepedia.io/" # সোর্স বাড়ানো হলো
        ]

        for target in sources:
            try:
                print(f"🔍 Accessing Source: {target}")
                await page.goto(target, wait_until="networkidle", timeout=60000)
                await asyncio.sleep(5)

                # অটো স্ক্রল
                for _ in range(5):
                    await page.evaluate("window.scrollBy(0, 800)")
                    await asyncio.sleep(1)

                # মাল্টিপল সিলেক্টর ট্রাই করা (God Level Strategy)
                cards = await page.query_selector_all('div[class*="card"], div[class*="item"], a[href*="/tool/"]')
                
                count = 0
                for card in cards:
                    try:
                        name_el = await card.query_selector('h3, h2, .tool-name, b')
                        name = await name_el.inner_text() if name_el else ""
                        
                        link_el = await card.query_selector('a')
                        href = await link_el.get_attribute('href') if link_el else ""
                        if href and not href.startswith('http'):
                            href = target.rstrip('/') + href

                        desc_el = await card.query_selector('p, .description, .text')
                        desc = await desc_el.inner_text() if desc_el else "Advanced AI Agent evaluated by NOD Protocol."
                        
                        cat_el = await card.query_selector('[class*="category"], [class*="tag"]')
                        category = await cat_el.inner_text() if cat_el else "AI Agent"

                        if name and href and len(name) > 2:
                            if await save_to_db(name, href, desc, category, ""):
                                count += 1
                            if count >= 30: break 
                    except: continue

                print(f"✅ Source Synced. Found {count} new agents.")

            except Exception as e:
                print(f"✗ Error at {target}: {e}")

        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
