import os
import requests
from supabase import create_client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

def fetch_and_save():
    # এখানে আমরা Futurepedia বা API থেকে ডেটা নিব
    # আপাতত একটি ডামি ডেটা দিয়ে টেস্ট করছি
    new_ai = {
        "name": "Claude 3.5",
        "category": "Language Model",
        "trust_score": 95,
        "url": "https://claude.ai",
        "description": "Powerful AI by Anthropic"
    }
    supabase.table("ai_agents").upsert(new_ai).execute()
    print("New AI added to Node The Future!")

fetch_and_save()
