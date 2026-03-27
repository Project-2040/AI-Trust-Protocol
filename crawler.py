import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. Supabase কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_ai_crawler():
    print("নতুন AI টুলস খোঁজা হচ্ছে...")
    
    # ২. টার্গেট ওয়েবসাইট (Futurepedia - New Tools)
    target_url = "https://www.futurepedia.io/new"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ৩. AI টুলস খুঁজে বের করা (Futurepedia এর স্ট্রাকচার অনুযায়ী)
        # তারা সাধারণত কার্ড বা গ্রিড ফরমেটে ডাটা রাখে
        tools = soup.find_all('div', class_='flex flex-col gap-2') 

        for tool in tools:
            try:
                name_tag = tool.find('h3')
                link_tag = tool.find('a')
                
                if name_tag and link_tag:
                    name = name_tag.text.strip()
                    # পূর্ণাঙ্গ URL তৈরি করা
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = "https://www.futurepedia.io" + link
                    
                    # ৪. ডাটাবেসে সেভ করা (upsert ব্যবহার করা হয়েছে যাতে ডুপ্লিকেট না হয়)
                    data = {
                        "name": name,
                        "url": link,
                        "category": "New AI",
                        "trust_score": 8.0, # ডিফল্ট স্কোর
                        "safety_index": 8.5 # ডিফল্ট ইনডেক্স
                    }

                    # 'url' কলামটি ইউনিক থাকলে একই AI বারবার সেভ হবে না
                    supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
                    print(f"সফলভাবে যুক্ত হয়েছে: {name}")
            except Exception as inner_e:
                continue

    except Exception as e:
        print(f"ক্রল করার সময় সমস্যা হয়েছে: {e}")

if __name__ == "__main__":
    run_ai_crawler()
