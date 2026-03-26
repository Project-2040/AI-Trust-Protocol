import asyncio
from playwright.async_api import async_playwright
from supabase import create_client
import random

# Credentials
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

async def run_pro_crawler():
    async with async_playwright() as p:
        print("--- STARTING BROWSER ---")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # সরাসরি RSS ফিড ট্রাই করা (এটি ১ সেকেন্ডে ডেটা দেয়)
            print("--- FETCHING DATA ---")
            await page.goto("https://www.futurepedia.io/rss.xml", timeout=60000)
            content = await page.content()
            
            # ডেটাবেজে কানেকশন টেস্ট করতে একটি ফেইক ডাটা আগে ইনসার্ট করি
            # যদি এটি সফল হয়, বুঝবেন সুপাবেস ঠিক আছে
            test_data = {
                "name": f"AI Tool {random.randint(100, 999)}",
                "category": "Live Sync",
                "trust_scor": 9.5,
                "safety_ind": 98,
                "url": "https://futurepedia.io"
            }
            supabase.table("ai_agents").insert(test_data).execute()
            print("✅ TEST DATA SYNCED!")

        except Exception as e:
            print(f"❌ CRITICAL ERROR: {str(e)}")
        finally:
            await browser.close()
            print("--- MISSION ENDED ---")

if __name__ == "__main__":
    asyncio.run(run_pro_crawler())
