import os
import sys
import csv
import json
import pandas as pd
import argparse
from datetime import date, datetime, timedelta
from lib import kugiri
from data_manager import Data_Manager
from conf import settings
from theaters import *

# 映画館ごとに日付を管理したり表示したりするクラス
# オプションで、スケジュール表示対象の映画館を指定する

class Update_Database():
    """
    全ての映画館のデータマネージャを呼び出し、条件に応じてデータベースを更新
    """
    def __init__(self):
        print("Update_Database")

        # 入出力を行うファイルのパス
        self.theater_data_dir_path = settings.THEATER_DATA_DIR_PATH
        self.theater_data_path = f'{settings.THEATER_DATA_DIR_PATH}/{settings.THEATER_DATA_JSON_FILE_NAME}.json'

        # オプションの設定
        parser = argparse.ArgumentParser()
        parser.add_argument('--scrape', action='store_true', help='強制的にWebスクレイピングを行う')
        args = parser.parse_args()

        # 保存用ディレクトリ
        self.theater_data_dict = {}

        if args.scrape:
            # scrapeオプションが指定された場合
            print('--scrapeオプションが指定されました。')
            self.save_theater_data_dict()
            Data_Manager.scrape = True
        else:
            # 映画館データが存在しない場合
            if not os.path.exists(self.theater_data_path):
        
                print('映画館データが存在しません。')
                # そもそもディレクトリがない場合
                if not os.path.exists(self.theater_data_dir_path):
                    os.makedirs(self.theater_data_dir_path)
                    print(f'ディレクトリ{self.theater_data_dir_path}を作成しました。')

                self.save_theater_data_dict()
                Data_Manager.no_data = True
            
            # 映画館データが存在した場合
            else:
                with open(self.theater_data_path, 'r') as file:
                    self.theater_data_dict = json.load(file)
                print(f'データをロードしました。')

                # ファイルに最終更新日が書いてあれば、それを取得
                if "last_update" in self.theater_data_dict:
                    self.last_update = datetime.strptime(self.theater_data_dict["last_update"], "%Y-%m-%d").date()
                    print(f"最終取得日:{self.last_update}")

                    # 最終取得日が{settings.UPDATE_DAYS_DELTA}日以上前ならWebスクレイピングを行う
                    if date.today() > self.last_update + timedelta(days = settings.UPDATE_DAYS_DELTA):
                        print(f'最終取得日から{settings.UPDATE_DAYS_DELTA}日以上経っています。')
                        self.save_theater_data_dict()
                        Data_Manager.old = True

                    # 最終取得日が{settings.UPDATE_DAYS_DELTA}日以内の場合
                    else:
                        print(f'最終取得日が{settings.UPDATE_DAYS_DELTA}日以内です。')
                        Data_Manager.old = False

                # 最終更新日が書いてなければ、スクレイピングを行う
                else:
                    print('最終更新日が不明です。')
                    self.save_theater_data_dict()
                    Data_Manager.no_data = True

        # 映画館の設定を読み込む
        with open('conf/theaters_settings.json') as f:
            self.theaters_settings_dict = json.load(f)

        # conf/theaters_settings.jsonから映画館クラス名の一覧を取得する 
        self.theater_class_name_list = [theater_class_name for theater_class_name in self.theaters_settings_dict.keys()]

        # 映画館のデータマネージャのリストを作成
        self.data_manager_dict = {}
        for theater_name in self.theater_class_name_list:
            theater_class = globals()[theater_name]
            self.data_manager_dict[theater_name] = Data_Manager(theater_class())

        # スケジュールデータを作成する
        self.schedule_path = f'{settings.SCHEDULE_DIR_PATH }/{settings.SCHEDULE_CSV_FILE_NAME}.csv'
        self.get_schedule()

    def get_last_update_str(self):
        last_update_str = date.today().strftime("%Y-%m-%d")
        return last_update_str

    def save_theater_data_dict(self):
        self.theater_data_dict['last_update'] = self.get_last_update_str()
        with open(self.theater_data_path, 'w', encoding="utf-8") as f:
            json.dump(self.theater_data_dict, f, indent = 4, ensure_ascii=False)

    def get_schedule(self):
        print(kugiri("="))
        print("get_schedule")
        # scheduleディレクトリが無い場合、作成
        if not os.path.exists(settings.SCHEDULE_DIR_PATH ):
            print(f"ディレクトリ{settings.SCHEDULE_DIR_PATH}を作成します。")
            os.makedirs(settings.SCHEDULE_DIR_PATH )
            
        # scheduleディレクトリにall_schedule.csvがない場合、スケジュールを作成
        if not os.path.exists(self.schedule_path):
            self.save_all_schedule()

        # all_schedule.csvがあった場合
        else:
            # どこかでスクレイピングが行われていた場合：
            if Data_Manager.scraped:
                print("スケジュールデータを更新します。")
                self.save_all_schedule()
            else:
                print("スケジュールデータは更新されませんでした。")
        
    def save_all_schedule(self):
        self.schedule_df = self.get_schedule_df()
        print("スケジュールデータを取得しました。")
        # CSVで保存（rowのindexはFalseに）
        self.schedule_df.to_csv(self.schedule_path, index=False)
        print(f"全てのスケジュールを{self.schedule_path}に保存しました。")

    def get_schedule_df(self):
        df_list = []

        for data_manager in self.data_manager_dict.values():
            df = data_manager.get_df()
            df_list.append(df)

        # データフレームを縦に結合
        df_merged = pd.concat(df_list, axis=0)

        # 開始日時でソート
        df_sorted = df_merged.sort_values(by='開始日時')

        schedule_df = df_sorted

        return schedule_df

if __name__ == "__main__":
    update_database = Update_Database()