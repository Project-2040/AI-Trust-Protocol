import requests
import time
import supabase

# Improved Crawler V2
class Crawler:
    def __init__(self, supabase_url, supabase_key):
        self.supabase = supabase.create_client(supabase_url, supabase_key)
        self.base_url = "https://api.example.com/ai-tools"
        self.headers = {"User-Agent": "MyCrawler/1.0", "Accept": "application/json"}

    def fetch_data(self):
        retries = 5
        for attempt in range(retries):
            try:
                response = requests.get(self.base_url, headers=self.headers)
                response.raise_for_status()  # Raise an error for bad responses
                return response.json()
            except requests.exceptions.HTTPError as err:
                if response.status_code == 403:
                    print(f"403 Forbidden: Retrying after delay...")
                else:
                    print(f"HTTP error occurred: {err}")
                time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(2 ** attempt)
        return None

    def save_data(self, data):
        # Save to Supabase
        self.supabase.from_('ai_tools').insert(data).execute()

    def run(self):
        data = self.fetch_data()
        if data:
            self.save_data(data)
        else:
            print("Failed to fetch data after multiple attempts.")

if __name__ == '__main__':
    URL = "your_supabase_url"
    KEY = "your_supabase_key"
    crawler = Crawler(URL, KEY)
    crawler.run()