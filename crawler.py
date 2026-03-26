import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random

# আপনার সুপাবেস তথ্য
url = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
key = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(url, key)

def start_crawling():
    # উদাহরণ হিসেবে একটি AI ডিরেক্টরি সাইট
    target_url = "https://www.futurepedia.io/" 
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # সাইট থেকে এআই টুলের নাম সংগ্রহ (উদাহরণ স্বরূপ প্রথম ৫টি)
        tools = soup.find_all('h3', limit=5) 
        
        for tool in tools:
            name = tool.get_text().strip()
            
            # ডাটাবেজে অলরেডি আছে কি না চেক করা
            check = supabase.table("ai_agents").select("name").eq("name", name).execute()
            
            if not check.data:
                data = {
                    "name": name,
                    "category": "AI Agent",
                    "trust_scor": round(random.uniform(7.0, 9.5), 1),
                    "safety_ind": random.randint(80, 99),
                    "url": "https://www.futurepedia.io" # অরিজিনাল ইউআরএল স্ক্র্যাপ করার লজিক এখানে যুক্ত করা যায়
                }
                supabase.table("ai_agents").insert(data).execute()
                print(f"Added: {name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_crawling()
