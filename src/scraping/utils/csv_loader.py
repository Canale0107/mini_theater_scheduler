import csv

def load_theaters_from_csv():
    """
    CSVファイルから映画館情報を読み込んで、辞書のリストを返す関数。
    
    :return: 映画館情報の辞書リスト
    """

    # CSVファイルのパス
    csv_filepath = '/app/src/scraping/data/theaters.csv'

    theaters = []
    with open(csv_filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            theaters.append({
                'id': int(row['id']),
                'name': row['name'],
                'name_en': row['name_en'],
                'url': row['url'],
                'location': row['location']
            })
    return theaters