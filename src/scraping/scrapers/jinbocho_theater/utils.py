from bs4 import BeautifulSoup
import requests

def get_soup(url, encoding="Shift_JIS"):
    """
    指定されたURLのHTMLを取得し、BeautifulSoupオブジェクトを返す
    """
    response = requests.get(url)
    response.encoding = encoding
    return BeautifulSoup(response.text, "html.parser")

def get_program_movie_list_url(program_url):
    """
    プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
    """
    return program_url.replace(".html", "_list.html")