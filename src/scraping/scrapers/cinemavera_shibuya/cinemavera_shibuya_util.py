import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import Levenshtein

__all__ = ['get_programs', 'get_movies', 'get_movie_scheudles']

def _get_soup(url):
    # URLからHTMLを取得
    response = requests.get(url)
    # エンコーディングを自動で判定し、文字コードを設定する
    encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
    response.encoding = encoding

    soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")

    return soup

def _get_program_urls(theater_url):
    program_urls = []
    program_urls.append(urljoin(theater_url, 'programs.html'))
    program_urls.append(urljoin(theater_url, 'preview.html'))
    
    return program_urls

def _get_program_title(program_url):
    """
    タイトルがh2タグに囲まれていることを仮定
    """
    program_soup = _get_soup(program_url)
    program_title = program_soup.find('h2').text

    return program_title

def _get_program_duration(program_url):
    """
    プログラムの上映期間を取得
    """

    program_soup = _get_soup(program_url)

    schedule_tag = program_soup.find('li', {'class': 'schedule'})
    schedule_text = schedule_tag.find('h4').text

    program_start_date, program_end_date = schedule_text.split(' ～ ')
    program_start_date = datetime.strptime(program_start_date, '%Y/%m/%d').strftime('%Y-%m-%d')
    program_end_date = datetime.strptime(program_end_date, '%Y/%m/%d').strftime('%Y-%m-%d')

    program_duration_dict = {"start": program_start_date, "end": program_end_date}

    return program_duration_dict

def _get_program_movie_list_url(program_url):
    """
    シネマヴェーラの場合、program_movie_list_url == program_url
    """
    
    return program_url

def _get_program(program_url):
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
    movie_tags = program_movie_list_soup.find_all('ul', {'class': 'films', 'id': re.compile(r'^id\d+$')})

    return movie_tags

def _get_movie_id_and_title(movie_tag):
    # 映画のIDを取得
    movie_id_text = movie_tag.get('id') # 例："id50:
    match = re.search(r"id(\d+)", movie_id_text)
    if match:
        movie_id = match.group(1)

    # 映画のタイトルを取得
    movie_title_with_timedelta = movie_tag.find('h3').text

    match = re.search(r'『(.+)（\d+分', movie_title_with_timedelta)
    if match:
        movie_title = match.group(1)

    # movie_title_with_numberに”／サイレント"が含まれることがある
    match = re.search(r'／(.*)）』', movie_title_with_timedelta)
    if match:
        other_info = match.group(1)
    else:
        other_info = ""

    return movie_id, movie_title, other_info

def _get_movie_url(program_movie_list_url, movie_id):

    movie_url = f'{program_movie_list_url}#id{movie_id}'

    return movie_url

def _get_movie_type(movie_text_tag, other_info):
    """
    映画タイプを取得
    神保町シアターの場合、
        制作年/製作会社/白黒orカラー/上映時間
    などの情報
    """

    movie_text = movie_text_tag.text

    # 公開年の取得
    year_start = movie_text.find('公開：') + len('公開：')
    year_end = movie_text.find('年', year_start)
    year = movie_text[year_start:year_end]

    if other_info != "":
        movie_type = f"{year}年/{other_info}"
    else:
        movie_type = f"{year}年"

    return movie_type

def _get_cast_dict(movie_text_tag):
    """
    キャストのリストを取得
    """
    movie_text = movie_text_tag.text
    # 監督の取得
    director_start = movie_text.find('監督：') + len('監督：')
    director_end = movie_text.find('\n', director_start)
    director = movie_text[director_start:director_end]

    # 出演者の取得
    cast_start = movie_text.find('出演：') + len('出演：')
    cast_end = movie_text.find('\n', cast_start)
    cast = movie_text[cast_start:cast_end]

    cast_dict = {"監督": director, "出演": cast}

    return cast_dict

def _get_synopsis(movie_text_tag):
    """
    あらすじを取得
    """
    # 出演者がいないドキュメンタリーがあるので[5]はダメ、最後にコピーライトが入ることがあるので[-1]もだめ、
    text_split = movie_text_tag.text.split('\n')

    # 以下のコードだと、あらすじの書き出しが「公開」、「監督」、「出演」の時に動かない可能性がある
    # 出演者がないドキュメント映画であらすじが「出演〜」だとまずい
    flags = [False, False]
    synopsis = ""
    for text in text_split:
        #print(text)
        if text == "":
            #print("pass")
            pass
        elif text.startswith("公開"):
            #print("pass")
            flags[0] = True
        elif text.startswith("監督") and flags[0]:
            #print("pass")
            flags[1] = True
        elif text.startswith("出演") and flags[1]:
            #print("pass")
            pass
        else: 
            #print(synopsis)
            synopsis = text
            break

    return synopsis

def _format_timedelta(timedelta):
    total_sec = timedelta.total_seconds()
    
    minutes = total_sec // 60

    # total time
    return f'{int(minutes)}分'


