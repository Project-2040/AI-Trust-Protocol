import os
import logging
import sqlite3

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Check for required environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL is None:
    logging.error('DATABASE_URL environment variable is not set.')
    raise EnvironmentError('DATABASE_URL not set')

try:
    # Connect to the database
    conn = sqlite3.connect(DATABASE_URL)
    logging.info('Database connection established.')
except sqlite3.Error as e:
    logging.error(f'Error connecting to database: {e}')
    raise

try:
    # Perform database operations
    with conn:
        # Database logic here
        logging.info('Database operations performed successfully.')
except sqlite3.Error as e:
    logging.error(f'Error during database operations: {e}')
finally:
    conn.close()
    logging.info('Database connection closed.')