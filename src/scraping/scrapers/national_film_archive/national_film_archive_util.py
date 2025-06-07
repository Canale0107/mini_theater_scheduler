import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

__all__ = ['get_programs', 'get_movies', 'get_movie_schedules']

def _get_soup(url):

    # URLからHTMLを取得
    response = requests.get(url)
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    response.encoding = encoding
    return BeautifulSoup(response.content.decode('utf-8'), "html.parser")

def _get_program_urls(theater_url):
    """
    メインページから、上映プログラムのURLを取得する
    """

    main_page_soup = _get_soup(theater_url)
    h1_tag = main_page_soup.find("h1", string="開催中の上映")

    if h1_tag is None:
        print("開催中の上映セクションが見つかりませんでした")
        return []

    screening_link_tag = h1_tag.find_next("a")
    if screening_link_tag is None or "href" not in screening_link_tag.attrs:
        print("上映リンクが見つかりませんでした")
        return []

    screening_link = screening_link_tag["href"]
    program_urls = [screening_link]

    return program_urls
def _get_program_id(program_url):
    pattern = r"/(\w+)/$"
    match = re.search(pattern, program_url)
    if match:
        program_id = match.group(1)
    else:
        program_id = "unknown"
    return program_id

def _get_program_title(program_url):
    """
    プログラムタイトルがページタイトルに含まれることを仮定
    """
    program_soup = _get_soup(program_url)
    title_text = program_soup.title.string
    program_title = title_text.split(" | ")[0]

    return program_title

def _get_program_duration(program_url):
    """
    プログラムの上映期間を取得
    """

    program_soup = _get_soup(program_url)

    # 正規表現パターンを定義する
    pattern = r"(\d{4}).(\d{1,2}).(\d{1,2}) - (\d{4})?.?(\d{1,2})?.?(\d{1,2})?"

    # HTMLから日付を取得する
    schedule = program_soup.find("div", class_="clearfix mb10").text
    # 正規表現で日付を取得する
    program_date_matches = re.search(pattern, schedule)

    program_start_year = int(program_date_matches.group(1))
    program_start_month = int(program_date_matches.group(2)) if program_date_matches.group(2) is not None else 1
    program_start_day = int(program_date_matches.group(3)) if program_date_matches.group(3) is not None else 1

    program_end_year = int(program_date_matches.group(4)) if program_date_matches.group(4) is not None else program_start_year
    program_end_month = int(program_date_matches.group(5)) if program_date_matches.group(5) is not None else program_start_month
    program_end_day = int(program_date_matches.group(6)) if program_date_matches.group(6) is not None else program_start_day

    program_start_ymd = datetime(program_start_year, program_start_month, program_start_day).date()
    program_end_ymd = datetime(program_end_year, program_end_month, program_end_day).date()

    program_start_ymd_str = program_start_ymd.strftime("%Y-%m-%d")
    program_end_ymd_str = program_end_ymd.strftime("%Y-%m-%d")

    program_duration_dict = {"start": program_start_ymd_str, "end": program_end_ymd_str}

    return program_duration_dict

def _get_program_movie_list_url(program_url):
    """
    プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
    """

    program_movie_list_url = program_url
    
    return program_movie_list_url

def _get_program(program_url):
    program_id = _get_program_id(program_url)
    program_title = _get_program_title(program_url)
    program_duration = _get_program_duration(program_url)
    program_movie_list_url = _get_program_movie_list_url(program_url)

    return {
        'title': program_title,
        'start_date': program_duration['start'],
        'end_date': program_duration['end'],
        'program_url': program_url,
        'program_movie_list_url': program_movie_list_url,
    }

def get_programs(theater_url):
    program_urls = _get_program_urls(theater_url)
    programs = []
    for program_url in program_urls:
        program = _get_program(program_url)
        programs.append(program)

    return programs

