from src.scraping.utils.csv_loader import load_theaters_from_csv

def get_theater_url(theater_id):
    theaters = load_theaters_from_csv()

    for theater in theaters:
        if theater['id'] == theater_id:
            return theater['url']
    return None

def get_theater_name_en(theater_id):
    theaters = load_theaters_from_csv()

    for theater in theaters:
        if theater['id'] == theater_id:
            return theater['name_en']
    return None