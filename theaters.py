import os
import re
import json
import requests
from datetime import date, datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlsplit, urlunsplit
from theater_class import Theater, Program, Movie

# TODO: 各映画館クラスを一つのファイルにする


# TODO: とりあえずscheduler以外を個人のgithubにpushする
# TODO: loggerを作る

# Webページの仕様が変わったら、アンダーバーから始まるメソッドのいずれかを更新する必要がある

class Jinbocho_Theater(Theater):
    def __init__(self):
        super().__init__()

    def scrape_to_be_informed_theater_object(self):
        """
        自分に情報を詰めるために、Webスクレイピングを行う
        このメソッドは映画館ごとに設計する必要がある
        """
        # self.theater_location = self._get_theater_location()
        # それぞれのプログラムページからの情報を集める
        program_urls = self._get_program_urls()
        program_object_list = self._get_program_object_list(program_urls)
        self.program_object_list = program_object_list
    
    # 以下、この映画館のホームページに特化したプライベートメソッド
    def _get_program_urls(self):
        """
        メインページから、上映プログラムのURLを取得する
        """

        main_page_soup = self._get_soup(self.theater_url)

        # <div class="link_all">タグを取得
        div_tag = main_page_soup.find("div", {"class": "link_all"})

        # <div class="link_all">タグから、プログラムへのURLを取得
        a_tags = div_tag.find_all("a", href=lambda href: href and href.startswith("program/"))

        program_urls = []
        for a_tag in a_tags:
            program_urls.append(urljoin(self.theater_url, a_tag["href"]))
        
        return program_urls

    def _get_program_object_list(self, program_urls):
        """
        program_objectを、プログラムの数分集めたリストを取得する
        """
        program_object_list = []
        for program_url in program_urls:

            program_object = self._get_program_object(program_url)
            program_object_list.append(program_object)

        return program_object_list

    def _get_program_object(self, program_url):
        """
        program_urlのprogram_objectを取得する
        """

        # プログラムIDを取得
        program_id = self._get_program_id(program_url)

        # プログラムのタイトルを取得
        program_soup = self._get_soup(program_url)
        program_title = self._get_program_title(program_soup)

        # プログラムの上映期間を取得
        program_duration = self._get_program_duration(program_soup)

        # プログラムの上映映画一覧ページのURLを取得
        program_movie_list_url = self._get_program_movie_list_url(program_url)

        # プログラム内の映画オブジェクトのリストを取得
        movie_object_list = self._get_movie_object_list(program_movie_list_url, program_duration)

        program_object = Program(program_id = program_id, 
                                program_title = program_title, 
                                program_duration=program_duration,  
                                program_url = program_url,
                                program_movie_list_url = program_movie_list_url, 
                                movie_object_list = movie_object_list)

        return program_object

    def _get_program_id(self, program_url):
        start_idx = program_url.index("program/") + len("program/")
        end_idx = program_url.index(".html")
        program_id = program_url[start_idx:end_idx]

        return program_id

    def _get_program_title(self, program_soup):
        """
        タイトルがh3タグに囲まれていることを仮定
        """
        h3_tags = program_soup.find_all("h3")
        program_title = [h3_tag.text.replace("\n", " ").replace("\t", "") for h3_tag in h3_tags]
        program_title = " ".join(program_title)

        return program_title

    def _get_program_duration(self, program_soup):
        """
        プログラムの上映期間を取得
        """

        # 正規表現パターンを定義する
        start_pattern = r"(\d+)年(\d+)月(\d+)日"

        # HTMLから日付を取得する
        schedule = program_soup.find("p", class_="schedule").text
        # 正規表現で日付を取得する
        program_start_date_matches = re.search(start_pattern, schedule)

        # 開始日をdatetimeオブジェクトとして取得する
        program_start_year = int(program_start_date_matches.group(1))
        program_start_month = int(program_start_date_matches.group(2))
        program_start_date = int(program_start_date_matches.group(3))
        program_start_ymd = datetime(program_start_year, program_start_month, program_start_date).date()
        
        #「〜xx年xx月xx日」、「・xx年xx月xx日」
        end_pattern1 = r"(〜|・)(\d+)年(\d+)月(\d+)日"
        # 「〜xx月xx日」、「・xx年xx月xx日」
        end_pattern2 = r"(〜|・)(\d+)月(\d+)日"
        #「〜xx日」、「・xx日」
        end_pattern3 = r"(〜|・)(\d+)日"

        # end_pattern1、end_pattern2、end_pattern3のいずれかにマッチするテキストが存在するかどうかを確認する
        program_end_date_matches1 = re.search(end_pattern1, schedule)
        program_end_date_matches2 = re.search(end_pattern2, schedule)
        program_end_date_matches3 = re.search(end_pattern3, schedule)

        if program_end_date_matches1:
            program_end_year = int(program_end_date_matches1.group(2))
            program_end_month = int(program_end_date_matches1.group(3))
            program_end_date = int(program_end_date_matches1.group(4))
        elif program_end_date_matches2:
            program_end_year = program_start_ymd.year
            program_end_month = int(program_end_date_matches2.group(2))
            program_end_date = int(program_end_date_matches2.group(3))
        elif program_end_date_matches3:
            program_end_year = program_start_ymd.year
            program_end_month = program_start_ymd.month
            program_end_date = int(program_end_date_matches3.group(2))
        else:
            program_end_year = program_start_ymd.year
            program_end_month = program_start_ymd.month
            program_end_date = program_start_ymd.date

        program_end_ymd = datetime(program_end_year, program_end_month, program_end_date).date()

        program_start_ymd_str = program_start_ymd.strftime("%Y-%m-%d")
        program_end_ymd_str = program_end_ymd.strftime("%Y-%m-%d")

        program_duration_dict = {"start": program_start_ymd_str, "end": program_end_ymd_str}

        return program_duration_dict
    
    def _get_program_movie_list_url(self, program_url):
        """
        プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
        """

        program_movie_list_url = program_url.replace(".html", "_list.html")
        
        return program_movie_list_url

    def _get_movie_object_list(self, program_movie_list_url, program_duration):
        movie_object_list = []
        program_movie_list_soup = self._get_soup(program_movie_list_url)
        movie_tags = self._get_movie_tags(program_movie_list_soup)
        for movie_tag in movie_tags:

            movie_object = self._get_movie_object(program_movie_list_url, program_duration, movie_tag)
            movie_object_list.append(movie_object)

        return movie_object_list

    def _get_movie_tags(self, program_movie_list_soup):

        movie_tags = program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})

        return movie_tags

    def _get_movie_object(self, program_movie_list_url, program_duration , movie_tag):

        movie_id, movie_title = self._get_movie_id_and_title(movie_tag)
        movie_url = self._get_movie_url(program_movie_list_url, movie_id)

        # print(movie_title) # for debug

        # 映画のメタ情報を取得
        type_tag, cast_tag, synopsis_tag = movie_tag.find_all("p", {"class": "data2_text"})

        # 映画タイプを取得
        movie_type = self._get_movie_type(type_tag)

        # キャストを取得
        cast_dict = self._get_cast_dict(cast_tag)

        # あらすじを取得
        movie_synopsis = self._get_synopsis(synopsis_tag)

        # 映画の上映時間を取得
        movie_timedelta_minute_str = self._get_movie_timedelta_minute_str(type_tag)

        # 上映開始日時のリストを取得
        movie_start_datetime_str_list = self._get_movie_start_datetime_str_list(program_duration, movie_tag)
            
        # Movieクラスのオブジェクトを作成。これをリスト化して、programオブジェクトに渡す
        movie_object = Movie(movie_title = movie_title, 
                            movie_id = movie_id, 
                            movie_url = movie_url,
                            movie_timedelta_minute_str = movie_timedelta_minute_str, 
                            movie_type = movie_type, 
                            movie_staff = cast_dict, 
                            movie_synopsis = movie_synopsis, 
                            movie_start_datetime_str_list = movie_start_datetime_str_list)

        return movie_object

    def _get_movie_type(self, type_tag):
        """
        映画タイプを取得
        神保町シアターの場合、
            制作年/製作会社/白黒orカラー/上映時間
        などの情報
        """

        movie_type_list = type_tag.text.split(u'\uff0f') # 全角スラッシュで区切られていることを仮定
        movie_type = "/".join(movie_type_list[:-1]) # 上映時間は除く(DRY)

        return movie_type

    def _get_cast_dict(self, cast_tag):
        """
        キャストの辞書を取得
        """
        cast_list = cast_tag.text.lstrip("■").split("■")
        cast_dict = {}
        for cast in cast_list:
            work, name = cast.split(u'\uff1a', 1) # 全角コロンでsplit
            cast_dict[work] = name

        return cast_dict
    
    def _get_synopsis(self, synopsis_tag):
        """
        あらすじを取得
        """
        synopsis = synopsis_tag.text
        return synopsis

    def _get_movie_start_datetime_str_list(self, program_duration, movie_tag):
        """
        上映開始日時のリストを取得
        """
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

                movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M:%S")

                movie_start_datetime_str_list.append(movie_start_datetime_str)

        return movie_start_datetime_str_list
    
    def _format_timedelta(self, timedelta):
        total_sec = timedelta.total_seconds()
        
        minutes = total_sec // 60

        # total time
        return f'{int(minutes)}分'

    def _get_movie_timedelta_minute_str(self, type_tag):
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

        movie_timedelta_minute_str = self._format_timedelta(movie_timedelta)

        return movie_timedelta_minute_str
    
    def _get_movie_id_and_title(self, movie_tag):
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

    def _get_movie_url(self, program_movie_list_url, movie_id):

        movie_url = f'{program_movie_list_url}#movie{movie_id.zfill(2)}'

        return movie_url

    def _get_soup(self, url):

        # URLからHTMLを取得
        response = requests.get(url)
        response.encoding = "Shift_JIS" 
        soup = BeautifulSoup(response.text, "html.parser")

        return soup

