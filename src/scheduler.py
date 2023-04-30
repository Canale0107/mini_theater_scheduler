import os
import sys
import csv
import json
import pandas as pd
import colorama
from colorama import Fore, Style
import argparse
from datetime import date, datetime, timedelta
from lib import kugiri
from data_manager import Data_Manager
from conf import settings
from theaters import Jinbocho_Theater, Cinemavera_Shibuya

# 映画館ごとに日付を管理したり表示したりするクラス
# オプションで、スケジュール表示対象の映画館を指定する

# TODO: Schedulerに--scrapeオプションをつけた時の動作はどうなる？

# TODO: 映画館ごとのjsonファイルは一つにまとめるようにした方がいい
# TODO: 映画館ごとのクラスも一つのファイル(theaters.py)でまとめて定義する

def clear_terminal():
    os.system('clear' if os.name == 'posix' else 'cls')

class Movie_Info():
    def __init__(self, theater_name="", program_title="", movie_title="", movie_duration="", schedule_start_time_str="", schedule_end_time_str="", movie_type="", movie_staff_dict="", movie_synopsis="", movie_url=""):
        self.theater_name = theater_name
        self.program_title = program_title
        self.movie_title = movie_title
        self.movie_duration = movie_duration
        self.schedule_start_time_str = schedule_start_time_str
        self.schedule_end_time_str = schedule_end_time_str
        self.movie_type = movie_type
        self.movie_staff_dict = movie_staff_dict
        self.movie_synopsis = movie_synopsis
        self.movie_url = movie_url

