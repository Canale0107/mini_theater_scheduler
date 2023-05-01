from flask import Flask, render_template, request
import csv

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