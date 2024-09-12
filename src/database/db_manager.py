import os
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import text
from .models import Base

# 環境変数からデータベース接続情報を取得
DATABASE_URL = os.getenv("DATABASE_URL")

# データベース接続設定
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# データベースのリセット（データを削除しIDをリセット）
def reset_db():
    """ データベース内のすべてのテーブルをリセット（TRUNCATE） """
    with engine.connect() as conn:
        # TRUNCATE文を使用してすべてのテーブルのデータを削除し、IDをリセット
        conn.execute(text("""
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'TRUNCATE TABLE ' || quote_ident(r.tablename) || ' RESTART IDENTITY CASCADE';
            END LOOP;
        END $$;
        """))
        conn.commit()
        print("Database has been reset.")

# データベースの初期化（必要に応じて呼び出し）
def init_db():
    """ テーブルをデータベースに作成する """
    Base.metadata.create_all(bind=engine)

# コンテキストマネージャとしてセッションを管理
@contextmanager
def get_db():
    """ セッションを取得するジェネレーター """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()