# Improved crawler.py

import logging
import requests
from sqlalchemy import create_engine, exc

logging.basicConfig(level=logging.INFO)

class Crawler:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        logging.info("Database engine created.")

    def fetch_data(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"An error occurred while fetching data: {e}")
            return None

    def save_to_database(self, data):
        if data is None:
            logging.warning("No data to save.")
            return
        try:
            with self.engine.connect() as connection:
                connection.execute("INSERT INTO data_table (data) VALUES (:data)", {'data': data})
            logging.info("Data saved to database successfully.")
        except exc.SQLAlchemyError as e:
            logging.error(f"Database error occurred: {e}")

# Example usage
if __name__ == '__main__':
    crawler = Crawler('sqlite:///mydatabase.db')
    data = crawler.fetch_data('https://example.com/data')
    crawler.save_to_database(data)