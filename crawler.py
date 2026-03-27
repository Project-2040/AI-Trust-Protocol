import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. Supabase কানেকশন (GitHub Secrets থেকে আসবে)
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_ai_crawler():
    print("নতুন AI টুলস খোঁজা শুরু হচ্ছে...")
    
    # ২. Futurepedia ওয়েবসাইট থেকে ডাটা নেওয়া
    target_url = "https://www.futurepedia.io/new"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(target_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ৩. AI কার্ডগুলো খুঁজে বের করা
        # Futurepedia-র বর্তমান স্ট্রাকচার অনুযায়ী কার্ডগুলো লুপ করা হচ্ছে
        tools = soup.select('div.flex.flex-col.gap-2') 

        for tool in tools:
            try:
                name_tag = tool.find('h3')
                link_tag = tool.find('a')
                
                if name_tag and link_tag:
                    name = name_tag.text.strip()
                    tool_url = link_tag['href']
                    if not tool_url.startswith('http'):
                        tool_url = "https://www.futurepedia.io" + tool_url
                    
                    # ৪. ডাটাবেসে সেভ করা (Upsert ব্যবহার করা হয়েছে যাতে ডুপ্লিকেট না হয়)
                    data = {
                        "name": name,
                        "url": tool_url,
                        "category": "Latest AI",
                        "trust_score": 8.5,
                        "safety_index": 9.0
                    }

                    # 'url' কলামের ওপর ভিত্তি করে ডুপ্লিকেট চেক করবে
                    supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
                    print(f"সফলভাবে ডাটাবেসে যুক্ত হয়েছে: {name}")
            except Exception:
                continue

    except Exception as e:
        print(f"ক্রল করার সময় সমস্যা হয়েছে: {e}")

if __name__ == "__main__":
    run_ai_crawler()
