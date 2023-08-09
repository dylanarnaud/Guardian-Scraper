# --- Standard Libraries ---
import logging
import requests
import schedule
import signal
import sqlite3
import threading
import time

# --- Custom Modules ---
from guardian_scraper import GuardianScraper
from guardian_database import GuardianDatabase
from guardian_api import GuardianAPI

# --- Constants ---
NUM_SCRAPER_PAGES_INITIAL = 10
NUM_SCRAPER_PAGES = 1
MINUTES_BETWEEN_RUNS = 60

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def scraper_job(pages_to_scrape=NUM_SCRAPER_PAGES):
    """Scrape, load, and transform data"""
    logging.info("Starting the scraper job...")
    
    # Scrape data first
    logging.info("Starting task: Scraping data")
    try:
        scraper.scrape_data(page_count=pages_to_scrape)
        if scraper.data is None:
            raise ValueError("Scraped data is empty.")
        logging.info("Completed task: Scraping data")
    except Exception as e:
        logging.error(f"Error during Scraping data: {e}")
        return

    # Now, proceed to loading and transforming if data is available
    tasks = [
        ('Loading data', database.load, {'dataframe': scraper.data}),
        ('Transforming data', database.transform, {})
    ]

    for task_name, task_func, task_args in tasks:
        logging.info(f"Starting task: {task_name}")
        try:
            task_func(**task_args)
            logging.info(f"Completed task: {task_name}")
        except Exception as e:
            logging.error(f"Error during {task_name}: {e}")

    logging.info("Finished the scraper job.")



def api_launch():
    """Launch the GuardianAPI for better concurrency"""
    api.run(debug=False, threaded=True)


def handle_termination_signal(_, __):
    """Handle termination for a graceful shutdown"""
    logging.info('Shutting down gracefully...')
    api.stop()  # Using GuardianAPI's stop() function to stop the app.
    exit(0)


# --- Main Execution ---
if __name__ == "__main__":
    logging.info('Guardian Scraper and API starting up...')

    # Signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, handle_termination_signal)
    signal.signal(signal.SIGINT, handle_termination_signal)

    # Initialize database
    database = GuardianDatabase()
    logging.info("Database initialized!")
    database.initialize_database()

    # Run the scraper job with more pages if no data exists, else use the regular number
    scraper = GuardianScraper()
    data_exists = database.has_data()
    pages_to_scrape = NUM_SCRAPER_PAGES_INITIAL if not data_exists else NUM_SCRAPER_PAGES
    scraper_job(pages_to_scrape=pages_to_scrape)

    # Initialize GuardianAPI
    api = GuardianAPI()

    # Schedule scraper job runs
    schedule.every(MINUTES_BETWEEN_RUNS).minutes.do(scraper_job)

    # Launch GuardianAPI concurrently
    api_thread = threading.Thread(target=api_launch)
    api_thread.start()

    # Check scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)