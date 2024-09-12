from bs4 import BeautifulSoup
import requests

def get_soup(url):
    response = requests.get(url)
    response.encoding = "Shift_JIS" 
    soup = BeautifulSoup(response.text, "html.parser")

    return soup

def get_program_movie_list_url(program_url):
    """
    プログラムIDに_listをつけるとプログラムの映画一覧ページのURLになることを仮定し、プログラムの映画一覧ページのURLを取得
    """

    program_movie_list_url = program_url.replace(".html", "_list.html")
    
    return program_movie_list_url