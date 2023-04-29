import json

# TODO: クラスの説明を詳しく書く
class Theater():
    """
    映画館クラス
    プログラムオブジェクトのリストを持つ
    それぞれの映画館クラスの親クラスとなる
    """
    def __init__(self):

        self.theater_class_name = self.__class__.__name__
        
        # 映画館の情報をJSONファイルから読み込む
        with open('theaters_settings.json') as f:
            theaters_dict = json.load(f)
        
            self.theater_name = theaters_dict[self.theater_class_name]["THEATER_NAME"]
            self.theater_name_en = theaters_dict[self.theater_class_name]["THEATER_NAME_EN"]
            self.theater_url = theaters_dict[self.theater_class_name]["THEATER_URL"]
            self.theater_location = theaters_dict[self.theater_class_name]["THEATER_LOCATION"]

        # Programオブジェクトのリストを初期化
        self.program_object_list = []

    # encode (theater_object -> theater_dict)
    def get_dictionary(self):
        theater_dict = {
            "theater_name": self.theater_name,
            "theater_name_en": self.theater_name_en,
            "theater_url": self.theater_url,
            "location": self.theater_location,
            "programs": self.get_programs_dict()
        }

        return theater_dict

    # encode (program_object_list -> programs_dict)
    def get_programs_dict(self):

        programs_dict = {}
        for program_object in self.program_object_list:
            programs_dict[program_object.program_id] = program_object.get_dictionary()

        return programs_dict

class Program():
    """
    プログラムクラス
    映画オブジェクトのリストを持つ
    """
    def __init__(self, program_id = "", program_title="", program_duration=(), program_url="", program_movie_list_url="", movie_object_list=[]):
        self.program_id = program_id
        self.program_title = program_title
        self.program_duration = program_duration
        self.program_url = program_url
        self.program_movie_list_url = program_movie_list_url
        self.movie_object_list = movie_object_list # Movieオブジェクトのリスト

    # encode (program_object -> program_dict)
    def get_dictionary(self):
        """
        Programオブジェクト(自分)を辞書形式にして返す
        """
        program_dict = {
            "program_title": self.program_title, 
            "program_duration": self.program_duration,
            "program_url": self.program_url,
            "program_movie_list_url": self.program_movie_list_url,
            "movies": self.get_movies_dict() # Movieオブジェクトのリスト
        }

        return program_dict

    # encode (movie_object_list -> movies_dict)
    def get_movies_dict(self):
        """
        自分のMovieオブジェクトのリストを辞書にして返す
        """
        
        movies_dict = {}
        for movie_object in self.movie_object_list:
            movies_dict[movie_object.movie_id] = movie_object.get_dictionary()
        
        return movies_dict
  
class Movie():
    """
    映画クラス
    映画に関する情報をもつ
    """
    def __init__(self, movie_id=None, movie_title=None, movie_timedelta_minute_str=None, movie_url=None, movie_type=None, movie_staff=None, movie_synopsis=None, movie_start_datetime_str_list=None):
        self.movie_id = movie_id
        self.movie_title = movie_title
        self.movie_url = movie_url
        self.movie_timedelta_minute_str = movie_timedelta_minute_str
        self.movie_type = movie_type
        self.movie_staff = movie_staff
        self.movie_synopsis = movie_synopsis
        self.movie_start_datetime_str_list = movie_start_datetime_str_list or []

    # encode (movie_object -> movie_dict)
    def get_dictionary(self):
        """
        Movieオブジェクト(自分)を辞書形式にして返す
        """
        movie_dict = {
            "movie_title": self.movie_title,
            "movie_url": self.movie_url,
            "movie_timedelta_minute_str": self.movie_timedelta_minute_str,
            "movie_type": self.movie_type,
            "movie_staff": self.movie_staff,
            "movie_synopsis": self.movie_synopsis,
            "movie_start_datetime_str_list": self.movie_start_datetime_str_list
        }

        return movie_dict