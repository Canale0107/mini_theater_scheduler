'''
プログラム情報の保存・取得ロジック
'''
from sqlalchemy.orm import Session
from src.database.models import Program

class ProgramRepository:
    @staticmethod
    def create_program(db: Session, title: str, start_date, end_date, program_url: str, program_movie_list_url: str, theater_id: int):
        new_program = Program(
            theater_id=theater_id,
            title=title,
            start_date=start_date,
            end_date=end_date,
            program_url=program_url,
            program_movie_list_url=program_movie_list_url
        )
        db.add(new_program)
        db.commit()
        db.refresh(new_program)  # 新しいプログラムのデータを返す
        return new_program