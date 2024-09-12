from abc import ABC, abstractmethod


class ScraperInterface(ABC):
    @abstractmethod
    def scrape_programs(self, theater_url):
        """
        プログラム情報をスクレイピングする抽象メソッド。
        各映画館のスクレイピングクラスで実装する必要がある。
        """
    
    @abstractmethod
    def scrape_movies(self, program_url):
        """
        プログラムに関連する映画情報をスクレイピングする抽象メソッド。
        各映画館のスクレイピングクラスで実装する必要がある。
        """

    @abstractmethod
    def scrape_movie_schedules(self, program_url):
        """
        映画の上映時間をスクレイピングする抽象メソッド。
        各映画館のスクレイピングクラスで実装する必要がある。
        """