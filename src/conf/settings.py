import os

THEATER_DATA_DIR_PATH = "theater_data"
THEATER_DATA_JSON_FILE_NAME = "theater_data"

SCHEDULE_DIR_PATH = 'schedule'
SCHEDULE_CSV_FILE_NAME = 'all_schedule'

# データの最終取得日からこの日数以上経過していたら、再度Webスクレイピングを行う
UPDATE_DAYS_DELTA = 30 