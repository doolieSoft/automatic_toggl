import datetime
import time
import unittest
import random


class Automatic_Toggl(object):
    def __init__(self):
        self.titles = {}
        self.current_app_name = None
        self.current_title = None
        self.current_start_datetime = None
        self.current_stop_datetime = None

    def start_log(self, title, app_name, start_datetime):
        self.current_app_name = app_name
        self.current_title = title
        self.current_start_datetime = start_datetime
        self.current_stop_datetime = None

    def get_current_recorded_app_name_and_title(self):
        return self.current_app_name, self.current_title

    def stop_log(self, stop_datetime=None):
        if self.current_start_datetime is None or stop_datetime is None or self.current_app_name is None:
            # TODO lancer une exception
            print("hello")
            pass

        if self.current_title not in self.titles:
            self.titles[self.current_title] = []

        self.titles[self.current_title].append(
            {
                'start': self.current_start_datetime
                , 'stop': stop_datetime
                , 'app_name': self.current_app_name
                , 'duration': stop_datetime - self.current_start_datetime
            })

        self.current_title = None
        self.current_app_name = None
        self.current_start_datetime = None
        self.current_stop_datetime = None

    def get_title_time_used(self, title, titles_detail=None):

        total_time_used = datetime.timedelta()

        titles_detail_list = titles_detail

        if titles_detail is None:
            titles_detail_list = self.titles

        if title not in titles_detail_list:
            # TODO throw exception ... ou renvoyer 0 ... à voir
            print("hello")
            return None
            pass

        for line_detail in titles_detail_list[title]:
            total_time_used += line_detail['duration']

        return total_time_used

    def get_titles_time_used(self, titles_detail=None):
        result = {}
        titles_detail_list = titles_detail

        if titles_detail is None:
            titles_detail_list = self.titles

        for title in titles_detail_list:
            result[title] = self.get_title_time_used(title=title, titles_detail=titles_detail)

        return result

    def get_sorted_titles_by_time(self, titles_detail=None, reverse=False):

        titles_time_used = self.get_titles_time_used(titles_detail)

        s = [(title, titles_time_used[title]) for title in
             sorted(titles_time_used, key=lambda e: (titles_time_used[e], e), reverse=reverse)]
        return s

    def get_titles_detail(self):
        return self.titles.items()

    def get_title_detail(self, title, titles_detail=None):
        #TODO titles_detail doit etre utilise si pas à None
        if title not in self.titles:
            # TODO throw an exception...
            pass

        return self.titles[title]

    def hours_minutes_seconds(td):
        return td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60

    def get_titles_time_used_between(self, datetime_from, datetime_until):
        titles_time_used_between = {}
        for title_detail in self.get_titles_detail():
            for line_detail in title_detail[1]:
                if line_detail['start'] >= datetime_from and line_detail['stop'] <= datetime_until:
                    if title_detail[0] not in titles_time_used_between:
                        titles_time_used_between[title_detail[0]] = []
                    titles_time_used_between[title_detail[0]].append(line_detail)
                    print("Trouvé {} : {}".format(title_detail[0], str(line_detail)))

        return titles_time_used_between


################################### UNITTEST START ###################################


