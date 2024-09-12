from src.scraping.scraper_interface import ScraperInterface
from .scrape_programs import get_programs
from .scrape_movies import get_movies
from .scrape_movie_schedules import get_movie_schedules

__all__ = ['JinbochoTheaterScraper']

class JinbochoTheaterScraper(ScraperInterface):
    def __init__(self, theater_url):
        self.theater_url = theater_url

    def scrape_programs(self):

        programs = get_programs(self.theater_url)
        return programs

    def scrape_movies(self, program_url):

        movies = get_movies(program_url)
        return movies
    
    def scrape_movie_schedules(self, program_url):

        movie_schedules = get_movie_schedules(program_url)
        return movie_schedules
