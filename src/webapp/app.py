from flask import Flask, render_template, jsonify
import csv
from datetime import date

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

    schedule_dict = {
        "テレビ東京": {
            "1":{
                "title": "カードファイト!! ヴァンガード2019",
                "discription": "先導アイチをはじめとするヴァンガードファイターたちが挑む新たな戦いの場「ヴァンガード甲子園」。失った何かを取り戻すため彼らの運命が再び交錯する!",
                "start_hour": 8,
                "start_min": 0, 
                "duration": 30,
            },
            "2":{
                "title": "しまじろうのわお！",
                "discription": "世界の、自然の、不思議がいっぱい! 「わお!」(驚き)がつまった30分! 親子で楽しめる、しまじろうのテレビ番組です。",
                "start_hour": 8,
                "start_min": 30,
                "duration": 30
            },
            "3":{
                "title": "ウルトラマンタイガ",
                "discription": "宇宙人がひそかに暮らしている地球で、民間警備組織E.G.I.S.のメンバーとして働く工藤ヒロユキは、任務中に宇宙人がらみの事件にまきこまれてしまう。",
                "start_hour": 9,
                "start_min": 0,
                "duration": 30
            },
            "4":{
                "title": "ポチっと発明",
                "discription": "4回戦は「カーリング・レース・バトル」。氷上の的を狙ってシュートし、合計得点を競い合う。対戦相手に点差を広げられるも、エイジ達は巨大な雪だるまの攻略を目指す。",
                "start_hour": 9,
                "start_min": 30,
                "duration": 30
            },
            "5":{
                "title": "けだまのゴンじろー",
                "discription": "消防訓練に来たマコトたち。火と水に強そうな消防士のボタンをゲットすれば無敵になれると思ったゴンじろーは、教官の消防士のボタンを手に入れるため奮闘するが…!?",
                "start_hour": 10,
                "start_min": 0,
                "duration": 30
            },
            "6":{
                "title": "パウ・パトロール",
                "discription": "世界160の国や地域で放送される大人気アニメが日本上陸！主人公・ケントと、6匹の子犬からなるチーム「パウ・パトロール」が様々なトラブルに立ち向かうよ!",
                "start_hour": 10,
                "start_min": 30,
                "duration": 30
            },
            "7":{
                "title": "TXNニュース",
                "discription": "",
                "start_hour": 11,
                "start_min": 0,
                "duration": 3
            },
            "8":{
                "title": "TVチャンピオン極～KIWAMI～",
                "discription": "超絶高カロリー…でも美味い！そんな禁断メシの天才料理人が集結！バターの海でステーキVSチーズまみれデブサンド！マヨネーズ丸１本使ったすき焼きVSチャーハンは絶品!",
                "start_hour": 11,
                "start_min": 3,
                "duration": 27
            },
            "9":{
                "title": "世界！ ニッポン行きたい人応援団",
                "discription": "“ニッポンに行きたくて行きたくてたまらない”外国人を世界で大捜索！盆石が大好き！なアメリカ人男性をご招待！アメリカで醤油作りの会社を設立した男性も登場!",
                "start_hour": 11,
                "start_min": 30,
                "duration": 30
            }
        },
        "フジテレビ": {
            "1":{
                "title": "めざましどようび",
                "discription": "五輪チケット狙い目は…再抽選に数十万枚用意▽いじめメモ担任紛失▽伊調・川井が激突へ▽ローマ街にゴミの山▽言葉聞き分けるトド▽藤原紀香の健康法は",
                "start_hour": 8,
                "start_min": 0,
                "duration": 30
            },
            "2":{
                "title": "にじいろジーン", 
                "discription": "特別企画!SNSで話題のじぃばぁを世界へ発信▽夏休み前に!動物園&amp;水族館を100倍楽しむ方法▽世界有数パワスポ!アメリカ・セドナ▽都心オアシスの階段で出世運UP",
                "start_hour": 8,
                "start_min": 30,
                "duration": 85
            },
            "3":{
                "title": "ライオンのグータッチ",
                "discription": "初の予選突破を目指す小学生リレーチームを陸上界のレジェンド末續慎吾が本気指導!少しの意識で変わる!速く走れるフォームとは?スタートダッシュの極意も伝授",
                "start_hour": 9,
                "start_min": 55,
                "duration": 30
            },
            "4":{
                "title": "いただきハイジャンプ",
                "discription": "知念&amp;伊野尾VS高木&amp;八乙女がグルメブラックジャックで真剣勝負!名店のから揚げ一皿の個数を足していき21を目指す!多種多様なから揚げが続々▽山田珍回答",
                "start_hour": 10,
                "start_min": 25,
                "duration": 28
            },
            "5":{
                "title": "タイプライターズ13～物書きの世界～",
                "discription": "共に小説を創作し作家としての顔を持つ又吉直樹と加藤シゲアキが、ゲストの作家の素顔や執筆の裏側を探求する、物書きによる物書きの為のバラエティ。",
                "start_hour": 10, 
                "start_min": 53,
                "duration": 57
            },
            "6":{
                "title": "FNN Live News days",
                "discription": "週末の昼も「ライブニュース　デイズ」をお見逃しなく。民放で最大級の全国ネットワークを持つFNNの記者が取材したニュースをお届けします。",
                "start_hour": 11, 
                "start_min": 50,
                "duration": 10
            },
        },
        "TOKYO MX":{
            "1":{
                "title": "テレビショッピング",
                "discription": "素肌つるつるセット【化粧品】",
                "start_hour": 8,
                "start_min": 0,
                "duration": 30
            },
            "2":{
                "title": "歴人めし", 
                "discription": "特平賀源内が鰻屋に頼まれて考えた宣伝文句が「土用の丑の日」。市販のかば焼きをふっくらさせる技と酢の物「うざく」を作る",
                "start_hour": 8,
                "start_min": 30,
                "duration": 15
            },
            "3":{
                "title": "比叡の光",
                "discription": "",
                "start_hour": 8,
                "start_min": 45,
                "duration": 15
            },
            "4":{
                "title": "テレビショッピング",
                "discription": "スレンダートーン フィットプラス【エクササイズグッズ】▽パーフェクトワン薬用ホワイトニングジェル【化粧品】▽野草酵素【健康食品】",
                "start_hour": 9, 
                "start_min": 0,
                "duration": 90
            },
            "5":{
                "title": "アート・ステージ",
                "discription": "大正、昭和初期に活動した日本画家、速水御舟。40年という短い生涯で数多くの、様々な作風の作品を残しました。生誕125年を記念した展覧会へのご招待もあります!",
                "start_hour": 10, 
                "start_min": 30,
                "duration": 25
            },
            "6":{
                "title": "東海林&amp;小堺のグッチョイス！",
                "discription": "",
                "start_hour": 10, 
                "start_min": 55,
                "duration": 5
            },
            "7":{
                "title": "週末ハッピーライフ！ お江戸に恋して",
                "discription": "ゲストには話題のイケメン集団「男劇団　青山表参道X」の西銘駿と飯島寛騎が登場!「もっと進め!江戸小町」は江戸川区・篠崎界隈をぶらり!中野区長も生出演!",
                "start_hour": 11, 
                "start_min": 0,
                "duration": 55
            },
            "8":{
                "title": "もっと目からウロコ！",
                "discription": "",
                "start_hour": 11, 
                "start_min": 55,
                "duration": 5
            }
        }
    }
    return render_template('schedule.html', 
                            date=date.today().strftime("%Y年%-m月%-d日"),
                            channel_titles=['テレビ東京', 'フジテレビ', 'TOKYO MX'],
                            times=range(7, 24),
                            schedule_dict=schedule_dict)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3333)

# または、以下を実行
# export FLASK_APP = app.py
# flask run