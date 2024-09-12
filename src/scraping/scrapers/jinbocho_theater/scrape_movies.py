import re
from datetime import timedelta

from .utils import get_soup, get_program_movie_list_url


__all__ = ['get_movies']


def _get_movie_tags(program_url):
    """
    映画のタグを取得
    """
    program_movie_list_soup = get_soup(get_program_movie_list_url(program_url))
    return program_movie_list_soup.find_all('div', {"class": "data2_film"}, {'id': re.compile(r"movie\d{2}")})


def _get_movie_id_and_title(movie_tag):
    """
    映画IDとタイトルを取得
    """
    movie_title_with_number = movie_tag.find("div", {"class": "data2_title"}).text.strip().replace("\t", "")
    movie_title_with_number = re.sub(r'\xa0+', ' ', movie_title_with_number)  # スペースを半角スペースに

    # IDとタイトルを抽出
    title_match = re.match(r"(\d+)[.]\s+(.*)", movie_title_with_number)
    if title_match:
        movie_id, movie_title = title_match.groups()
        return movie_id, movie_title
    raise ValueError("映画IDとタイトルが見つかりませんでした")


def get_movie_url(program_url, movie_id):
    """
    映画のURLを生成
    """
    return f'{get_program_movie_list_url(program_url)}#movie{movie_id.zfill(2)}'


def get_movie_type(type_tag):
    """
    映画タイプを取得 (例: 制作年、製作会社、白黒/カラー、上映時間)
    """
    return "/".join(type_tag.text.split(u'\uff0f')[:-1])  # 上映時間を除外


def get_cast_dict(cast_tag):
    """
    キャスト情報を辞書形式で取得
    """
    cast_dict = {}
    cast_list = cast_tag.text.lstrip("■").split("■")
    for cast in cast_list:
        if u'\uff1a' in cast:
            role, name = cast.split(u'\uff1a', 1)
            cast_dict[role.strip()] = name.strip()
    return cast_dict


def get_synopsis(synopsis_tag):
    """
    あらすじを取得
    """
    return synopsis_tag.text.strip()


def format_timedelta(movie_timedelta):
    """
    タイムデルタを「xx分」の形式にフォーマット
    """
    minutes = movie_timedelta.total_seconds() // 60
    return f'{int(minutes)}分'


def get_movie_timedelta_minute_str(type_tag):
    """
    映画の上映時間を取得
    """
    type_text = type_tag.text
    movie_hour = int(re.search(r'(\d+)時間', type_text).group(1)) if re.search(r'(\d+)時間', type_text) else 0
    movie_minute = int(re.search(r'(\d+)分', type_text).group(1)) if re.search(r'(\d+)分', type_text) else 0
    return format_timedelta(timedelta(hours=movie_hour, minutes=movie_minute))


def _get_movie(program_url, movie_tag):
    """
    映画情報を取得
    """
    movie_id, movie_title = _get_movie_id_and_title(movie_tag)
    movie_url = get_movie_url(program_url, movie_id)

    type_tag, cast_tag, synopsis_tag = movie_tag.find_all("p", {"class": "data2_text"})
    movie_type = get_movie_type(type_tag)
    cast_dict = get_cast_dict(cast_tag)
    synopsis = get_synopsis(synopsis_tag)
    runtime = get_movie_timedelta_minute_str(type_tag)
    
    # スタッフ情報の整形
    staff = '◆' + '◆'.join(f"{k}: {v}" for k, v in cast_dict.items())

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
    """
    プログラムに紐づく全ての映画情報を取得
    """
    return [_get_movie(program_url, movie_tag) for movie_tag in _get_movie_tags(program_url)]
