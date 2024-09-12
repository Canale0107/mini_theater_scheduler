import re
from datetime import datetime
from urllib.parse import urljoin

from .utils import get_soup, get_program_movie_list_url


__all__ = ['get_programs']


def get_program_urls(theater_url):
    """
    メインページのURLから、上映プログラムのURL一覧を取得して返す
    """
    theater_soup = get_soup(theater_url)
    div_tag = theater_soup.find("div", {"class": "link_all"})
    if not div_tag:
        return []

    return [
        urljoin(theater_url, a_tag["href"]) 
        for a_tag 
        in div_tag.find_all("a", href=lambda href: href and href.startswith("program/"))
    ]

def get_program_title(program_url):
    """
    タイトルがh3タグに囲まれていることを仮定し、program_urlから、プログラムのタイトルを返す
    """
    program_soup = get_soup(program_url)
    h3_tags = program_soup.find_all("h3")
    return " ".join([h3_tag.text.strip() for h3_tag in h3_tags])


def extract_date(pattern, text):
    """
    指定された正規表現パターンで日付を抽出
    """
    match = re.search(pattern, text)
    return match.groups() if match else None


def parse_end_date(end_patterns, schedule, start_date):
    """
    終了日を複数のパターンから抽出し、見つからなければ開始日を返す
    """
    for pattern in end_patterns:
        end_date = extract_date(pattern, schedule)
        if end_date:
            year = start_date.year
            if len(end_date) == 4:  # 年月日が含まれるパターン
                year, month, day = map(int, end_date[1:])
            elif len(end_date) == 3:  # 月日が含まれるパターン
                month, day = map(int, end_date[1:])
            else:  # 日のみが含まれるパターン
                month, day = start_date.month, int(end_date[1])
            return datetime(year, month, day).date()
    return start_date  # 終了日が見つからなかった場合、開始日を返す


def get_program_duration(program_url):
    program_soup = get_soup(program_url)
    schedule = program_soup.find("p", class_="schedule").text
    start_pattern = r"(\d+)年(\d+)月(\d+)日"
    end_patterns = [
        r"(〜|・)(\d+)年(\d+)月(\d+)日",
        r"(〜|・)(\d+)月(\d+)日",
        r"(〜|・)(\d+)日"
    ]

    start_date = extract_date(start_pattern, schedule)
    if not start_date:
        raise ValueError("開始日が見つかりません")
    start_date = datetime(*map(int, start_date)).date()
    end_date = parse_end_date(end_patterns, schedule, start_date)
    
    return start_date, end_date


def _get_program(program_url):
    start_date, end_date = get_program_duration(program_url)
    return {
        'title': get_program_title(program_url),
        'start_date': start_date.strftime("%Y-%m-%d"),
        'end_date': end_date.strftime("%Y-%m-%d"),
        'program_url': program_url,
        'program_movie_list_url': get_program_movie_list_url(program_url),
    }


def get_programs(theater_url):
    """
    指定した劇場URLのプログラム情報を取得
    """
    return [_get_program(url) for url in get_program_urls(theater_url)]