def _get_movie_tags(program_url):

    program_movie_list_url = _get_program_movie_list_url(program_url)
    program_movie_list_soup = _get_soup(program_movie_list_url)
    
    # 入れ子になっているdivタグを取得しないように、find_allメソッドにrecursive=Falseを指定する
    movie_tags = program_movie_list_soup.find_all('div', {"class": "row row-15", "id":re.compile(r'ex-\d+')})
    return movie_tags

def _check_combination(movie_tag):
    # NFAJでは１つの上映で二つ以上の映画を上映することがあるらしい、その扱いをどうするか
    # それぞれを1つの映画として扱い、上映時間はうまく計算するのがいい
    # まずはそれを判別しなければならない
    # 上映時間のところに"計"が含まれているかどうかで判別

    is_combinated = False
    is_sub_movie = False

    movie_title = movie_tag.find('span', {"class": "ev-name"})
    movie_duration = movie_tag.find('small', {"class": "pl5 iblk"})

    if movie_title == None or movie_duration == None:
        # movie_tagはsub_movieのタグも再帰的に拾ってくるので、それの回避
        is_sub_movie = True

    else:
        movie_title_text = movie_title.text
        movie_duration_text = movie_duration.text
        # print(f'{movie_title_text=}') # for debug
        # print(f'{movie_duration_text=}') # for debug

        if "／" in movie_title_text or "計" in movie_duration_text:
            is_combinated = True
            # print('is_combinated') # for debug

    return is_combinated, is_sub_movie

def _get_movie_url(program_movie_list_url, movie_id):

    movie_url = f'{program_movie_list_url}#{movie_id}'

    return movie_url

def _get_sub_movies(program_url, movie_tag):

    program_movie_list_url = _get_program_movie_list_url(program_url)

    # movie_idを取得
    movie_id = movie_tag.get('id')
    # print(movie_id) # for debug
    movie_url = _get_movie_url(program_movie_list_url, movie_id)

    movie_start_datetime_str_list = []

    # それぞれのタイトル、上映時間、タイプ、制作年、スタッフ、あらすじを取得
    sub_movie_tag_list = movie_tag.find_all('div', {"class": "sub-event"})
    sub_movies = []
    sub_movie_start_datetime_str_list = movie_start_datetime_str_list.copy()
    for sub_movie_tag in sub_movie_tag_list:
        sub_movie_id = sub_movie_tag.find('div', {'class': 'row row-15'}).get('id')
        sub_movie_title = sub_movie_tag.find('span', {"class": "ev-name"}).text
        sub_movie_type_text = sub_movie_tag.find('small', {"class": "pl5"}).text
        sub_movie_staff_text = sub_movie_tag.find('p', {"class": "ev-meta"}).text
        sub_movie_timedelta_minute_str, sub_movie_type, sub_movie_staff = _get_movie_type_and_movie_staff(sub_movie_type_text, sub_movie_staff_text)

        sub_movie_synopsis = sub_movie_tag.find('div', {"class": "ev-more"}).text
        cast_dict = _get_cast_dict(sub_movie_staff)
        staff = '\u25C6'+ '\u25C6'.join(f"{k}: {v}" for k, v in cast_dict.items())

        runtime = sub_movie_timedelta_minute_str

        sub_movie = {
            'movie_id': sub_movie_id,
            'title': sub_movie_title,
            'synopsis': sub_movie_synopsis,
            'runtime': runtime,
            'type': sub_movie_type,
            'movie_url': movie_url,
            'staff': staff
        }
        sub_movies.append(sub_movie)

        # 次に連続して上映される映画の開始時刻のリストにする
        sub_movie_timedelta = timedelta(minutes=int(sub_movie_timedelta_minute_str.rstrip('分')))
        sub_movie_start_datetime_str_list = [(datetime.strptime(sub_movie_start_datetime_str, "%Y-%m-%d %H:%M")
                                            + sub_movie_timedelta).strftime("%Y-%m-%d %H:%M") 
                                            for sub_movie_start_datetime_str in sub_movie_start_datetime_str_list]

    return sub_movies

