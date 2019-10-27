import datetime
import time
import unittest


class Automatic_Toggl(object):
    def __init__(self):
        self.apps_logged = {}
        self.current_app_name = None
        self.current_app_title = None
        self.current_start_datetime = None
        self.current_timedelta = None

    def is_app_logged(self, app_name):
        if app_name in self.apps_logged:
            return True
        return False

    def get_apps_logged(self):
        return self.apps_logged

    def start_log(self, app_title, app_name):
        if app_name not in self.apps_logged:
            self.apps_logged[app_name] = {}
        if app_title not in self.apps_logged[app_name]:
            self.apps_logged[app_name][app_title] = {}

        start = datetime.datetime.now()
        self.current_app_name = app_name
        self.current_app_title = app_title
        self.current_start_datetime = start
        self.apps_logged[app_name][app_title]['start'] = start
        self.apps_logged[app_name][app_title]['duration'] = None

    def get_current_recorded_app_name_and_title(self):
        return self.current_app_name, self.current_app_title

    def get_current_timedelta(self):
        now = datetime.datetime.now()
        return (now - self.current_start_datetime)

    def stop_log(self):
        stop = datetime.datetime.now()
        self.apps_logged[self.current_app_name][self.current_app_title]['duration'] = stop - self.apps_logged[
            self.current_app_name][self.current_app_title]['start']

        self.current_start_datetime = None
        self.current_app_title = None
        self.current_app_name = None
        self.current_start_datetime = None

    def get_app_title_time_used(self, app_title, app_name):
        total_time_used = datetime.timedelta()

        for app_title in self.apps_logged[app_name]:
            total_time_used += self.apps_logged[app_name][app_title]['duration']

        return total_time_used


class TestAutomaticToggl(unittest.TestCase):

    def setUp(self):
        self.auto_toggl = Automatic_Toggl()
        # automatic_toggl_app.add_app_logged("chrome.exe")

    def test_can_record_app_title_and_app_name(self):
        self.auto_toggl.start_log(app_title="Toto va à la ferme", app_name="chrome.exe")
        self.assertTrue("Toto va à la ferme",
                        "chrome.exe" ==
                        self.auto_toggl.get_current_recorded_app_name_and_title())

    def test_can_stop_timer(self):
        nb_seconds = 2
        self.auto_toggl.start_log(app_title="Toto va à la ferme", app_name="chrome.exe")
        time.sleep(nb_seconds)
        self.auto_toggl.stop_log()
        self.assertTrue(nb_seconds == self.auto_toggl.get_app_title_time_used(app_title="Toto va à la ferme",
                                                                              app_name="chrome.exe").seconds)
