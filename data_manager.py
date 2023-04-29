import os
import re
import csv
import json
import pandas as pd
import argparse
from datetime import date, datetime, timedelta
from theater_class import Theater, Program, Movie
# from jinbocho_theater import Jinbocho_Theater # for debug
# from cinemavera_shibuya import Cinemavera_Shibuya # for debug

import settings

from lib import kugiri

class Data_Manager():
    """
    映画館データを保存・ロードするクラス
    Theaterオブジェクトはそれぞれ独自のData_Managerを持つ
    Theaterオブジェクト、Programオブジェクト、Movieオブジェクトと辞書データを相互に変換する
    """
    
    # 強制的にWebスクレイピングを行いたい場合Trueにするクラス変数（全オブジェクト共通）
    scrape = False

    # スクレイピングが行われたかどうかを保持するフラグ
    scraped = False
    
    def __init__(self, theater_object):
        print(kugiri("="))
        print(f'{theater_object.theater_name} data manager')

        self.last_update = None
        self.theater_object = theater_object

        # 入出力を行うファイルのパス
        self.data_dir_path = settings.THEATER_DATA_DIR_PATH
        self.theater_data_path = f'{settings.THEATER_DATA_DIR_PATH}/{settings.THEATER_DATA_JSON_FILE_NAME}.json'

        # 保存用辞書
        self.theater_data_dict = {}

        self.get_informed()

    def get_last_update_str(self):
        return self.last_update.strftime("%Y-%m-%d")

    def get_theater_dict(self):
        return self.theater_object.get_dictionary()

    def get_informed(self):
        
        """
        Webスクレイピング、またはJSONファイルのロードにより、self.theater_dataに情報を詰める
        """

        # --scrapeが指定された場合、last_updateを本日の日付とし、scrapeを行ってtheater_objectを作成し、self.theater_dataとする
 
        # theater_data.jsonがある場合、self.theater_dataにlast_updateとtheater_objectをロード
        if os.path.exists(self.theater_data_path):
            self.load_theater_data()

            if self.theater_object.theater_class_name not in self.theater_data_dict:
                print(f"ロードしたデータに{self.theater_object.theater_name}のデータが含まれません。")
                self.scrape_theater_data()

            if Data_Manager.scrape:
                print("--scrapeオプションが指定されました。")
                self.scrape_theater_data()

        # theater_data.jsonがない場合
        else:
            # データディレクトリがない場合、ディレクトリを作成
            if not os.path.exists(self.data_dir_path):
                os.makedirs(self.data_dir_path)
                logging.debug(f'directory not exists so directory {self.data_dir_path} created.')
            
            print(f'データファイル{self.theater_data_path}が存在しません。')
            self.scrape_theater_data()


    # TODO: initに書き、ファイルが存在する場合ロードし、ない場合last_updateだけ保存する
    # jsonファイルの、自分の映画館のところだけロード
    def load_theater_data(self):
        """
        JSONファイルをロードして、最終取得日と映画館の辞書を取得
        """
        with open(self.theater_data_path, 'r') as file:
            self.theater_data_dict = json.load(file)
        print(f'データをロードしました。')

        # ファイルに最終更新日が書いてあれば、それを取得
        if "last_update" in self.theater_data_dict:
            self.last_update = datetime.strptime(self.theater_data_dict["last_update"], "%Y-%m-%d").date()
            print(f"最終取得日:{self.get_last_update_str()}")

            # 自分の映画館のクラス名がファイルに登録されていた場合
            if self.theater_object.theater_class_name in self.theater_data_dict:
                theater_dict = self.theater_data_dict[self.theater_object.theater_class_name]

                # 最終取得日が{settings.UPDATE_DAYS_DELTA}日以上前ならWebスクレイピングを行う
                if date.today() > self.last_update + timedelta(days = settings.UPDATE_DAYS_DELTA):
                    print(f'最終取得日から{settings.UPDATE_DAYS_DELTA}以上経っています。')
                    self.scrape_theater_data()
                # 最終取得日が{settings.UPDATE_DAYS_DELTA}日以内の場合
                else:
                    print(f'最終取得日が{settings.UPDATE_DAYS_DELTA}日以内です。')
                    self.load_theater_dict(theater_dict)
            # "last_update"が書いていなかった場合
            else:
                print('ファイルにデータが登録されていません。')
                self.scrape_theater_data()

        # 最終更新日が書いてなければ、スクレイピングを行う
        else:
            print('ファイルにデータが登録されていません。')
            self.scrape_theater_data()

        # decode (theater_dict -> theater_object)
    def load_theater_dict(self, theater_dict):
        """
        theater_dictから自分のtheater_dataのtheater_objectに情報を詰めるメソッド
        """
        self.theater_object.theater_name = theater_dict["theater_name"]
        self.theater_object.theater_name_en = theater_dict["theater_name_en"]
        self.theater_object.theater_url = theater_dict["theater_url"]
        self.theater_object.theater_location = theater_dict["location"]

        program_object_list = self._programs_dict_to_program_object_list(theater_dict["programs"])
        self.theater_object.program_object_list = program_object_list

    # decode (programs_dict -> program_object_list)
    def _programs_dict_to_program_object_list(self, programs_dict):

        program_object_list = []
        for program_id, program_dict in programs_dict.items():

            movie_object_list = self._movies_dict_to_movie_object_list(program_dict["movies"])

            program_object = Program(program_id = program_id,
                                    program_title = program_dict["program_title"],
                                    program_duration = program_dict["program_duration"], 
                                    program_url = program_dict["program_url"], 
                                    program_movie_list_url = program_dict["program_movie_list_url"], 
                                    movie_object_list = movie_object_list)
            program_object_list.append(program_object)

        return program_object_list

    # decode (movies_dict -> movie_object_list)
    def _movies_dict_to_movie_object_list(self, movies_dict):

        movie_object_list = []
        for movie_id, movie_dict in movies_dict.items():
            movie_object = Movie(movie_id = movie_id, 
                                movie_title = movie_dict["movie_title"], 
                                movie_url = movie_dict["movie_url"], 
                                movie_timedelta_minute_str = movie_dict["movie_timedelta_minute_str"],
                                movie_type = movie_dict["movie_type"], 
                                movie_staff = movie_dict["movie_staff"], 
                                movie_synopsis = movie_dict["movie_synopsis"], 
                                movie_start_datetime_str_list = movie_dict["movie_start_datetime_str_list"])
            movie_object_list.append(movie_object)

        return movie_object_list

    def scrape_theater_data(self):
        print("Webスクレイピングを行います。")
        last_update = date.today()
        self.last_update = last_update

        Data_Manager.scraped = True

        # Theaterオブジェクトとしての自分に情報を追加する(to be informed theater object)ために、Webスクレイピングを行う
        self.theater_object.scrape_to_be_informed_theater_object()
        print("Webページをスクレイピングしました。")

        # 映画館の情報をjsonで保存
        self.dump_json()

    def dump_json(self):
        """
        最終取得日と映画館の辞書をJSONファイルとして保存
        """

        theater_dict = self.get_theater_dict()

        # 保存用辞書の最終取得日に、自分のtheater_dataの最終更新日を代入
        # TODO: last_updateはData_Managerが自分で持てばいい
        # TODO: そうすると、Theater_Dataクラスはいらなくなる
        self.theater_data_dict["last_update"] = self.get_last_update_str()
        self.theater_data_dict[self.theater_object.theater_class_name] = theater_dict

        with open(self.theater_data_path, 'w', encoding="utf-8") as f:
            json.dump(self.theater_data_dict, f, indent = 4, ensure_ascii=False)
            print(f"データを{self.theater_data_path}にセーブしました。")

    def get_df(self):
        """
        theater_objectに対応するpandas.DataFrameを取得する
        """
        sorted_schedule_list = self._get_sorted_schedule_list()

        df = pd.DataFrame(sorted_schedule_list, columns=['映画館クラス名', 'プログラムID', '映画ID', '開始日時', '終了日時'])

        return df

    # TODO: 後でマージするときにpandasでソートするのでソートしなくてもいい
    
    def _get_sorted_schedule_list(self):
        schedule_list = []
        theater_class_name = self.theater_object.theater_class_name
        program_object_list = self.theater_object.program_object_list
        for program_object in program_object_list:
            program_id = program_object.program_id
            movie_object_list = program_object.movie_object_list
            for movie_object in movie_object_list:
                movie_id = movie_object.movie_id
                for movie_start_datetime_str, movie_end_datetime_str in on_screen_time(movie_object):
                    schedule = [theater_class_name, program_id, movie_id, movie_start_datetime_str, movie_end_datetime_str]
                    schedule_list.append(schedule)

        # print(schedule_list) # for debug

        # movie_start_datetime_strで並べ替え
        # TODO: x[3]という書き方が好きじゃない
        sorted_schedule_list = sorted(schedule_list, key=lambda x: x[3])

        return sorted_schedule_list