def _get_movie_type_and_movie_staff(movie_type_text, movie_staff_text):

    movie_production_year = None
    movie_production_company = None

    if movie_staff_text is not None:
        regex = r"(\d{4})（(.+?)）(.+)"
        match = re.search(regex, movie_staff_text)
        if match:
            movie_production_year = match.group(1)
            movie_production_company = match.group(2)
            movie_staff = match.group(3)
        else:
            movie_staff = movie_staff_text
    else:
        movie_staff = None

    regex = r"\((.+?)\)"
    match = re.search(regex, movie_type_text)
    if match:
        elements = match.group(1).split("・")
        sub_movie_timedelta_minute_str = elements[0].split("分")[0] + "分"
        other_elements = elements[1:]

    if movie_production_year and movie_production_company:
        movie_type = "/".join([movie_production_year, movie_production_company, *other_elements])
    else:
        if other_elements:
            movie_type = "/".join(other_elements)
        else:
            movie_type = ""


    return sub_movie_timedelta_minute_str, movie_type, movie_staff

def _get_cast_dict(movie_staff):
    cast_dict = {}
    pattern = r"（(.*?)\）([^（]*)"
    matches = re.findall(pattern, movie_staff)
    for key, value in matches:
        cast_dict[key] = value.strip()
    return cast_dict

def _get_movie(program_url, movie_tag):
    program_movie_list_url = _get_program_movie_list_url(program_url)

    # movie_idを取得
    movie_id = movie_tag.get('id')
    movie_url = _get_movie_url(program_movie_list_url, movie_id)

    # 上映開始日時、上映場所を取得
    movie_start_datetime_ul = movie_tag.find('ul', {"class": "list-inline"})
    movie_start_datetime_tag_list = movie_start_datetime_ul.select('li')

    movie_start_datetime_str_list = []
    place_list = []
    for movie_start_datetime_tag in movie_start_datetime_tag_list:
        date_text = movie_start_datetime_tag.find('span', {"class": "pr-day"}).text.split('(')[0]
        time_text = movie_start_datetime_tag.find('span', {"class": "pr-from"}).text.strip()
        place_text = movie_start_datetime_tag.find('span', {"class": "pr-place custom-place"}).text.strip()

        movie_start_date = datetime.strptime(date_text, "%Y年%m月%d日").date()
        movie_start_time = datetime.strptime(time_text, "%I:%M %p").time()
        movie_start_datetime = datetime.combine(movie_start_date, movie_start_time)
        movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M")
        movie_start_datetime_str_list.append(movie_start_datetime_str)

        place = place_text.lstrip('@')
        place_list.append(place)

    # タイトル、上映時間、タイプ、制作年、スタッフ、あらすじを取得
    movie_title = movie_tag.find('span', {"class": "ev-name"}).text
    movie_type_text = movie_tag.find('small', {"class": "pl5 iblk"}).text
    if movie_tag.find('p', {"class": "ev-meta"}) is not None:
        movie_staff_text = movie_tag.find('p', {"class": "ev-meta"}).text
    else:
        movie_staff_text = None
    movie_timedelta_minute_str, movie_type, movie_staff = _get_movie_type_and_movie_staff(movie_type_text, movie_staff_text)
    if movie_staff is not None:
        cast_dict = _get_cast_dict(movie_staff)
    else:
        cast_dict = {}

    synopsis = movie_tag.find('div', {"class": "ev-more"}).text
    
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

def _extract_movie_start_datetime_and_place(movie_tag):
    movie_start_datetime_ul = movie_tag.find('ul', {"class": "list-inline"})
    movie_start_datetime_tag_list = movie_start_datetime_ul.select('li')

    movie_start_datetime_str_list = []
    place_list = []
    for movie_start_datetime_tag in movie_start_datetime_tag_list:
        date_text = movie_start_datetime_tag.find('span', {"class": "pr-day"}).text.split('(')[0]
        time_text = movie_start_datetime_tag.find('span', {"class": "pr-from"}).text.strip()
        place_text = movie_start_datetime_tag.find('span', {"class": "pr-place custom-place"}).text.strip()

        movie_start_date = datetime.strptime(date_text, "%Y年%m月%d日").date()
        movie_start_time = datetime.strptime(time_text, "%I:%M %p").time()
        movie_start_datetime = datetime.combine(movie_start_date, movie_start_time)
        movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M")
        movie_start_datetime_str_list.append(movie_start_datetime_str)

        place = place_text.lstrip('@')
        place_list.append(place)

    return movie_start_datetime_str_list, place_list

