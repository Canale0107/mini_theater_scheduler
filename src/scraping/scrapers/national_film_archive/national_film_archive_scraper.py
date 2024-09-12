from src.scraping.scraper_interface import ScraperInterface
from . import national_film_archive_util

__all__ = ['NationalFilmArchiveScraper']

class NationalFilmArchiveScraper(ScraperInterface):
    def __init__(self, base_url):
        self.base_url = base_url

    def scrape_programs(self):

        programs = national_film_archive_util.get_programs(self.base_url)
        return programs

    def scrape_movies(self, program_url):

        movies = national_film_archive_util.get_movies(program_url)
        return movies
    
    def scrape_movie_schedules(self, program_url):

        movie_schedules = national_film_archive_util.get_movie_schedules(program_url)
        return movie_schedules
