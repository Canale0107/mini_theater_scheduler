import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

__all__ = ['get_movie_schedules']

def get_soup(url):
    response = requests.get(url)
    response.encoding = "Shift_JIS" 
    html_text = response.text
    soup = BeautifulSoup(html_text, "html.parser")
    return soup

def get_program_movie_list_url(program_url):
    """
    プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
    """

    program_movie_list_url = program_url.replace(".html", "_list.html")
    
    return program_movie_list_url

def get_movie_id_and_title(movie_tag):
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

def extract_date(pattern, text):
    """指定された正規表現パターンで日付を抽出"""
    match = re.search(pattern, text)
    if match:
        return match.groups()
    return None

def get_program_duration(program_url):
    """
    プログラムの上映期間を取得
    """
    program_soup = get_soup(program_url)
    schedule = program_soup.find("p", class_="schedule").text

    # 正規表現パターンを定義
    start_pattern = r"(\d+)年(\d+)月(\d+)日"
    end_patterns = [
        r"(〜|・)(\d+)年(\d+)月(\d+)日",
        r"(〜|・)(\d+)月(\d+)日",
        r"(〜|・)(\d+)日"
    ]

    # 開始日を抽出
    start_date = extract_date(start_pattern, schedule)
    if start_date:
        program_start_year, program_start_month, program_start_date = map(int, start_date)
        program_start_ymd = datetime(program_start_year, program_start_month, program_start_date).date()
    else:
        raise ValueError("開始日が見つかりません")

    # 終了日を抽出
    program_end_ymd = None
    for pattern in end_patterns:
        end_date = extract_date(pattern, schedule)
        if end_date:
            if len(end_date) == 4:  # 年月日が含まれるパターン
                program_end_year, program_end_month, program_end_date = map(int, end_date[1:])
            elif len(end_date) == 3:  # 月日が含まれるパターン
                program_end_year = program_start_ymd.year
                program_end_month, program_end_date = map(int, end_date[1:])
            else:  # 日のみが含まれるパターン
                program_end_year = program_start_ymd.year
                program_end_month = program_start_ymd.month
                program_end_date = int(end_date[1])
            program_end_ymd = datetime(program_end_year, program_end_month, program_end_date).date()
            break
    
    # 終了日が見つからなかった場合、開始日と同じにする
    if not program_end_ymd:
        program_end_ymd = program_start_ymd

    program_duration_dict = {
        "start": program_start_ymd.strftime("%Y-%m-%d"),
        "end": program_end_ymd.strftime("%Y-%m-%d")
    }

    return program_duration_dict

def get_movie_start_datetime_str_list(program_url, movie_tag):
    """
    上映開始日時のリストを取得
    """
    program_duration = get_program_duration(program_url)

    schedule_text = movie_tag.find("p", {"class": "data2_sche"}).text

    movie_start_datetime_str_list = [] # 特定の映画の{"start": 上映開始日時, "end": 上映終了日時)を格納するリストを初期化
    for line in schedule_text.split("\n"):

        match = re.search(r"(\d+)月(\d+)日（.+）(\d+):(\d+)", line)
        if match:
            month_str, day_str, time_hour_str, time_minute_str = match.groups()
            month = int(month_str)
            day = int(day_str)

            # 年はプログラムの上映期間から取得
            program_start_ymd_str = program_duration["start"]
            program_start_year = datetime.strptime(program_start_ymd_str, '%Y-%m-%d').year
            program_start_month = datetime.strptime(program_start_ymd_str, '%Y-%m-%d').month

            # 年を跨ぐプログラムに対応
            # 映画の上映月がプログラムの開始月より小さければ、映画の上映年はプログラムの開始年に+1したものにする
            if month < program_start_month:
                year = program_start_year + 1
            else:
                year = program_start_year

            # 上映開始時間
            movie_start_datetime = datetime(year, month, day, int(time_hour_str), int(time_minute_str))

            movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M")

            movie_start_datetime_str_list.append(movie_start_datetime_str)

    return movie_start_datetime_str_list

def get_movie_tags(program_url):
    program_movie_list_url = get_program_movie_list_url(program_url)
    program_movie_list_soup = get_soup(program_movie_list_url)
    movie_tags = program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})

    return movie_tags

def get_movie_schedules(program_url):
    movie_schedules = []
    movie_tags = get_movie_tags(program_url)
    for movie_tag in movie_tags:
        movie_id, movie_title = get_movie_id_and_title(movie_tag)
        movie_start_datetime_str_list = get_movie_start_datetime_str_list(program_url, movie_tag)
        for movie_start_datetime_str in movie_start_datetime_str_list:
            movie_schedules.append(
                {
                    'movie_id': movie_id,
                    'start_datetime': movie_start_datetime_str
                }
            )
    
    return movie_schedules