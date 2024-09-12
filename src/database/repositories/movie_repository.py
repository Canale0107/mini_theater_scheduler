'''
映画情報の保存・取得ロジック
'''
from sqlalchemy.orm import Session
from src.database.models import Movie

class MovieRepository:
    @staticmethod
    def create_movie(db: Session, program_id: int, title: str, synopsis: str, runtime: str, type: str, movie_url: str, staff: str):
        new_movie = Movie(
            program_id=program_id,
            title=title,
            synopsis=synopsis,
            runtime=runtime,
            type=type,
            movie_url=movie_url,
            staff=staff
        )
        db.add(new_movie)
        db.commit()
        db.refresh(new_movie)  # 新しい映画のデータを返す
        return new_movie