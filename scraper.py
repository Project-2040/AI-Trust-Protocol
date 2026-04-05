import os
import requests
from supabase import create_client

# তোমার Supabase ক্রেডেনশিয়াল (GitHub Secrets থেকে আসবে)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def hunt_ai():
    # এটি একটি উদাহরন—আমরা বিভিন্ন AI ডিরেক্টরি থেকে ডেটা নিতে পারি
    # আপাতত আমরা ৩টি বড় AI এজেন্টের ডেটা অটোমেটিক ইনসার্ট করছি টেস্ট করার জন্য
    ais = [
        {"name": "ChatGPT 4o", "category": "LLM", "trust_scor": 98, "url": "https://chatgpt.com", "description": "The world's most popular AI by OpenAI."},
        {"name": "Claude 3.5 Sonnet", "category": "LLM", "trust_scor": 96, "url": "https://claude.ai", "description": "Highly advanced reasoning and coding AI by Anthropic."},
        {"name": "Midjourney v6", "category": "Image AI", "trust_scor": 92, "url": "https://midjourney.com", "description": "The leading high-fidelity image generation AI."}
    ]

    for ai in ais:
        try:
            supabase.table("ai_agents").upsert(ai).execute()
            print(f"Verified & Added: {ai['name']}")
        except Exception as e:
            print(f"Error adding {ai['name']}: {e}")

if __name__ == "__main__":
    hunt_ai()
