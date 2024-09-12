import re
from datetime import datetime

from .utils import get_soup, get_program_movie_list_url


__all__ = ['get_movie_schedules']


def get_movie_id_and_title(movie_tag):
    """
    映画のIDとタイトルを取得
    """
    movie_title_with_number = movie_tag.find("div", {"class": "data2_title"}).text.strip().replace("\t", "")
    movie_title_with_number = re.sub(r'\xa0+', ' ', movie_title_with_number)  # スペースを半角スペースに

    title_match = re.match(r"(\d+)[.]\s+(.*)", movie_title_with_number)
    if title_match:
        return title_match.groups()
    raise ValueError("映画のIDとタイトルが見つかりません")


def extract_date(pattern, text):
    """
    指定した正規表現パターンで日付を抽出
    """
    match = re.search(pattern, text)
    return match.groups() if match else None


def parse_program_duration(schedule):
    """
    プログラムの上映期間を抽出
    """
    start_pattern = r"(\d+)年(\d+)月(\d+)日"
    end_patterns = [
        r"(〜|・)(\d+)年(\d+)月(\d+)日",
        r"(〜|・)(\d+)月(\d+)日",
        r"(〜|・)(\d+)日"
    ]

    # 開始日を取得
    start_date = extract_date(start_pattern, schedule)
    if not start_date:
        raise ValueError("開始日が見つかりません")
    
    program_start_year, program_start_month, program_start_day = map(int, start_date)
    program_start_date = datetime(program_start_year, program_start_month, program_start_day).date()

    # 終了日を取得
    for pattern in end_patterns:
        end_date = extract_date(pattern, schedule)
        if end_date:
            if len(end_date) == 4:  # 年月日が含まれる場合
                program_end_year, program_end_month, program_end_day = map(int, end_date[1:])
            elif len(end_date) == 3:  # 月日が含まれる場合
                program_end_year = program_start_year
                program_end_month, program_end_day = map(int, end_date[1:])
            else:  # 日のみの場合
                program_end_year = program_start_year
                program_end_month = program_start_month
                program_end_day = int(end_date[1])
            return {
                "start": program_start_date.strftime("%Y-%m-%d"),
                "end": datetime(program_end_year, program_end_month, program_end_day).strftime("%Y-%m-%d")
            }
    
    # 終了日が見つからなかった場合、開始日を終了日に設定
    return {"start": program_start_date.strftime("%Y-%m-%d"), "end": program_start_date.strftime("%Y-%m-%d")}


def get_program_duration(program_url):
    """
    プログラムの上映期間を取得
    """
    program_soup = get_soup(program_url)
    schedule_text = program_soup.find("p", class_="schedule").text
    return parse_program_duration(schedule_text)


def extract_movie_schedule(schedule_text, program_start_year, program_start_month):
    """
    映画の上映スケジュールを抽出
    """
    movie_start_datetime_list = []
    for line in schedule_text.split("\n"):
        match = re.search(r"(\d+)月(\d+)日（.+）(\d+):(\d+)", line)
        if match:
            month, day, hour, minute = map(int, match.groups())
            # 年末の場合の対策
            movie_year = program_start_year if month >= program_start_month else program_start_year + 1
            movie_start_datetime = datetime(movie_year, month, day, hour, minute)
            movie_start_datetime_list.append(movie_start_datetime.strftime("%Y-%m-%d %H:%M"))
    return movie_start_datetime_list


def get_movie_start_datetime_str_list(program_url, movie_tag):
    """
    映画の上映開始日時のリストを取得
    """
    program_duration = get_program_duration(program_url)
    program_start_year = int(program_duration["start"].split("-")[0])
    program_start_month = int(program_duration["start"].split("-")[1])
    schedule_text = movie_tag.find("p", class_="data2_sche").text
    return extract_movie_schedule(schedule_text, program_start_year, program_start_month)


def get_movie_tags(program_url):
    """
    映画のタグ一覧を取得
    """
    program_movie_list_soup = get_soup(get_program_movie_list_url(program_url))
    return program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})


def get_movie_schedules(program_url):
    """
    プログラムに紐づく映画スケジュールを取得
    """
    movie_schedules = []
    for movie_tag in get_movie_tags(program_url):
        movie_id, movie_title = get_movie_id_and_title(movie_tag)
        movie_start_datetime_list = get_movie_start_datetime_str_list(program_url, movie_tag)
        for movie_start_datetime in movie_start_datetime_list:
            movie_schedules.append({
                'movie_id': movie_id,
                'start_datetime': movie_start_datetime
            })
    return movie_schedules
