from flask import Flask, render_template, jsonify
import csv, json
import pandas as pd
from datetime import datetime, date, timedelta
from src.database.db_manager import get_db
from src.database.models import Theater, Program, Movie  # 必要なモデルをインポート

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route('/')
def index():
    message = 'ミニシアター番組表'
    return render_template('index.html', message=message)

def read_csv_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            data.append(row)
    return data

@app.route('/schedule')
@app.route('/schedule/<request_date>')
def schedule(request_date=None):
    show_date = date.today() if request_date is None else datetime.strptime(request_date, "%Y-%m-%d").date()

    schedule_dict = {}
    theater_name_list = []

    with get_db() as db:
        theaters = db.query(Theater).all()
        
        # 劇場リストを生成
        for theater in theaters:
            theater_name_list.append(theater.name)
            schedule_dict[theater.name] = {}

            # プログラムと映画のスケジュールを取得
            for program in theater.programs:
                for movie in program.movies:
                    movie_runtime_str = movie.runtime.replace('分', '')
                    movie_runtime = int(movie_runtime_str)
                    movie_runtime_timedelta = timedelta(minutes=movie_runtime)
                    for movie_schedule in movie.movie_schedules:
                        start_datetime = movie_schedule.start_datetime
                        end_datetime = start_datetime + movie_runtime_timedelta

                        if start_datetime.date() == show_date:
                            schedule_dict[theater.name][movie.title] = {
                                "title": movie.title,
                                "start_end_time": f'{start_datetime.strftime("%H:%M")}-{end_datetime.strftime("%H:%M")}',
                                "type": movie.type,
                                "staff": movie.staff,
                                "start_hour": start_datetime.hour,
                                "start_min": start_datetime.minute,
                                "duration": movie_runtime,
                                "description": movie.synopsis,
                                "url": movie.movie_url,
                            }

    return render_template('schedule.html',
                            date=show_date.strftime("%Y年%-m月%-d日"),
                            previousday=(show_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                            nextday=(show_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                            theater_names=theater_name_list,
                            times=range(10, 24),
                            schedule_dict=schedule_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333, debug=True)

# または、以下を実行
# export FLASK_APP = app.py
# flask run