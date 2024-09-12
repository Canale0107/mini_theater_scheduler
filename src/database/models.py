from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# ベースクラスを作成
Base = declarative_base()

# Theatersテーブルの定義
class Theater(Base):
    __tablename__ = 'theaters'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    name_en = Column(String(255), nullable=False)
    url = Column(String(255))
    location = Column(String(255))

    # リレーション定義（例としてProgramsと紐づけ）
    programs = relationship("Program", back_populates="theater")

# Programsテーブルの定義
class Program(Base):
    __tablename__ = 'programs'
    
    id = Column(Integer, primary_key=True)
    theater_id = Column(Integer, ForeignKey('theaters.id'))
    title = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    program_url = Column(String(255))
    program_movie_list_url = Column(String(255))
    
    # リレーション
    theater = relationship("Theater", back_populates="programs")
    movies = relationship("Movie", back_populates="program")

# Moviesテーブルの定義
class Movie(Base):
    __tablename__ = 'movies'
    id = Column(Integer, primary_key=True)
    program_id = Column(Integer, ForeignKey('programs.id'), nullable=False)
    title = Column(String(255), nullable=False)
    synopsis = Column(Text)
    runtime = Column(String(20))
    type = Column(String(50))
    movie_url = Column(String(255))
    staff = Column(Text)  # スタッフ情報を単一の文字列として保存

    # リレーション
    program = relationship("Program", back_populates="movies")
    movie_schedules = relationship("MovieSchedule", back_populates="movies")

class MovieSchedule(Base):
    __tablename__ = 'movie_schedule'
    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer, ForeignKey('movies.id'), nullable=False)
    start_datetime = Column(DateTime)

    # リレーション
    movies = relationship("Movie", back_populates="movie_schedules")