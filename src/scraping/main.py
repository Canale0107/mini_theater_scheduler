from src.database.db_manager import reset_db, init_db, get_db
from src.database.repositories.theater_repository import TheaterRepository
from src.scraping.utils.csv_loader import load_theaters_from_csv
from src.scraping.scraper_manager import scrape_and_save_data


if __name__ == '__main__':
    # データベースをリセット（reset_dbは、開発・テスト時の使用に限る）
    reset_db()

    # 初期化
    init_db()

    # CSVから映画館情報を読み込む
    theaters = load_theaters_from_csv()

    # データベースに接続し、映画館情報を保存
    with get_db() as db:
        for theater in theaters:
            print(f"映画館: {theater['name']} をデータベースに保存中...")
            # 映画館情報を保存（既に存在する場合はスキップ）
            TheaterRepository.create_theater(
                db=db,
                id=theater['id'],
                name=theater['name'],
                name_en=theater['name_en'],
                url=theater['url'],
                location=theater['location']
            )

            # スクレイピングを行いプログラム・映画情報を保存
            print(f"映画館: {theater['name']} のデータをスクレイピング中...")
            scrape_and_save_data(theater['id'])

    print("すべての映画館データが処理されました。")