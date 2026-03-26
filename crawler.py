import asyncio
from playwright.async_api import async_playwright
from supabase import create_client
import random
import sys

# Supabase Credentials
URL = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
KEY = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(URL, KEY)

async def debug_crawler():
    async with async_playwright() as p:
        print("--- STEP 1: Launching Stealth Browser ---")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        print("--- STEP 2: Connecting to Futurepedia ---")
        try:
            # পেজ লোড হওয়া পর্যন্ত সর্বোচ্চ ১ মিনিট অপেক্ষা
            response = await page.goto("https://www.futurepedia.io/", wait_until="networkidle", timeout=60000)
            print(f"Server Response Status: {response.status}")
            
            # ৫ সেকেন্ড এক্সট্রা সময় যাতে JS ডেটা রেন্ডার হয়
            await page.wait_for_timeout(5000)
            
            # পেজের টাইটেল প্রিন্ট করে দেখা যে আসলে পেজে ঢুকতে পেরেছে কি না
            title = await page.title()
            print(f"Connected Page Title: {title}")

            # STEP 3: ডেটা খোঁজা (JavaScript এর মাধ্যমে)
            print("--- STEP 3: Extracting Data via JS Engine ---")
            tools = await page.evaluate('''() => {
                const results = [];
                // Futurepedia এর কার্ড হেডারগুলো ধরার চেষ্টা
                document.querySelectorAll('h3').forEach(el => {
                    if(el.innerText.trim().length > 1) results.append(el.innerText.trim());
                });
                return results;
            }''')

            print(f"Debug Info: Found {len(tools)} items on the page.")

            if not tools:
                print("⚠️ Warning: No data found! Futurepedia might be blocking the bot's view.")
                # স্ক্রিনশট নেওয়ার চেষ্টা (গিটহাবে সেভ হবে না, কিন্তু কোড রান হবে)
                return

            # STEP 4: ডাটাবেজ ইনসার্ট চেক
            print("--- STEP 4: Attempting Database Sync ---")
            for name in tools[:5]:
                print(f"Trying to add: {name}...")
                
                # ইনসার্ট করার আগে সুপাবেস কানেকশন টেস্ট
                try:
                    data = {
                        "name": name,
                        "category": "Auto Debug",
                        "trust_scor": round(random.uniform(8.0, 9.5), 1),
                        "safety_ind": random.randint(80, 95),
                        "url": "https://futurepedia.io"
                    }
                    res = supabase.table("ai_agents").insert(data).execute()
                    print(f"✅ Success: Saved {name} to Supabase!")
                except Exception as db_err:
                    print(f"❌ Supabase Error for {name}: {db_err}")

        except Exception as e:
            print(f"❌ Critical Error: {str(e)}")
        finally:
            await browser.close()
            print("--- MISSION ENDED ---")

if __name__ == "__main__":
    asyncio.run(debug_crawler())
