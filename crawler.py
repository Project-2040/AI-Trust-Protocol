import os
from supabase import create_client, Client

# GitHub Secrets থেকে ডাটা পড়া
url = os.environ.get("PROJECT_URL")
key = os.environ.get("SUPABASE_KEY")

# চেক করা হচ্ছে ডাটা পাওয়া গেছে কি না
if not url or not key:
    print("Error: Secrets load hoyni! GitHub Actions setting check korun.")
else:
    supabase: Client = create_client(url, key)
    print("Supabase connection successful!")
    