def _get_movie_timedelta_minute_str(movie_tag):

    movie_title_with_timedelta = movie_tag.find('h3').text

    pattern = r'（(\d+)分'
    match = re.search(pattern, movie_title_with_timedelta)

    if match:
        minutes = int(match.group(1))
        movie_timedelta = timedelta(minutes=minutes)
    
    movie_timedelta_minute_str = _format_timedelta(movie_timedelta)

    return movie_timedelta_minute_str

def _get_movie(program_url, movie_tag):
    program_movie_list_url = _get_program_movie_list_url(program_url)

    movie_id, movie_title, other_info = _get_movie_id_and_title(movie_tag)
    movie_url = _get_movie_url(program_movie_list_url, movie_id)

    # 映画のメタ情報を取得
    movie_text_tag = movie_tag.find("li", {"class": "txt"})

    # 映画タイプを取得
    movie_type = _get_movie_type(movie_text_tag, other_info)

    # キャストを取得
    cast_dict = _get_cast_dict(movie_text_tag)

    # あらすじを取得
    synopsis = _get_synopsis(movie_text_tag)

    # 映画の上映時間を取得
    movie_timedelta_minute_str = _get_movie_timedelta_minute_str(movie_tag)

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

def _get_movie_start_datetime_str_list(schedule_tag, program_duration, movies):
    """
    上映開始日時のリストを取得
    スケジュールがたまに誤字ってることがあるので、その場合はレーベンシュタイン距離が最も近いものを採用する
    例：
        正：「太陽は光り輝く」　誤：「太陽は光輝く」
        正：「栄光何するものぞ」　誤：「栄光なにするものぞ」
    半角カッコと全角カッコも入り乱れている
    """
    rows = schedule_tag.find_all('tr')

    # 月の初期値をNoneに設定
    month = None
    movie_schedule_list = []

    for row in rows:
        # 日付を取得
        date_tag = row.find(class_='day')
        date_text = date_tag.text.strip()

        # 月が書いてある場合は更新する
        if '/' in date_text:
            month_date_str = date_text
            month_str = date_text.split('/')[0]
        # 月が書いていない場合は前の行の月を用いる
        else:
            month_date_str = month_str + '/' + date_text

        month, date = map(int, month_date_str.split("/"))

        # 年はプログラムの上映期間から取得
        program_start_ymd_str = program_duration["start"]
        program_start_year = datetime.strptime(program_start_ymd_str, '%Y-%m-%d').year
        program_start_month = datetime.strptime(program_start_ymd_str, '%Y-%m-%d').month

        # 年を跨ぐプログラムに対応
        if month < program_start_month:
            year = program_start_year + 1
        else:
            year = program_start_year

        # 上映スケジュールを取得
        time_tags = row.find_all(class_='time')
        film_tags = row.find_all(class_='film')

        for time_tag, film_tag in zip(time_tags, film_tags):
            time_text = time_tag.text.strip()
            film_text = film_tag.text.strip()

            if time_text == "":
                continue
            else:
                match = re.match(r"(\d+):(\d+).*", time_text)
                if match:
                    hour = int(match.group(1))
                    minute = int(match.group(2))

                movie_start_datetime = datetime(year, month, date, hour, minute)
                movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M")
                
                if film_text != "" and film_text != "\n":
                    is_matched = False

                    # 映画名から余計な情報を削除（例：「麦秋(74分)」→「麦秋」）
                    film_text_clean = re.sub(r"[（(].*?[)）]", "", film_text).strip()

                    for movie in movies:
                        # 邦題と原題の対策
                        if movie["title"].split(" ")[0] in film_text_clean:
                            movie_schedule_list.append({
                                'movie_id': movie['movie_id'],
                                'start_datetime': movie_start_datetime_str
                            })
                            is_matched = True
                            break

                    if not is_matched:
                        # 一致する映画が一つも見つからなかった場合
                        target_string = film_text_clean.split(" ")[0]
                        min_distance = len(target_string)
                        closest_movie = None
                        for movie in movies:
                            distance = Levenshtein.distance(target_string, movie["title"].split(" ")[0])
                            if distance < min_distance:
                                min_distance = distance
                                closest_movie = movie

                        if closest_movie:
                            movie_schedule_list.append({
                                'movie_id': closest_movie['movie_id'],
                                'start_datetime': movie_start_datetime_str
                            })
                        else:
                            print(f"正しく読み取れませんでした：{target_string}")

    return movie_schedule_list


def get_movie_schedules(theater_url, program_url):

    movie_schedules = []

    movie_tags = _get_movie_tags(program_url)
    link = movie_tags[0].find('a', {'class': 'linkbutton'})['href']
    schedule_table_url = urljoin(theater_url, link)
    schedule_table_soup = _get_soup(schedule_table_url)
    schedule_tag = schedule_table_soup.find("table", {"class": "pctime"})

    program_duration = _get_program_duration(program_url)

    movies = get_movies(program_url)

    movie_schedules = _get_movie_start_datetime_str_list(schedule_tag, program_duration, movies)

    return movie_schedules