def _get_sub_movie_schedules(program_url, movie_tag):

    # 共通の上映開始日時、上映場所を取得
    movie_start_datetime_str_list, place_list = _extract_movie_start_datetime_and_place(movie_tag)

    # サブ映画のタイトル、上映時間、タイプ、スタッフを取得
    sub_movie_tag_list = movie_tag.find_all('div', {"class": "sub-event"})
    sub_movie_schedules = []
    sub_movie_start_datetime_str_list = movie_start_datetime_str_list.copy()
    
    for sub_movie_tag in sub_movie_tag_list:
        sub_movie_id = sub_movie_tag.find('div', {'class': 'row row-15'}).get('id')
        sub_movie_title = sub_movie_tag.find('span', {"class": "ev-name"}).text
        sub_movie_type_text = sub_movie_tag.find('small', {"class": "pl5"}).text
        sub_movie_staff_text = sub_movie_tag.find('p', {"class": "ev-meta"}).text
        sub_movie_timedelta_minute_str, sub_movie_type, sub_movie_staff = _get_movie_type_and_movie_staff(sub_movie_type_text, sub_movie_staff_text)

        # 上映時間に基づいて次の上映時刻を計算
        sub_movie_timedelta = timedelta(minutes=int(sub_movie_timedelta_minute_str.rstrip('分')))
        sub_movie_start_datetime_str_list = [(datetime.strptime(sub_movie_start_datetime_str, "%Y-%m-%d %H:%M")
                                            + sub_movie_timedelta).strftime("%Y-%m-%d %H:%M") 
                                            for sub_movie_start_datetime_str in sub_movie_start_datetime_str_list]
        
        for sub_movie_start_datetime_str in sub_movie_start_datetime_str_list:
            sub_movie_schedules.append(
                {
                    'movie_id': sub_movie_id,
                    'start_datetime': sub_movie_start_datetime_str
                }
            )

    return sub_movie_schedules

def _get_movie_schedule(program_url, movie_tag):
    # movie_idを取得
    movie_id = movie_tag.get('id')

    # 上映開始日時、上映場所を取得
    movie_start_datetime_str_list, place_list = _extract_movie_start_datetime_and_place(movie_tag)

    movie_schedules = []
    for movie_start_datetime_str in movie_start_datetime_str_list:
        movie_schedules.append(
            {
                'movie_id': movie_id,
                'start_datetime': movie_start_datetime_str
            }
        )
    
    return movie_schedules

def get_movies(program_url):
    movies = []
    movie_tags = _get_movie_tags(program_url)
    for movie_tag in movie_tags:
        is_combinated, is_sub_movie = _check_combination(movie_tag)

        if not is_sub_movie:
            # 1つの上映で複数の映画をやる場合
            if is_combinated:
                sub_movies = _get_sub_movies(program_url, movie_tag)
                movies.extend(sub_movies)
            else:
                movie = _get_movie(program_url, movie_tag)
                movies.append(movie)
    return movies

def get_movie_schedules(program_url):
    movie_schedules = []
    movie_tags = _get_movie_tags(program_url)
    for movie_tag in movie_tags:
        is_combinated, is_sub_movie = _check_combination(movie_tag)

        if not is_sub_movie:
            # 1つの上映で複数の映画をやる場合
            if is_combinated:
                sub_movie_schedule = _get_sub_movie_schedules(program_url, movie_tag)
                movie_schedules.extend(sub_movie_schedule)
            else:
                movie_schedule = _get_movie_schedule(program_url, movie_tag)
                movie_schedules.extend(movie_schedule)
    
    return movie_schedules