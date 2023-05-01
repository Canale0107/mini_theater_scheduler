import os

CONF_DIR = os.path.dirname(__file__)
UPDATE_DATABASE_DIR = os.path.dirname(CONF_DIR)
SRC_DIR = os.path.dirname(UPDATE_DATABASE_DIR)
APP_DIR = os.path.dirname(SRC_DIR)
DATA_DIR = os.path.join(APP_DIR, "data")

THEATER_DATA_DIR_PATH = os.path.join(DATA_DIR, "theater_data")
THEATER_DATA_JSON_FILE_NAME = "theater_data"

SCHEDULE_DIR_PATH = os.path.join(DATA_DIR, "schedule")
SCHEDULE_CSV_FILE_NAME = 'all_schedule'

# データの最終取得日からこの日数以上経過していたら、再度Webスクレイピングを行う
UPDATE_DAYS_DELTA = 30 