class TestAutomaticToggl(unittest.TestCase):

    def setUp(self):
        self.toggl = Automatic_Toggl()
        self.start_datetime = datetime.datetime.now()

    def test_can_record_title_and_app_name(self):
        self.toggl.start_log(title="Toto va à la ferme", app_name="chrome.exe",
                             start_datetime=self.start_datetime)
        self.assertTrue("Toto va à la ferme",
                        "chrome.exe" ==
                        self.toggl.get_current_recorded_app_name_and_title())

    def test_can_stop_timer(self):
        nb_seconds = 2
        self.toggl.start_log(title="Toto va à la ferme", app_name="chrome.exe",
                             start_datetime=self.start_datetime)
        stop_datetime = self.start_datetime + datetime.timedelta(seconds=nb_seconds)
        self.toggl.stop_log(stop_datetime)
        self.assertTrue(nb_seconds == self.toggl.get_title_time_used(title="Toto va à la ferme").seconds)

    def test_can_get_log_sorted_by_time(self):
        titles = [
            ("Toto va à la ferme 1", 10)
            , ("Toto va à la ferme 2", 20)
            , ("Toto va à la ferme 3", 30)
            , ("Toto va à la ferme 4", 70)
            , ("Toto va à la ferme 5", 50)
        ]

        start_datetime = self.start_datetime
        for app_tuple in titles:
            self.toggl.start_log(title=app_tuple[0], app_name="chrome.exe",
                                 start_datetime=start_datetime)
            stop_datetime = start_datetime + datetime.timedelta(seconds=app_tuple[1])
            start_datetime = stop_datetime

            self.toggl.stop_log(stop_datetime)

        sorted_titles_by_time = self.toggl.get_sorted_titles_by_time()
        sorted_titles_by_time_desc = self.toggl.get_sorted_titles_by_time(reverse=True)

        self.assertTrue(len(sorted_titles_by_time_desc) == 5)
        self.assertTrue("Toto va à la ferme 1" == sorted_titles_by_time[0][0])
        self.assertTrue("Toto va à la ferme 4" == sorted_titles_by_time_desc[0][0])

    def test_can_log_titles_multiple_times(self):
        titles = [
            ("Toto va à la ferme 1", 50)
            , ("Toto va à la ferme 2", 20)
            , ("Toto va à la ferme 1", 30)
            , ("Toto va à la ferme 3", 20)
            , ("Toto va à la ferme 2", 60)
            , ("Toto va à la ferme 2", 70)
            , ("Toto va à la ferme 3", 10)
            , ("Toto va à la ferme 4", 20)
            , ("Toto va à la ferme 1", 50)
            , ("Toto va à la ferme 5", 30)
            , ("Toto va à la ferme 3", 40)
            , ("Toto va à la ferme 2", 60)
        ]
        start_of_test_start_datetime = self.start_datetime
        start_datetime = start_of_test_start_datetime

        for app_tuple in titles:
            self.toggl.start_log(title=app_tuple[0], app_name="chrome.exe",
                                 start_datetime=start_datetime)
            stop_datetime = start_datetime + datetime.timedelta(seconds=app_tuple[1])
            start_datetime = stop_datetime

            self.toggl.stop_log(stop_datetime)

        title_detail = self.toggl.get_title_detail(title="Toto va à la ferme 1")

        self.assertTrue(len(title_detail) == 3)
        sorted_titles_by_time = self.toggl.get_sorted_titles_by_time()
        sorted_titles_by_time_desc = self.toggl.get_sorted_titles_by_time(reverse=True)

        self.assertTrue(len(sorted_titles_by_time_desc) == 5)
        self.assertTrue("Toto va à la ferme 4" == sorted_titles_by_time[0][0])
        self.assertTrue("Toto va à la ferme 2" == sorted_titles_by_time_desc[0][0])

        # TODO verif contenu de title_detail

    def test_can_get_apps_title_between_2_datetime(self):
        apps_title = [
            ("Toto va à la ferme 1", 50)
            , ("Toto va à la ferme 2", 20)
            , ("Toto va à la ferme 1", 30)
            , ("Toto va à la ferme 3", 20)
            , ("Toto va à la ferme 2", 60)
            , ("Toto va à la ferme 2", 40)
            , ("Toto va à la ferme 3", 10)
            , ("Toto va à la ferme 4", 20)
            , ("Toto va à la ferme 1", 50)
            , ("Toto va à la ferme 5", 30)
            , ("Toto va à la ferme 3", 40)
            , ("Toto va à la ferme 2", 60)
        ]
        start_of_test_start_datetime = self.start_datetime
        start_datetime = start_of_test_start_datetime

        year, month, day = start_datetime.strftime("%Y"), start_datetime.strftime("%m"), start_datetime.strftime("%d")
        datetime_from = start_datetime.strptime("{}-{}-{} 08:30:00".format(year, month, day), "%Y-%m-%d %H:%M:%S")
        datetime_until = start_datetime.strptime("{}-{}-{} 08:34:00".format(year, month, day), "%Y-%m-%d %H:%M:%S")

        start_datetime = datetime_from
        print(str(datetime_from) + " -> " + str(datetime_until))

        for app_tuple in apps_title:
            self.toggl.start_log(title=app_tuple[0], app_name="chrome.exe",
                                 start_datetime=start_datetime)
            stop_datetime = start_datetime + datetime.timedelta(seconds=app_tuple[1])
            start_datetime = stop_datetime

            self.toggl.stop_log(stop_datetime)

        titles_used_between_dates = self.toggl.get_titles_time_used_between(datetime_from, datetime_until)
        sorted_titles_by_time_desc = self.toggl.get_sorted_titles_by_time(titles_used_between_dates, reverse=True)
        self.assertTrue(len(titles_used_between_dates) == 3)
        print(sorted_titles_by_time_desc)


if __name__ == '__main__':
    unittest.main()
