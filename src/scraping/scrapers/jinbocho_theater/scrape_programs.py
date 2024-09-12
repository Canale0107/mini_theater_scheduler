import re
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests

__all__ = ['get_programs']

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

def get_program_urls(theater_url):
    """
    メインページのURLから、上映プログラムのURL一覧を取得して返す
    """
    theater_soup = get_soup(theater_url)
    div_tag = theater_soup.find("div", {"class": "link_all"})
    if not div_tag:
        return []

    program_urls = []
    for a_tag in div_tag.find_all("a", href=lambda href: href and href.startswith("program/")):
        program_urls.append(urljoin(theater_url, a_tag["href"]))

    return program_urls

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