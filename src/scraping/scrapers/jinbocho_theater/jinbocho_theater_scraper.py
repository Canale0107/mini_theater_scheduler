from src.scraping.scraper_interface import ScraperInterface
from . import jinbocho_theater_util

__all__ = ['JinbochoTheaterScraper']

class JinbochoTheaterScraper(ScraperInterface):
    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_programs(self):

        programs = jinbocho_theater_util.get_programs(self.base_url)
        return programs

    def scrape_movies(self, program_url):

        movies = jinbocho_theater_util.get_movies(program_url)
        return movies
    
    def scrape_movie_schedules(self, program_url):

        movie_schedules = jinbocho_theater_util.get_movie_schedules(program_url)
        return movie_schedules
