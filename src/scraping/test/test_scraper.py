import os
import json
from src.scraping.scraper_factory import ScraperFactory

def save_to_json(file_path, data):
    with open(file_path, 'w', encoding='UTF-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)
    print(f'save to {file_path}')

def test_scraper(theater_id, output_dirpath):

    scraper = ScraperFactory.get_scraper(theater_id)

    os.makedirs(output_dirpath, exist_ok=True)

    # プログラム情報を取得
    programs = scraper.scrape_programs()
    save_to_json(os.path.join(output_dirpath, 'programs.json'), programs)

    # 各プログラムの映画情報とスケジュール情報を取得
    for program in programs:
        program_url = program['program_url']
        # 映画情報を取得して保存
        movies = scraper.scrape_movies(program_url)
        save_to_json(os.path.join(output_dirpath, 'movies.json'), movies)

        # 映画のスケジュール情報を取得して保存
        movie_schedules = scraper.scrape_movie_schedules(program_url)
        save_to_json(os.path.join(output_dirpath, 'movie_schedules.json'), movie_schedules)
