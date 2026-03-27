import requests
import time
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
import logging

logging.basicConfig(level=logging.INFO)

class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36'
        ]

    def fetch_url(self, url):
        headers = {'User-Agent': random.choice(self.user_agents)}
        try:
            response = self.session.get(url, headers=headers)
            response.raise_for_status()  # raises HTTPError for bad responses
            return response.content
        except RequestException as e:
            logging.error(f'Error fetching {url}: {e}')
            return None

    def crawl(self, urls):
        for url in urls:
            content = self.fetch_url(url)
            if content:
                logging.info(f'Successfully fetched {url}')
                time.sleep(2)  # Delay between requests
            else:
                logging.warning(f'Failed to fetch {url}')

# Example usage:
# crawler = Crawler()
# crawler.crawl(['http://example.com', 'http://example.org'])
