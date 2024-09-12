import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from .util import get_soup, get_program_movie_list_url

__all__ = ['get_movies', 'get_movie_schedules']

def get_program_urls(theater_url):
    """
    メインページのURLから、上映プログラムのURL一覧を取得して返す
    """
    main_page_soup = get_soup(theater_url)
    div_tag = main_page_soup.find("div", {"class": "link_all"})
    if not div_tag:
        return []

    program_urls = []
    for a_tag in div_tag.find_all("a", href=lambda href: href and href.startswith("program/")):
        program_urls.append(urljoin(theater_url, a_tag["href"]))

    return program_urls

def get_program_id(program_url):
    """
    program_urlから、program_idを取得して返す
    """
    start_idx = program_url.index("program/") + len("program/")
    end_idx = program_url.index(".html")
    program_id = program_url[start_idx:end_idx]

    return program_id

def get_program_title(program_url):
    """
    タイトルがh3タグに囲まれていることを仮定し、program_urlから、プログラムのタイトルを返す
    """
    program_soup = get_soup(program_url)
    h3_tags = program_soup.find_all("h3")
    program_title = [h3_tag.text.replace("\n", " ").replace("\t", "") for h3_tag in h3_tags]
    program_title = " ".join(program_title)

    return program_title

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



def _get_program(program_url):

    # program_id = get_program_id(program_url)
    program_title = get_program_title(program_url)
    program_duration = get_program_duration(program_url)
    program_movie_list_url = get_program_movie_list_url(program_url)
    
    return {
        'title': program_title,
        'start_date': program_duration['start'],
        'end_date': program_duration['end'],
        'program_url': program_url,
        'program_movie_list_url': program_movie_list_url,
    }



def get_programs(theater_url):
    program_urls = get_program_urls(theater_url)

    programs = []
    for program_url in program_urls:
        program = _get_program(program_url)
        programs.append(program)

    return programs


def get_movie_tags(program_url):
    program_movie_list_url = get_program_movie_list_url(program_url)
    program_movie_list_soup = get_soup(program_movie_list_url)
    movie_tags = program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})

    return movie_tags

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

def get_movie_url(program_url, movie_id):
    program_movie_list_url = get_program_movie_list_url(program_url)
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

def get_movie(program_url, movie_tag):
    movie_id, movie_title = get_movie_id_and_title(movie_tag)
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
    movie_tags = get_movie_tags(program_url)
    for movie_tag in movie_tags:
        movie = get_movie(program_url, movie_tag)
        movies.append(movie)
    return movies

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