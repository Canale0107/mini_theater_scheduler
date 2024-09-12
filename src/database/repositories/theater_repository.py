from sqlalchemy.orm import Session
from src.database.models import Theater

class TheaterRepository:
    @staticmethod
    def create_theater(db: Session, id: int, name: str, name_en: str, url: str, location: str):
        """ 映画館情報をデータベースに保存するメソッド """
        # 映画館が既にデータベースに存在するか確認
        existing_theater = db.query(Theater).filter_by(name=name).first()
        if existing_theater:
            return existing_theater  # 既存の映画館を返す
        
        # 新しい映画館をデータベースに追加
        new_theater = Theater(
            id=id,
            name=name,
            name_en=name_en,
            url=url,
            location=location
        )
        db.add(new_theater)
        db.commit()
        db.refresh(new_theater)  # 新しい映画館のデータを返す
        return new_theater