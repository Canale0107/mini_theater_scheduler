from flask import Flask, render_template, jsonify
import csv, json
import pandas as pd
from datetime import datetime, date

app = Flask(__name__)

@app.route('/')
def index():
    message = 'Hello, Flask!'
    return render_template('index.html', message=message)

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data


@app.route('/csv_view')
def csv_view():
    data = read_csv_file('../../data/schedule_sample/all_schedule.csv')

    return render_template('csv_view.html', data=data)

@app.route('/schedule')
def schedule():

    # TODO: theater_settings.jsonから読み込む
    with open('../update_database/conf/theaters_settings.json') as f:
        theaters_settings_dict = json.load(f)
    theater_class_name_list = []
    theater_name_list = []
    for theater_class_name, theater_settings_dict in theaters_settings_dict.items():
        theater_class_name_list.append(theater_class_name)
        theater_name = theater_settings_dict["THEATER_NAME"]
        theater_name_list.append(theater_name)

    with open('../../data/theater_data_sample/theater_data.json') as f:
        theater_data = json.load(f)

    schedule_dict = {}
    for theater_class_name in theater_class_name_list:
        theater_dict = theater_data[theater_class_name]
        theater_name = theater_dict["theater_name"]
        schedule_dict[theater_name] = {}

    schedule_df = pd.read_csv('../../data/schedule_sample/all_schedule.csv', dtype=str)

    today = date.today()

    for index, row in schedule_df.iterrows():
    # 行ごとの処理
        theater_class_name = row['映画館クラス名']
        program_id = row['プログラムID']
        movie_id = row['映画ID']
        start_datetime = datetime.strptime(row['開始日時'], "%Y-%m-%d %H:%M")
        end_datetime = datetime.strptime(row['終了日時'], "%Y-%m-%d %H:%M")
        movie_duration = int((end_datetime - start_datetime).total_seconds()/60)

        if start_datetime.date() == today:
            theater_dict = theater_data[theater_class_name]
            program_dict = theater_dict["programs"][program_id]
            movie_dict = program_dict["movies"][movie_id]

            theater_name = theater_dict["theater_name"]
            movie_title = movie_dict["movie_title"]
            movie_type = movie_dict["movie_type"]
            movie_staff_dict = movie_dict["movie_staff"]
            movie_synopsis = movie_dict["movie_synopsis"]
            movie_url = movie_dict["movie_url"]
            schedule_dict[theater_name][movie_title]={
                    "title": movie_title,
                    "start_end_time": f'{start_datetime.strftime("%H:%M")}-{end_datetime.strftime("%H:%M")}',
                    "type": movie_type,
                    "staff": "■".join([""]+[f'{work}：{name}' for work, name in movie_staff_dict.items()]),
                    "start_hour": start_datetime.hour,
                    "start_min": start_datetime.minute,
                    "duration": movie_duration,
                    "discription": movie_synopsis,
                    "url": movie_url,
                }

    return render_template('schedule.html', 
                            date=today.strftime("%Y年%-m月%-d日"),
                            theater_names=theater_name_list,
                            times=range(10, 24),
                            schedule_dict=schedule_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333)

# または、以下を実行
# export FLASK_APP = app.py
# flask run