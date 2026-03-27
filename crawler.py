import os
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# ১. কানেকশন সেটআপ
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def run_ai_crawler():
    print("AI টুলস খোঁজা শুরু হচ্ছে...")
    
    # ২. টার্গেট সাইট (Futurepedia New Tools)
    # আমরা সরাসরি তাদের API বা নির্দিষ্ট ফিড চেক করার চেষ্টা করছি
    target_url = "https://www.futurepedia.io/new"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # ৩. বিভিন্ন ধরণের ট্যাগে ডেটা খোঁজা (যেহেতু তারা ক্লাস পরিবর্তন করে)
        # সাধারণত তারা h3 বা h2 ট্যাগ ব্যবহার করে নামের জন্য
        found_count = 0
        
        # আমরা সব 'a' ট্যাগ চেক করছি যেগুলোতে AI টুলের লিংক থাকতে পারে
        for link_tag in soup.find_all('a', href=True):
            # লিংকগুলোর ভেতর সাধারণত /tool/ বা এই জাতীয় শব্দ থাকে
            href = link_tag['href']
            name_tag = link_tag.find(['h3', 'h2', 'span'])
            
            if name_tag and len(name_tag.text.strip()) > 2:
                name = name_tag.text.strip()
                full_url = href if href.startswith('http') else f"https://www.futurepedia.io{href}"
                
                # কিছু ফিল্টার যাতে ফালতু লিংক না যায়
                if "/tool/" in full_url or "futurepedia.io" in full_url:
                    data = {
                        "name": name,
                        "url": full_url,
                        "category": "AI Agent",
                        "trust_score": 7.5,
                        "safety_index": 8.0
                    }
                    
                    try:
                        # ডাটাবেসে পাঠানো
                        supabase.table('ai_agents').upsert(data, on_conflict='url').execute()
                        print(f"সংরক্ষিত: {name}")
                        found_count += 1
                    except:
                        continue
            
            if found_count >= 10: # একবারে ১০টি নিলেই যথেষ্ট
                break

        if found_count == 0:
            print("দুঃখিত, কোনো নতুন টুল খুঁজে পাওয়া যায়নি। সাইটের ডিজাইন হয়তো বদলেছে।")
        else:
            print(f"মোট {found_count} টি টুল পাওয়া গেছে!")

    except Exception as e:
        print(f"ভুল হয়েছে: {e}")

if __name__ == "__main__":
    run_ai_crawler()
