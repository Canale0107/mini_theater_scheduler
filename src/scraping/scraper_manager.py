from src.database.db_manager import get_db
from src.database.repositories.program_repository import ProgramRepository
from src.database.repositories.movie_repository import MovieRepository
from src.database.repositories.movie_schedule_repository import MovieScheduleRepository
from .scraper_factory import ScraperFactory


def scrape_and_save_data(theater_id):
    """
    渡されたスクレイパーを使ってプログラム情報と映画情報を取得し、データベースに保存する処理。
    """

    scraper = ScraperFactory.get_scraper(theater_id)

    # プログラム情報を取得
    programs = scraper.scrape_programs()

    with get_db() as db:
        for program_data in programs:
            # プログラム情報をデータベースに保存
            program = ProgramRepository.create_program(
                db=db,
                title=program_data['title'],
                start_date=program_data['start_date'],
                end_date=program_data['end_date'],
                program_url=program_data['program_url'],
                program_movie_list_url=program_data['program_movie_list_url'],
                theater_id=theater_id
            )
            
            # 映画情報を取得
            movies = scraper.scrape_movies(program_data['program_url'])
            # 映画のスケジュール情報を取得
            movie_schedules = scraper.scrape_movie_schedules(program_data['program_url'])
            
            # 映画情報をデータベースに保存
            for movie_data in movies:
                movie = MovieRepository.create_movie(
                    db=db,
                    program_id=program.id, # プログラムの外部キー
                    title=movie_data['title'],
                    synopsis=movie_data['synopsis'],
                    runtime=movie_data['runtime'],
                    type=movie_data['type'],
                    movie_url=movie_data['movie_url'],
                    staff=movie_data['staff']
                )
                

                for movie_schedule_data in movie_schedules:
                    if movie_schedule_data['movie_id'] == movie_data['movie_id']:
                        MovieScheduleRepository.create_movie_schedule(
                            db=db,
                            movie_id=movie.id,
                            start_datetime=movie_schedule_data['start_datetime']
                        )