class on_screen_time:
    """
    movie_objectから、(開始時刻, 終了時刻)を順番に返すイテレータオブジェクト
    """
    def __init__(self, movie_object):
        self.movie_start_datetime_str_list = movie_object.movie_start_datetime_str_list
        # 上映時間のtimedeltaを取得
        match = re.match(r'^(\d+)分', movie_object.movie_timedelta_minute_str)
        if match:
            minute_str = match.group(1)
            self.movie_timedelta = timedelta(minutes=int(minute_str))

        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= len(self.movie_start_datetime_str_list):
            raise StopIteration

        movie_start_datetime_str = self.movie_start_datetime_str_list[self.index]
        # 上映開始datetimeを取得
        movie_start_datetime = datetime.strptime(movie_start_datetime_str, "%Y-%m-%d %H:%M")
        # 上映終了datetimeを計算
        movie_end_datetime = movie_start_datetime + self.movie_timedelta
        # 上映終了datetimeを文字列に変換
        movie_end_datetime_str = movie_end_datetime.strftime("%Y-%m-%d %H:%M")

        result = (movie_start_datetime_str, movie_end_datetime_str)
        self.index += 1
            
        return result

# for debug
'''
if __name__ == '__main__':
    
    # 例
    jinbocho_data_manager = Data_Manager(Jinbocho_Theater())
    cinemavera_data_manager = Data_Manager(Cinemavera_Shibuya())
    jinbocho_theater_object = jinbocho_data_manager.theater_data.theater_object
    print("プログラム一覧：")
    for program_object in jinbocho_theater_object.program_object_list:
        program_title = program_object.get_dictionary()["program_title"]
        print(program_title)
'''