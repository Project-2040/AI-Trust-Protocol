import os
import time
import random
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
from supabase import create_client, Client

# --- CONFIGURATION ---
PROJECT_URL = os.environ.get("PROJECT_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(PROJECT_URL, SUPABASE_KEY)

# রিয়েল হিউম্যান ইউজার এজেন্ট লিস্ট
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def human_delay(min_sec=2, max_sec=5):
    """৪. থ্রটলিং: মানুষের মতো বিরতি নেওয়া"""
    await asyncio.sleep(random.uniform(min_sec, max_sec))

async def save_to_db(name, url, source):
    try:
        data = {
            "name": name.strip()[:200],
            "url": url.strip(),
            "source": source,
            "category": "AI Tool",
            "trust_score": random.uniform(7.0, 9.0), # র্যান্ডম স্কোর হিউম্যান টাচ দেয়
            "is_verified": False
        }
        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
        print(f"  ✓ God-Level Save: {name[:30]}...")
        return True
    except: return False

async def run_god_crawler():
    async with async_playwright() as p:
        # ১. Headless Browser (আসল ক্রোম ব্রাউজার ব্যাকগ্রাউন্ডে চলবে)
        browser = await p.chromium.launch(headless=True)
        
        # ২. Residential Proxy (যদি থাকে তবে ব্যবহার করবে)
        proxy = os.environ.get("RESIDENTIAL_PROXY")
        context_args = {"user_agent": random.choice(USER_AGENTS)}
        if proxy:
            context_args["proxy"] = {"server": proxy}
            
        context = await browser.new_context(**context_args)
        page = await context.new_page()

        # ৩. Stealth Mode: ব্রাউজার যে বট সেটা বুঝতে দিবে না
        await stealth_async(page)

        print(f"[{datetime.now().isoformat()}] 🤖 God-Level Scraper Active...")

        # সোর্স লিস্ট (এখানে আরও সোর্স যোগ করা যাবে)
        sources = [
            {'name': 'FutureTools', 'url': 'https://www.futuretools.io/'},
            {'name': 'Futurepedia', 'url': 'https://www.futurepedia.io/'}
        ]

        total_saved = 0
        for source in sources:
            try:
                print(f"\n📍 Visiting {source['name']}...")
                # মানুষের মতো পেজ লোড করা
                await page.goto(source['url'], wait_until="networkidle")
                await human_delay(3, 6)

                # মাউস স্ক্রলিং সিমুলেশন (যাতে বট না মনে হয়)
                await page.mouse.wheel(0, 500)
                await human_delay(1, 2)

                # ডাটা এক্সট্রাকশন (আসল পেজ কন্টেন্ট থেকে)
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # সোর্স অনুযায়ী ডাটা খোঁজা (উদাহরণস্বরূপ লিঙ্কগুলো নেওয়া হচ্ছে)
                links = soup.find_all('a', href=True)
                count = 0
                for link in links:
                    title = link.get_text().strip()
                    href = link['href']
                    
                    if len(title) > 5 and 'http' in href and count < 10:
                        if await save_to_db(title, href, source['name']):
                            count += 1
                            await human_delay(0.5, 1.5)
                
                total_saved += count
                print(f"  ✓ Found {count} items from {source['name']}")

            except Exception as e:
                print(f"  ✗ Error visiting {source['name']}: {e}")

        await browser.close()
        print(f"\n✅ All Done! Total God-Level Entries: {total_saved}")

if __name__ == "__main__":
    asyncio.run(run_god_crawler())
