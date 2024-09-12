from sqlalchemy.orm import Session
from src.database.models import MovieSchedule

class MovieScheduleRepository:
    @staticmethod
    def create_movie_schedule(db: Session, movie_id: int, start_datetime: str):
        new_movie_schedule= MovieSchedule(
            movie_id=movie_id,
            start_datetime=start_datetime
        )
        db.add(new_movie_schedule)
        db.commit()
        db.refresh(new_movie_schedule)
        return new_movie_schedule