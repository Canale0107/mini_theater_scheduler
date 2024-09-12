from src.scraping.scrapers.jinbocho_theater.jinbocho_theater_scraper import JinbochoTheaterScraper
from src.scraping.scrapers.cinemavera_shibuya.cinemavera_shibuya_scraper import CinemaveraShibuyaScraper
from src.scraping.scrapers.national_film_archive.national_film_archive_scraper import NationalFilmArchiveScraper
from src.scraping.utils.get_theater_info import get_theater_url, get_theater_name_en


class ScraperFactory:
    @staticmethod
    def get_scraper(theater_id):
        """
        与えられた映画館のIDに基づいて適切なスクレイパーインスタンスを返すファクトリメソッド。
        """

        theater_name_en = get_theater_name_en(theater_id)
        theater_url = get_theater_url(theater_id)

        match theater_name_en:
            case "Jinbocho Theater":
                return JinbochoTheaterScraper(theater_url)
            case "Cinemavera Shibuya":
                return CinemaveraShibuyaScraper(theater_url)
            case "National Film Archive":
                return NationalFilmArchiveScraper(theater_url)
            case _:
                raise ValueError(f"Unsupported theater id: {theater_id}")