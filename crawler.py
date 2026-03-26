import requests
from bs4 import BeautifulSoup
from supabase import create_client
import random
import time

# আপনার সুপাবেস তথ্য
url = "https://dmfpnkyiqybzfpzwnvtc.supabase.co"
key = "sb_publishable_GX3-5y1b56mbjhMSMnX51g_afmPxKXC"
supabase = create_client(url, key)

def start_crawling():
    # নতুন সোর্স: এটি অনেক বেশি ডেটা দেয় এবং ব্লক কম করে
    target_url = "https://www.futuretools.io/" 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # এই সাইটে এআই টুলগুলোর নাম সাধারণত 'h3' বা নির্দিষ্ট ক্লাস এ থাকে
        # আমরা সব লিঙ্ক থেকে নাম খোঁজার চেষ্টা করব
        tools = soup.select('.tool-card-name-link') or soup.find_all('h3')
        
        added_count = 0
        for tool in tools:
            name = tool.get_text().strip()
            
            if len(name) > 2 and added_count < 5: # একসাথে ৫টি করে নতুন টুল যোগ হবে
                # চেক করা হচ্ছে আগে থেকে আছে কি না
                check = supabase.table("ai_agents").select("name").eq("name", name).execute()
                
                if not check.data:
                    data = {
                        "name": name,
                        "category": "AI Discovery",
                        "trust_scor": round(random.uniform(7.5, 9.8), 1), # আপনার ডাটাবেজ কলাম
                        "safety_ind": random.randint(85, 99),            # আপনার ডাটাবেজ কলাম
                        "url": "https://www.futuretools.io"
                    }
                    supabase.table("ai_agents").insert(data).execute()
                    print(f"Successfully Automated: {name}")
                    added_count += 1
                    time.sleep(1) # সাইট যেন ব্লক না করে তাই ১ সেকেন্ড বিরতি
                    
        if added_count == 0:
            print("No new tools found or already up to date.")
            
    except Exception as e:
        print(f"Automation Error: {e}")

if __name__ == "__main__":
    start_crawling()
