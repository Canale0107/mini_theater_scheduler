from src.scraping.scraper_interface import ScraperInterface
from . import cinemavera_shibuya_util

class CinemaveraShibuyaScraper(ScraperInterface):
    def __init__(self, theater_url):
        self.theater_url = theater_url

    def scrape_programs(self):

        programs = cinemavera_shibuya_util.get_programs(self.theater_url)
        return programs

    def scrape_movies(self, program_url):

        movies = cinemavera_shibuya_util.get_movies(program_url)
        return movies
    
    def scrape_movie_schedules(self, program_url):

        movie_schedules = cinemavera_shibuya_util.get_movie_schedules(self.theater_url, program_url)
        return movie_schedules