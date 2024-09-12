import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

__all__ = ['get_movies']

def _get_soup(url):
    response = requests.get(url)
    response.encoding = "Shift_JIS" 
    html_text = response.text
    soup = BeautifulSoup(html_text, "html.parser")
    return soup

def _get_program_movie_list_url(program_url):
    """
    プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
    """

    program_movie_list_url = program_url.replace(".html", "_list.html")
    
    return program_movie_list_url

def _get_movie_tags(program_url):
    program_movie_list_url = _get_program_movie_list_url(program_url)
    program_movie_list_soup = _get_soup(program_movie_list_url)
    movie_tags = program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})

    return movie_tags

def _get_movie_id_and_title(movie_tag):
    # 映画のタイトルを取得
    movie_title_with_number = movie_tag.find("div", {"class": "data2_title"}).text.replace("\n", "").replace("\t", "")
    # タイトル内のスペースを半角スペースに置換
    movie_title_with_number = re.sub(r'\xa0+', ' ', movie_title_with_number)

    # 映画のIDとタイトルを取得
    title_match = re.match(r"(\d+)[.]\s+(.*)", movie_title_with_number)
    if title_match:
        movie_id = title_match.group(1)
        movie_title = title_match.group(2)

    return movie_id, movie_title

def get_movie_url(program_url, movie_id):
    program_movie_list_url = _get_program_movie_list_url(program_url)
    movie_url = f'{program_movie_list_url}#movie{movie_id.zfill(2)}'

    return movie_url

def get_movie_type(type_tag):
    """
    映画タイプを取得
    神保町シアターの場合、
        制作年/製作会社/白黒orカラー/上映時間
    などの情報
    """

    movie_type_list = type_tag.text.split(u'\uff0f') # 全角スラッシュで区切られていることを仮定
    movie_type = "/".join(movie_type_list[:-1]) # 上映時間は除く(DRY)

    return movie_type

def get_cast_dict(cast_tag):
    """
    キャストの辞書を取得
    """
    cast_list = cast_tag.text.lstrip("■").split("■")
    cast_dict = {}
    for cast in cast_list:
        work, name = cast.split(u'\uff1a', 1) # 全角コロンでsplit
        cast_dict[work] = name

    return cast_dict

def get_synopsis(synopsis_tag):
    """
    あらすじを取得
    """
    synopsis = synopsis_tag.text
    return synopsis

def format_timedelta(movie_timedelta):
    total_sec = movie_timedelta.total_seconds()
    
    minutes = total_sec // 60

    # total time
    return f'{int(minutes)}分'

def get_movie_timedelta_minute_str(type_tag):
    type_text = type_tag.text
    # 上映時間を取得
    timedelta_hour_match = re.search(r'(\d+)時間', type_text)
    movie_timedelta_hour = timedelta(hours = 0)
    timedelta_minute_match = re.search(r'(\d+)分', type_text)
    movie_timedelta_minute = timedelta(minutes = 0)

    if timedelta_hour_match:
        movie_hour = int(timedelta_hour_match.group(1))
        movie_timedelta_hour += timedelta(hours = movie_hour)
    if timedelta_minute_match:
        movie_minute = int(timedelta_minute_match.group(1))
        movie_timedelta_minute += timedelta(minutes = movie_minute)
        
    movie_timedelta = movie_timedelta_hour + movie_timedelta_minute

    movie_timedelta_minute_str = format_timedelta(movie_timedelta)

    return movie_timedelta_minute_str


def _get_movie(program_url, movie_tag):
    movie_id, movie_title = _get_movie_id_and_title(movie_tag)
    movie_url = get_movie_url(program_url, movie_id)

    type_tag, cast_tag, synopsis_tag = movie_tag.find_all("p", {"class": "data2_text"})

    movie_type = get_movie_type(type_tag)
    cast_dict = get_cast_dict(cast_tag)
    synopsis = get_synopsis(synopsis_tag)

    movie_timedelta_minute_str = get_movie_timedelta_minute_str(type_tag)

    runtime = movie_timedelta_minute_str
    staff = '\u25C6'+ '\u25C6'.join(f"{k}: {v}" for k, v in cast_dict.items())

    return {
        'movie_id': movie_id,
        'title': movie_title,
        'synopsis': synopsis,
        'runtime': runtime,
        'type': movie_type,
        'movie_url': movie_url,
        'staff': staff
    }

def get_movies(program_url):
    movies = []
    movie_tags = _get_movie_tags(program_url)
    for movie_tag in movie_tags:
        movie = _get_movie(program_url, movie_tag)
        movies.append(movie)
    return movies
