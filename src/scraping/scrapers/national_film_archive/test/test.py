import os
from src.scraping.test.test_scraper import test_scraper

if __name__ == '__main__':
    THEATER_ID = 3
    output_dirpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
    test_scraper(THEATER_ID, output_dirpath)