class Scheduler():
    def __init__(self):
        clear_terminal()

        # 映画館の設定を読み込む
        with open('conf/theaters_settings.json') as f:
            self.theaters_settings_dict = json.load(f)

        # conf/theaters_settings.jsonから映画館クラス名の一覧を取得する 
        self.theater_class_name_list = [theater_class_name for theater_class_name in self.theaters_settings_dict.keys()]

        self.get_options()

        # Schedulerは映画館のデータマネージャのリストを持つ
        self.data_manager_dict = {}
        for theater_name in self.theater_class_name_list:
            theater_class = globals()[theater_name]
            self.data_manager_dict[theater_name] = Data_Manager(theater_class())

        self.schedule_path = f'{settings.SCHEDULE_DIR_PATH }/{settings.SCHEDULE_CSV_FILE_NAME}.csv'
        self.get_schedule()
    

    def get_options(self):
        # オプションの設定
        parser = argparse.ArgumentParser()

        # 相互排他的なオプションのグループを作成
        group = parser.add_mutually_exclusive_group()
        group.add_argument('--date', type=str, help='スケジュール表示対象の日付をyymmdd形式（または\"tomorrow\"）で指定（デフォルトは今日）', default=date.today().strftime("%y%m%d"))
        group.add_argument('--title', type=str, help='指定した文字列を含むタイトルの映画のスケジュールを全て表示する', default=None)
        group.add_argument('--program', action='store_true', help='上映中のプログラムの映画情報を表示', default=None)

        # detailオプションはいずれのオプションとも組み合わせて使える
        parser.add_argument('--scrape', action='store_true', help='強制的にWebスクレイピングを行う')
        parser.add_argument('--detail', action='store_true', help='詳細な情報を表示する')
        # 映画館オプションを設定ファイルから定義する
        for theater_class_name, theater_settings in self.theaters_settings_dict.items():
            theater_name = theater_settings["THEATER_NAME"]
            option_str_short = theater_settings["OPTION_STR"][0]
            option_str_long = theater_settings["OPTION_STR"][1]
            parser.add_argument(f'-{option_str_short}', f'--{option_str_long}', action='store_true', help=f'{theater_name}のスケジュールを表示する')

        args = parser.parse_args()

        # オプションで、スケジュールを表示する映画館を指定する（デフォルトは全部）
        # 左のリストが空集合だったら、全ての映画館が表示対象となる
        self.theaters_to_be_displayed = [theater_class_name for theater_class_name in self.theater_class_name_list \
                                        if vars(args)[self.theaters_settings_dict[theater_class_name]["OPTION_STR"][1]]] \
                                        or self.theater_class_name_list

        if args.date == "tomorrow":
            today = datetime.today()  # 現在の日付を取得
            tomorrow = today + timedelta(days=1)  # 1日後の日付を計算
            self.show_date = tomorrow
        else:
            self.show_date = datetime.strptime(args.date, "%y%m%d")
        self.detail = args.detail
        self.show_program_info = args.program
        self.schedule_search_title = args.title
        Data_Manager.scrape = args.scrape

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
                # スクレイピングが行われていなかった場合、保存済みのものをロードする
                self.schedule_df = pd.read_csv(self.schedule_path)
                print("スケジュールデータをロードしました。")
        

    def save_all_schedule(self):
        self.schedule_df = self.get_schedule_df()
        print("スケジュールデータを取得しました。")
        # CSVで保存（rowのindexはFalseに）
        self.schedule_df.to_csv(self.schedule_path, index=False)
        print(f"全てのスケジュールを{self.schedule_path}に保存しました。")

    def main(self):
        # オプションで文字列が指定されていたら、日時に関わらず指定した文字列がタイトルに含まれるような映画を表示
        if self.schedule_search_title != None:
            self.print_movie_search_title()
        # --programオプションが表示されたら、指定した映画館の上映中のプログラムの映画の一覧を表示する
        elif self.show_program_info:
            self.print_movies_in_program()
        # その他の場合は、指定した映画館の指定した日付の上映情報を表示
        else:           
            self.print_todays_movie()

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

    def _get_schedule_data_from_row(self, row):
        """
        schedule.csvを読み込んだpd.DataFrameの行から情報を取得して返す
        """

        now = datetime.now()

        schedule_theater_class_name = row['映画館クラス名']
        schedule_program_id = row['プログラムID']
        schedule_movie_id = row['映画ID']

        schedule_start_time = datetime.strptime(row['開始日時'], "%Y-%m-%d %H:%M")
        schedule_end_time = datetime.strptime(row['終了日時'], "%Y-%m-%d %H:%M")

        data = (schedule_theater_class_name, schedule_program_id, schedule_movie_id, schedule_start_time, schedule_end_time)

        return data

    def _get_movie_info(self, schedule_theater_class_name, schedule_program_id, schedule_movie_id, schedule_start_time, schedule_end_time):
        """
        schedule.csvから取得した映画館クラス名、プログラムID、映画IDから、詳細情報を取得して返す
        """

        # 映画館の辞書を取得
        data_manager = self.data_manager_dict[schedule_theater_class_name]
        theater_object = data_manager.theater_object
        theater_data_dict = theater_object.get_dictionary()

        theater_name = theater_data_dict["theater_name"] # !

        # プログラムタイトル
        programs_dict = theater_object.get_programs_dict()
        program_dict = programs_dict[schedule_program_id] 
        program_title = program_dict["program_title"] # !

        # 映画の情報
        movie_dict = program_dict["movies"][str(schedule_movie_id)]
        movie_title = movie_dict["movie_title"] # !
        movie_duration = movie_dict["movie_timedelta_minute_str"] # !
        # 詳細
        movie_type = movie_dict["movie_type"] # !
        movie_staff_dict = movie_dict["movie_staff"] # !
        movie_synopsis = movie_dict["movie_synopsis"] # !
        movie_url = movie_dict["movie_url"] # !

        schedule_start_time_str = schedule_start_time.strftime("%-m月%-d日 %H:%M") # !
        schedule_end_time_str = schedule_end_time.strftime("%H:%M") # !

        movie_info = Movie_Info(theater_name = theater_name,
                                    program_title = program_title, 
                                    movie_title = movie_title, 
                                    movie_duration = movie_duration, 
                                    movie_type = movie_type, 
                                    schedule_start_time_str = schedule_start_time_str,
                                    schedule_end_time_str = schedule_end_time_str,
                                    movie_staff_dict = movie_staff_dict, 
                                    movie_synopsis = movie_synopsis, 
                                    movie_url = movie_url)

        return movie_info

    def print_movie_search_title(self):
        # ターミナルの文字に色をつけるための設定
        colorama.init()

        print(kugiri("="))
        # オプションで文字列が指定されていたら、日時に関わらず指定した文字列がタイトルに含まれるような映画を表示
        print(f'\"{self.schedule_search_title}\"をタイトルに含む映画の上映情報')
        print(f'表示対象映画館：{", ".join([self.theaters_settings_dict[theater_class_name]["THEATER_NAME"] for theater_class_name in self.theaters_to_be_displayed])}')
        print(kugiri("="))

        # 上映が終わったかどうか
        now = datetime.now()

        # 本日上映の映画タイトルを表示
        # スケジュールデータフレームを一行ずつ見ていく
        for index, row in self.schedule_df.iterrows():

            data = self._get_schedule_data_from_row(row)
            schedule_theater_class_name, schedule_program_id, schedule_movie_id, schedule_start_time, schedule_end_time = data
            over = (now > schedule_start_time)

            # 映画館のjsonファイルは、Data_Managerを呼び出した際に既に読んでいるので、それを使う
            movie_info = self._get_movie_info(*data)
            # スケジュール表示対象映画館のみ表示
            if schedule_theater_class_name in self.theaters_to_be_displayed:
                
                if self.schedule_search_title in movie_info.movie_title:     
                    self.show_movie_info(movie_info, over)

        # TODO: 指定した文字列を含むタイトルの映画の詳細情報を1回だけ表示

    def print_movies_in_program(self):
        print(kugiri("="))
        # オプションで文字列が指定されていたら、日時に関わらず指定した文字列がタイトルに含まれるような映画を表示
        print(f'上映中のプログラムの映画一覧')
        print(f'表示対象映画館：{", ".join([self.theaters_settings_dict[theater_class_name]["THEATER_NAME"] for theater_class_name in self.theaters_to_be_displayed])}')

        # 本日上映の映画タイトルを表示
        # スケジュールデータフレームを一行ずつ見ていく

        # 映画館ごとに上映中のプログラムの映画一覧を表示
        # TODO: 上映日時の最後のやつが過ぎてるやつはグレーにする
        for theater_to_be_displayed in self.theaters_to_be_displayed:
            # 映画館の辞書を取得
            data_manager = self.data_manager_dict[theater_to_be_displayed]
            theater_object = data_manager.theater_object
            theater_data_dict = theater_object.get_dictionary()
            theater_name = theater_data_dict["theater_name"] # !

            # プログラムタイトル
            programs_dict = theater_object.get_programs_dict()
            
            today = date.today()
            
            for program_id, program_dict in programs_dict.items():
                program_title = program_dict["program_title"] # !
                program_duration = program_dict["program_duration"]
                program_start_date = datetime.strptime(program_duration["start"], "%Y-%m-%d").date()
                program_end_date = datetime.strptime(program_duration["end"], "%Y-%m-%d").date()

                # プログラムが上映中であるならば表示する
                if program_start_date <= today and today <= program_end_date:
                    print(kugiri("="))
                    print(f'{theater_name} {program_title}')
                    print(kugiri("="))

                    for movie_id, movie_dict in program_dict["movies"].items():
                        #print(movie_id, movie_dict)

                        # 映画の情報
                        #movie_dict = program_dict["movies"][movie_id]
                        movie_title = movie_dict["movie_title"] # !
                        movie_duration = movie_dict["movie_timedelta_minute_str"] # !
                        # 詳細
                        movie_type = movie_dict["movie_type"] # !
                        movie_staff_dict = movie_dict["movie_staff"] # !
                        movie_synopsis = movie_dict["movie_synopsis"] # !
                        movie_start_datetime_str_list = movie_dict["movie_start_datetime_str_list"]
                        movie_url = movie_dict["movie_url"] # !

                        # 日付を取得できてないやつ対策
                        if movie_start_datetime_str_list:
                            over = datetime.now() > datetime.strptime(movie_start_datetime_str_list[-1], "%Y-%m-%d %H:%M")
                        else:
                            over = False
                        if over:
                            print(Fore.LIGHTBLACK_EX, end='')

                        print(f'{movie_id}. {movie_title} （{movie_duration}）')

                        # 詳細表示
                        if self.detail:
                            print(movie_type)
                            print("■".join([""]+[f'{work}：{name}' for work, name in movie_staff_dict.items()]))
                            print(movie_synopsis)
                            for movie_start_datetime_str in movie_start_datetime_str_list:
                                print(datetime.strptime(movie_start_datetime_str, "%Y-%m-%d %H:%M").strftime("%-m月%-d日 %H:%M"))
                            print(movie_url)

                        if over:
                            print(Style.RESET_ALL, end='')
                        
                        if self.detail:
                            print(kugiri("-"))

    # 指定した日付の上映情報
    # TODO: 綺麗に表示する部分は関数を分ける
    def print_todays_movie(self):

        # ターミナルの文字に色をつけるための設定
        colorama.init()

        print(kugiri("="))
        print(f'{self.show_date.strftime("%-m月%-d日")}の上映情報')
        print(f'表示対象映画館：{", ".join([self.theaters_settings_dict[theater_class_name]["THEATER_NAME"] for theater_class_name in self.theaters_to_be_displayed])}')
        print(kugiri("="))

        # 上映が終わったかどうか
        now = datetime.now()

        # 本日上映の映画タイトルを表示
        # スケジュールデータフレームを一行ずつ見ていく
        for index, row in self.schedule_df.iterrows():

            data = self._get_schedule_data_from_row(row)
            schedule_theater_class_name, schedule_program_id, schedule_movie_id, schedule_start_time, schedule_end_time = data
            over = (now > schedule_start_time)

            # 映画館のjsonファイルは、Data_Managerを呼び出した際に既に読んでいるので、それを使う
            movie_info = self._get_movie_info(*data)

            # スケジュール表示対象映画館のみ表示
            if schedule_theater_class_name in self.theaters_to_be_displayed:
                # スケジュール表示対象日ならば、スケジュールを表示する
                if schedule_start_time.date() == self.show_date.date():
                    self.show_movie_info(movie_info, over)

    def show_movie_info(self, movie_info, over=False):
    # 上映終了したものは灰色で表示
        if over:
            print(Fore.LIGHTBLACK_EX, end='')

        print(f'{movie_info.theater_name} {movie_info.program_title}')
        print(f'{movie_info.schedule_start_time_str}-{movie_info.schedule_end_time_str} {movie_info.movie_title} （{movie_info.movie_duration}）')                        

        # 詳細表示
        if self.detail:
            print(movie_info.movie_type)
            print("■".join([""]+[f'{work}：{name}' for work, name in movie_info.movie_staff_dict.items()]))
            print(movie_info.movie_synopsis)
            print(movie_info.movie_url)

        # 上映終了したものは色を戻す
        if over:
            print(Style.RESET_ALL, end='')
        print(kugiri("-"))
        

    # 欲しい機能一覧：
    # ✅　詳細表示 true/false
    # ✅　映画館ごと(開始時刻順)
    # ✅　開始時刻順 (映画館ごちゃ混ぜ)
    # ✅　日付指定
    # ✅　映画タイトルを指定し、特定の映画の上映日時の一覧を表示
    # ✅　映画館ごとに、上映中のプログラムの映画スケジュール・映画情報の一覧を表示（終了したものはグレーで）   


    # TODO: 指定した期間のデータを.ics形式で出力、タイトル、開始時刻、終了時刻、場所、説明
    """
    def create_event(event_name, start_time, end_time):
        # iCalのイベントオブジェクトを作成
        event = Event()
        event.add('summary', event_name)
        event.add('dtstart', start_time)
        event.add('dtend', end_time)
        event.add('dtstamp', datetime.now())

        return event

    def create_ical(csv_filename):
        # iCalのカレンダーオブジェクトを作成
        calendar = Calendar()
        calendar.add('prodid', '-//My Calendar//example.com//')
        calendar.add('version', '2.0')

        # CSVファイルからイベントを読み込み、iCal形式に変換
        with open(csv_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                event_name = row['event_name']
                start_time = datetime.strptime(row['start_time'], '%Y-%m-%d %H:%M')
                end_time = datetime.strptime(row['end_time'], '%Y-%m-%d %H:%M')
                event = create_event(event_name, start_time, end_time)
                calendar.add_component(event)

        # iCal形式の文字列を返す
        return calendar.to_ical().decode('utf-8')

    # 例: "events.csv"からiCal形式の文字列を作成する
    ical_string = create_ical("events.csv")

    # iCal形式の文字列をファイルに保存する
    with open("events.ics", "w") as ical_file:
        ical_file.write(ical_string)
    """

if __name__ == "__main__":
    scheduler = Scheduler()
    scheduler.main()