# Webページの仕様が変わったら、アンダーバーから始まるメソッドのいずれかを更新する必要がある

# TODO: どこで時間がかかっているのか特定する
# TODO: loggerを使って特定する

class Cinemavera_Shibuya(Theater):
    def __init__(self):
        super().__init__()

    def scrape_to_be_informed_theater_object(self):
        """
        自分に情報を詰めるために、Webスクレイピングを行う
        このメソッドは映画館ごとに設計する必要がある
        """
        # self.theater_location = self._get_theater_location()
        # それぞれのプログラムページからの情報を集める
        program_urls = self._get_program_urls()
        program_object_list = self._get_program_object_list(program_urls)
        self.program_object_list = program_object_list
    
    # 以下、この映画館のホームページに特化したプライベートメソッド
    def _get_program_urls(self):
        """
        メインページから、上映プログラムのURLを取得する
        """

        program_urls = []
        program_urls.append(urljoin(self.theater_url, 'programs.html'))
        program_urls.append(urljoin(self.theater_url, 'preview.html'))
        
        return program_urls

    def _get_program_object_list(self, program_urls):
        """
        program_objectを、プログラムの数分集めたリストを取得する
        """
        program_object_list = []
        for program_url in program_urls:

            program_object = self._get_program_object(program_url)
            program_object_list.append(program_object)

        return program_object_list

    def _get_program_object(self, program_url):
        """
        program_urlのprogram_objectを取得する
        """

        # プログラムIDを取得
        program_id = self._get_program_id(program_url)

        # プログラムのタイトルを取得
        program_soup = self._get_soup(program_url)
        program_title = self._get_program_title(program_soup)

        # プログラムの上映期間を取得
        program_duration = self._get_program_duration(program_soup)

        # プログラムの上映映画一覧ページのURLを取得
        program_movie_list_url = self._get_program_movie_list_url(program_url)

        # プログラム内の映画オブジェクトのリストを取得
        movie_object_list = self._get_movie_object_list(program_movie_list_url, program_duration)

        program_object = Program(program_id = program_id, 
                                program_title = program_title, 
                                program_duration=program_duration,  
                                program_url = program_url,
                                program_movie_list_url = program_movie_list_url, 
                                movie_object_list = movie_object_list)

        return program_object

    def _get_program_id(self, program_url):
        """
        シネマヴェーラ渋谷のプログラムは、バックナンバーにはidがついているのだが、上映中のもののidを取得するのは難しい
        """
        if program_url == urljoin(self.theater_url, 'programs.html'):
            program_id = "now"
        elif program_url == urljoin(self.theater_url, 'preview.html'):
            program_id = "next"
        else:
            program_id = "unknown"

        return program_id

    def _get_program_title(self, program_soup):
        """
        タイトルがh2タグに囲まれていることを仮定
        """
        
        program_title = program_soup.find('h2').text

        return program_title

    def _get_program_duration(self, program_soup):
        """
        プログラムの上映期間を取得
        """

        schedule_tag = program_soup.find('li', {'class': 'schedule'})
        schedule_text = schedule_tag.find('h4').text

        program_start_date, program_end_date = schedule_text.split(' ～ ')
        program_start_date = datetime.strptime(program_start_date, '%Y/%m/%d').strftime('%Y-%m-%d')
        program_end_date = datetime.strptime(program_end_date, '%Y/%m/%d').strftime('%Y-%m-%d')

        program_duration_dict = {"start": program_start_date, "end": program_end_date}

        return program_duration_dict
    
    def _get_program_movie_list_url(self, program_url):
        """
        シネマヴェーラの場合、program_movie_list_url == program_url
        """
        
        return program_url

    def _get_movie_object_list(self, program_movie_list_url, program_duration):
        movie_object_list = []
        program_movie_list_soup = self._get_soup(program_movie_list_url)
        movie_tags = self._get_movie_tags(program_movie_list_soup)

        link = movie_tags[0].find('a', {'class': 'linkbutton'})['href']

        schedule_table_url = urljoin(self.theater_url, link)

        schedule_table_soup = self._get_soup(schedule_table_url)
        schedule_tag = schedule_table_soup.find("table", {"class": "pctime"})

        for movie_tag in movie_tags:
            
            movie_object = self._get_movie_object(program_movie_list_url, schedule_tag, program_duration, movie_tag)
            movie_object_list.append(movie_object)

        return movie_object_list

    def _get_movie_tags(self, program_movie_list_soup):

        movie_tags = program_movie_list_soup.find_all('ul', {'class': 'films', 'id': re.compile('^id\d+$')})

        return movie_tags

    def _get_movie_object(self, program_movie_list_url, schedule_tag, program_duration, movie_tag):

        movie_id, movie_title, other_info = self._get_movie_id_and_title(movie_tag)
        movie_url = self._get_movie_url(program_movie_list_url, movie_id)


        # 映画のメタ情報を取得
        movie_text_tag = movie_tag.find("li", {"class": "txt"})

        # 映画タイプを取得
        movie_type = self._get_movie_type(movie_text_tag, other_info)

        # キャストを取得
        cast_dict = self._get_cast_dict(movie_text_tag)

        # あらすじを取得
        movie_synopsis = self._get_synopsis(movie_text_tag)

        # 映画の上映時間を取得
        movie_timedelta_minute_str = self._get_movie_timedelta_minute_str(movie_tag)

        # 上映開始日時のリストを取得
        movie_start_datetime_str_list = self._get_movie_start_datetime_str_list(movie_tag, schedule_tag, program_duration, movie_title)
            
        # Movieクラスのオブジェクトを作成。これをリスト化して、programオブジェクトに渡す
        movie_object = Movie(movie_title = movie_title, 
                            movie_id = movie_id, 
                            movie_url = movie_url,
                            movie_timedelta_minute_str = movie_timedelta_minute_str, 
                            movie_type = movie_type, 
                            movie_staff = cast_dict, 
                            movie_synopsis = movie_synopsis, 
                            movie_start_datetime_str_list = movie_start_datetime_str_list)

        return movie_object

    def _get_movie_type(self, movie_text_tag, other_info):
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

    def _get_cast_dict(self, movie_text_tag):
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
    
    def _get_synopsis(self, movie_text_tag):
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
                pass
            elif text.startswith("監督") and flags[0]:
                #print("pass")
                flags[1] = True
                pass
            elif text.startswith("出演") and flags[1]:
                #print("pass")
                pass
            else: 
                #print(synopsis)
                synopsis = text
                break

        return synopsis

    # TODO: 高速化の余地あり
    def _get_movie_start_datetime_str_list(self, movie_tag, schedule_tag, program_duration, movie_title):
        """
        上映開始日時のリストを取得
        スケジュールがたまに誤字ってることがある
        TODO: ->レーベンシュタイン距離が最も近いものを採用する
        例：
        正：「太陽は光り輝く」　誤：「太陽は光輝く」
        TODO: 表を見るのを一回にする、今は映画ごとに以下のfor文を回していて、非効率
        """

        rows = schedule_tag.find_all('tr')

        # 月の初期値をNoneに設定
        month = None
        movie_start_datetime_str_list = []

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
            # 映画の上映月がプログラムの開始月より小さければ、映画の上映年はプログラムの開始年に+1したものにする
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
                    pass
                else:
                    match = re.match(r"(\d+):(\d+).*", time_text)
                    if match:
                        hour = int(match.group(1))
                        minute = int(match.group(2))

                    movie_start_datetime = datetime(year, month, date, hour, minute)
                    movie_start_datetime_str = movie_start_datetime.strftime("%Y-%m-%d %H:%M:%S")
                    
                    # 洋画の場合、邦題の後にスペースを空けて原題が入るが、スケジュールには邦題しか乗らないので、その対策。
                    if movie_title.split(" ")[0] in film_text:
                        movie_start_datetime_str_list.append(movie_start_datetime_str)

        return movie_start_datetime_str_list

    def _format_timedelta(self, timedelta):
        total_sec = timedelta.total_seconds()
        
        minutes = total_sec // 60

        # total time
        return f'{int(minutes)}分'


    def _get_movie_timedelta_minute_str(self, movie_tag):

        movie_title_with_timedelta = movie_tag.find('h3').text

        pattern = r'（(\d+)分'
        match = re.search(pattern, movie_title_with_timedelta)

        if match:
            minutes = int(match.group(1))
            movie_timedelta = timedelta(minutes=minutes)
        
        movie_timedelta_minute_str = self._format_timedelta(movie_timedelta)

        return movie_timedelta_minute_str
    
    def _get_movie_id_and_title(self, movie_tag):
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
        match = re.search(r'『／(.*)）', movie_title_with_timedelta)
        if match:
            other_info = match.group(1)
        else:
            other_info = ""

        return movie_id, movie_title, other_info

    def _get_movie_url(self, program_movie_list_url, movie_id):

        movie_url = f'{program_movie_list_url}#id{movie_id}'

        return movie_url

    def _get_soup(self, url):

        # URLからHTMLを取得
        response = requests.get(url)
        # エンコーディングを自動で判定し、文字コードを設定する
        encoding = response.encoding if 'charset' in response.headers.get('content-type', '').lower() else None
        response.encoding = encoding

        soup = BeautifulSoup(response.content.decode('utf-8'), "html.parser")

        return soup

if __name__ == "__main__":
    jinbocho_theater = Cinemavera_Shibuya()
    