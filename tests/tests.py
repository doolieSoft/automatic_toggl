import datetime
import time
import unittest
import random

TEST_RAPPORT_FOLDER = "test_rapport\\"

TACHE_DIVERSE = "Tâche diverse"

DURATION = 'duration'

PROJECT = 'project'

STOP = 'stop'

START = 'start'

EXE = 'exe'


class Automatic_Toggl(object):
    def __init__(self):
        self.titles = {}
        self.current_exe = None
        self.current_title = None
        self.current_project = None
        self.current_start_datetime = None
        self.current_stop_datetime = None
        self.app_logged = {}
        self.HEADER_RAPPORT = "Email,Description,Project,Start date,Start time,Duration"
        self.load_app_logged()

    def load_app_logged(self):

        f_app_logged = open("app_logged.csv", "r", encoding="utf8")
        i = 0
        for line in f_app_logged:
            if i == 0:
                i += 1
                continue

            app, project, default_title = line.split(";")
            self.app_logged[app] = {}
            self.app_logged[app]['project'] = project
            self.app_logged[app]['default_title'] = default_title.rstrip("\n")

        f_app_logged.close()

    def start_log(self, title, exe, start_datetime):

        if exe in self.app_logged:
            self.current_exe = exe
            self.current_start_datetime = start_datetime
            self.current_stop_datetime = None
            self.current_project = self.app_logged[exe]['project']
            if self.app_logged[exe]['default_title'] == "":
                self.current_title = title
            else:
                self.current_title = self.app_logged[exe]['default_title']
        else:
            self.current_exe = None
            self.current_project = None
            self.current_start_datetime = None
            self.current_stop_datetime = None

    def stop_log(self, stop_datetime=None):
        if self.current_start_datetime is None or stop_datetime is None or self.current_exe is None:
            # TODO lancer une exception
            return

        if self.current_title not in self.titles:
            self.titles[self.current_title] = []

        self.titles[self.current_title].append(
            {
                START: self.current_start_datetime
                , STOP: stop_datetime
                , EXE: self.current_exe
                , DURATION: stop_datetime - self.current_start_datetime
                , PROJECT: self.current_project
            })

        self.current_title = None
        self.current_exe = None
        self.current_start_datetime = None
        self.current_stop_datetime = None

    def hours_minutes_seconds(self, td):
        return td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60

    def get_current_recorded_title_and_exe(self):
        return self.current_exe, self.current_title

    def get_log_content(self):
        return self.titles.items()

    def get_usage(self, datetime_from, datetime_until, title, exe=None):
        titles_time_used_between = self.get_log(datetime_from, datetime_until, exe, title)
        total_time_used = datetime.timedelta()

        # TODO check que title est bien dans le tableau ou bien le tableau est vide et donc pas de prob.. à tester
        for line_detail in titles_time_used_between[title]:
            total_time_used += line_detail['duration']

        return total_time_used

    def get_usages(self, datetime_from, datetime_until, reverse=True):
        titles_time_used_between = self.get_log(datetime_from, datetime_until)
        result = {}

        for title in titles_time_used_between:
            result[title] = self.get_usage(datetime_from, datetime_until, title=title)

        if reverse is True:
            s = [(title, result[title]) for title in
                 sorted(result, key=lambda e: (-result[e], e))]
        else:
            s = [(title, result[title]) for title in
                 sorted(result, key=lambda e: (result[e], e))]
        return s

    def get_log(self, datetime_from, datetime_until, exe=None, title=None):
        log_between_datetimes = self.get_log_between_datetimes(datetime_from, datetime_until)
        result = {}
        if title is None and exe is None:
            return log_between_datetimes

        if title is not None and exe is not None:
            title_result = {}
            title_result[title] = [x for x in log_between_datetimes[title]]
            result = {title: title_result[t] for t in title_result for line in
                      title_result[t] if line['exe'] == exe}
            return result

        if exe is not None:
            result = {t: log_between_datetimes[t] for t in log_between_datetimes for line in
                      log_between_datetimes[t] if line['exe'] == exe}
            return result

        if title is not None:
            result[title] = [x for x in log_between_datetimes[title]]
            return result

    def get_log_between_datetimes(self, datetime_from, datetime_until):
        titles_time_used_between = {}

        for title_detail in self.get_log_content():
            for line_detail in title_detail[1]:
                if line_detail['start'] >= datetime_from and line_detail['stop'] <= datetime_until:
                    if title_detail[0] not in titles_time_used_between:
                        titles_time_used_between[title_detail[0]] = []
                    titles_time_used_between[title_detail[0]].append(line_detail)
        return titles_time_used_between

    def get_exe_used_between_2_datetimes(self, datetime_from, datetime_until):
        result = []
        titles_used_between_2_datetimes = self.get_log(datetime_from, datetime_until)
        for title in titles_used_between_2_datetimes:
            for title_detail in titles_used_between_2_datetimes[title]:
                if title_detail['exe'] not in result:
                    result.append(title_detail['exe'])
        return result

    def replace_title_by_exe_default_title_if_used_less_than(self, titles_time_used_between_2_datetimes,
                                                             sorted_titles_used, lowest_usage_limit):
        result = titles_time_used_between_2_datetimes.copy()
        # TODO soit init une liste de default title par exe au niveau de la classe, ou alors passer le tableau ici
        for title_detail in sorted_titles_used:
            if title_detail[1].seconds < lowest_usage_limit:
                result["default app title"] = result.pop(title_detail[0])
        return result

    def load_prep_rapport(self, f_prepa):
        i = 0
        for line in f_prepa:
            if i == 0:
                i += 1
                continue

            exe, email, description, project, start_date, start_time, duration = line.split(",")
            start_datetime = datetime.datetime.strptime(start_date + " " + start_time, "%Y-%m-%d %H:%M:%S")
            self.start_log(description, exe, start_datetime)
            hours, minutes, seconds = duration.split(":")
            stop_datetime = start_datetime + datetime.timedelta(hours=int(hours), minutes=int(minutes),
                                                                seconds=int(seconds))
            self.stop_log(stop_datetime)

    def get_most_used_titles(self, datetime_from, datetime_until):
        result = []
        titles_usages = self.get_usages(datetime_from, datetime_until)
        titles_usages_seconds = [x[1] for x in titles_usages]

        total_seconds = sum([x.seconds for x in titles_usages_seconds])
        for title_usage in titles_usages:
            if title_usage[1].seconds / total_seconds > 0.01:
                if title_usage[0] not in result:
                    result.append(title_usage[0])

        print()
        return result

    def generate_rapport(self, datetime_from, datetime_until, most_used_title):
        most_used_titles_grouped = {}
        total_not_in_most_used = 0
        total_in_most_used = 0

        # print("Most used title : ")
        # for title in most_used_title:
        #    print("{} used {} ".format(title, self.get_usage(datetime_from, datetime_until, title)))

        # print()
        for title in self.titles:
            if title in most_used_title:
                most_used_titles_grouped[title] = self.titles[title]
                total_in_most_used += len(self.titles[title])
            else:
                lines = []
                for line in self.titles[title]:
                    line['old_title'] = title
                    lines.append(line)

                if TACHE_DIVERSE not in most_used_titles_grouped:
                    most_used_titles_grouped[TACHE_DIVERSE] = lines
                    total_not_in_most_used += len(self.titles[title])
                else:
                    most_used_titles_grouped[TACHE_DIVERSE].extend(lines)
                    total_not_in_most_used += len(self.titles[title])

        sorted_default_title_log = sorted(most_used_titles_grouped[TACHE_DIVERSE], key=lambda e: e[START])
        compressed_default_title_log = []
        i = 0
        while i < len(sorted_default_title_log) - 1:
            current_start = sorted_default_title_log[i][START]
            current_duration = sorted_default_title_log[i][DURATION]
            total_duration_to_add = current_duration
            merged = False

            n = 1
            while current_start + total_duration_to_add == sorted_default_title_log[i + n][START]:
                total_duration_to_add += sorted_default_title_log[i + n][DURATION]
                merged = True
                n += 1
                if not i + n < len(sorted_default_title_log):
                    break

            new_line_default_title_log = sorted_default_title_log[i]
            if merged == True:
                new_line_default_title_log[DURATION] = total_duration_to_add
                new_line_default_title_log[STOP] = new_line_default_title_log[START] + new_line_default_title_log[
                    DURATION]
                compressed_default_title_log.append(new_line_default_title_log)
                i += n
            else:
                compressed_default_title_log.append(sorted_default_title_log[i])
                i += 1

        most_used_titles_grouped[TACHE_DIVERSE] = compressed_default_title_log
        total_default_title_grouped = len(compressed_default_title_log)

        lines = []
        for title in most_used_titles_grouped:
            for line_detail in most_used_titles_grouped[title]:
                line_detail['title'] = title
                lines.append(line_detail)

        # for line in sorted(lines, key=lambda e: e['start']):
        #    print(line)

        print("total_in_most_used = " + str(total_in_most_used))
        print("total_not_in_most_used = " + str(total_not_in_most_used))
        print("then they are grouped : total_default_title_grouped = " + str(total_default_title_grouped))
        print("grand total most_used_titles_grouped = " + str(len(lines)))
        f_rapport = open(TEST_RAPPORT_FOLDER + "rapport-2019-11-25.csv", "w")
        f_rapport.write(self.HEADER_RAPPORT + "\n")

        for line in sorted(lines, key=lambda e: e['start']):

            f_rapport.write(self.get_line_from_dict(line) + "\n")
            if 'old_title' in line:
                print(
                    "Old_Title ... stefano.crapanzano@chuliege.be,{},{},{},{},{}".format(line['title'], line["project"],
                                                                                         line[START],
                                                                                         line[DURATION],
                                                                                         line['old_title']))
            else:
                print("stefano.crapanzano@chuliege.be,{},{},{},{}".format(line['title'], line["project"], line[START],
                                                                           line[DURATION]))

        f_rapport.close()

    def load_prep_rapports(self, list_of_files_to_load):
        for file in list_of_files_to_load:
            f_prepa = open(file, "r", encoding="utf8")
            self.load_prep_rapport(f_prepa)
            f_prepa.close()

    def get_line_from_dict(self, line):
        date_from = line['start'].strftime("%Y-%m-%d")
        time_from = line['start'].strftime("%H:%M:%S")
        hours, minutes, seconds = self.hours_minutes_seconds(line['duration'])
        duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                                 minutes,
                                                 seconds)
        return "stefano.crapanzano@chuliege.be" \
               + "," + line['title'] \
               + "," + line['project'] \
               + "," + date_from \
               + "," + time_from \
               + "," + duration


################################### UNITTEST START ###################################


class TestAutomaticToggl(unittest.TestCase):

    def setUp(self):
        self.toggl = Automatic_Toggl()
        self.start_datetime = datetime.datetime.now()
        year, month, day = self.start_datetime.strftime("%Y"), self.start_datetime.strftime(
            "%m"), self.start_datetime.strftime("%d")
        self.today = "{}-{}-{}".format(str(year), str(month), str(day))

        self.init_toggl()
        self.golden_usages = [('Toto va à la ferme 1', datetime.timedelta(0, 9122)),
                              ('Lecture documentation', datetime.timedelta(0, 9120)),
                              ('Toto va à la ferme 3', datetime.timedelta(0, 8450)),
                              ('Navigation système de fichier', datetime.timedelta(0, 2168))]

        self.golden_reversed_usages = [('Navigation système de fichier', datetime.timedelta(0, 2168)),
                                       ('Toto va à la ferme 3', datetime.timedelta(0, 8450)),
                                       ('Lecture documentation', datetime.timedelta(0, 9120)),
                                       ('Toto va à la ferme 1', datetime.timedelta(0, 9122))]

    def init_toggl(self):
        self.titles = [
            ("Toto va à la ferme 1", "08:30:00", "08:35:00", "chrome.exe")
            , ("Toto va à la ferme 2", "08:35:00", "08:37:00", "firefox.exe")
            , ("Toto va à la ferme 1", "08:37:00", "08:43:00", "chrome.exe")
            , ("Toto va à la ferme 1", "08:43:00", "10:43:02", "chrome.exe")
            , ("Toto va à la ferme 3", "10:43:02", "12:44:00", "chrome.exe")
            , ("Toto va à la ferme 2", "12:44:00", "14:46:00", "firefox.exe")
            , ("a", "14:46:00", "14:46:02", "explorer.exe")
            , ("b", "14:46:02", "14:46:04", "explorer.exe")
            , ("c", "14:46:04", "14:46:06", "explorer.exe")
            , ("d", "14:46:06", "14:46:08", "explorer.exe")
            , ("Toto va à la ferme 3", "14:46:08", "14:59:00", "chrome.exe")
            , ("Toto va à la ferme 4", "14:59:00", "15:35:00", "explorer.exe")
            , ("Toto va à la ferme 1", "15:35:00", "15:56:00", "chrome.exe")
            , ("Toto va à la ferme 5", "15:56:00", "16:25:00", "mozi.exe")
            , ("Toto va à la ferme 3", "16:25:00", "16:32:00", "chrome.exe")
            , ("Toto va à la ferme 2", "16:32:00", "17:00:00", "firefox.exe")
        ]
        for title_tuple in self.titles:
            start_datetime = datetime.datetime.strptime(self.today + " " + title_tuple[1], "%Y-%m-%d %H:%M:%S")
            self.toggl.start_log(title=title_tuple[0], exe=title_tuple[3],
                                 start_datetime=start_datetime)
            stop_datetime = datetime.datetime.strptime(self.today + " " + title_tuple[2], "%Y-%m-%d %H:%M:%S")

            self.toggl.stop_log(stop_datetime)

    def test_can_record_title_and_exe(self):
        self.toggl.start_log(title="Toto va à la ferme", exe="chrome.exe",
                             start_datetime=self.start_datetime)
        self.assertTrue("Toto va à la ferme",
                        "chrome.exe" ==
                        self.toggl.get_current_recorded_title_and_exe())

    def test_can_stop_timer(self):
        nb_seconds = 2
        self.toggl.start_log(title="Toto va à la ferme", exe="chrome.exe", start_datetime=self.start_datetime)
        stop_datetime = self.start_datetime + datetime.timedelta(seconds=nb_seconds)
        self.toggl.stop_log(stop_datetime)
        result_nb_sec = self.toggl.get_usage(self.start_datetime, stop_datetime, title="Toto va à la ferme").seconds
        self.assertTrue(nb_seconds == result_nb_sec)

    def test_can_get_usage_by_title(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        title_usage = self.toggl.get_usage(datetime_from, datetime_until, title="Toto va à la ferme 1")
        self.assertTrue(title_usage == datetime.timedelta(days=0, hours=2, minutes=32, seconds=2))

    def test_can_get_usages(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        titles_usages = self.toggl.get_usages(datetime_from, datetime_until)
        self.assertTrue(titles_usages == self.golden_usages)

        reversed_titles_usages = self.toggl.get_usages(datetime_from, datetime_until, reverse=False)
        self.assertTrue(reversed_titles_usages == self.golden_reversed_usages)

    def test_can_get_log_between_2_datetimes(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        titles_used_between_dates = self.toggl.get_log(datetime_from, datetime_until)
        self.assertTrue(len(titles_used_between_dates) == 4)

    def test_can_get_log_between_2_datetimes_for_one_title_of_one_exe(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        log_in_datetimes = self.toggl.get_log(datetime_from, datetime_until, title="Toto va à la ferme 1",
                                              exe="chrome.exe")
        self.assertTrue(len(log_in_datetimes) == 1)

    def test_can_get_log_between_2_datetimes_for_one_title(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        title_log = self.toggl.get_log(datetime_from, datetime_until, title="Toto va à la ferme 1")
        self.assertTrue(len(title_log) == 1)

        # TODO verif contenu de title_detail

    def test_can_get_log_between_2_datetimes_for_one_exe(self):
        datetime_from = datetime.datetime.strptime("{} 12:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 16:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        exe_log_between_dates = self.toggl.get_log(datetime_from, datetime_until, exe="explorer.exe")
        self.assertTrue(len(exe_log_between_dates) == 1)

    def test_can_get_exe_between_2_datetimes(self):
        datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("{} 10:50:00".format(self.today), "%Y-%m-%d %H:%M:%S")

        exe_used_between_dates = self.toggl.get_exe_used_between_2_datetimes(datetime_from, datetime_until)
        self.assertTrue(len(exe_used_between_dates) == 2)

    def test_can_load_prep_rapport(self):
        automatic_toggl = Automatic_Toggl()

        list_of_files_to_load = [(TEST_RAPPORT_FOLDER + "prep_rapport-2019-10-24.csv")
                                 # "prep_rapport-2019-10-24-Lot.csv",
                                 # "prep_rapport-2019-10-24-Lot1.csv",
                                 # "prep_rapport-2019-10-24-Lot2.csv"
                                 ]

        automatic_toggl.load_prep_rapports(list_of_files_to_load)
        self.assertTrue(len(automatic_toggl.get_log_content()) > 0)

    def test_can_generate_rapport(self):
        automatic_toggl = Automatic_Toggl()

        datetime_from = datetime.datetime.strptime("2019-10-24 08:30:00", "%Y-%m-%d %H:%M:%S")
        datetime_until = datetime.datetime.strptime("2019-10-24 17:00:00", "%Y-%m-%d %H:%M:%S")

        list_of_files_to_load = [TEST_RAPPORT_FOLDER + "prep_rapport-2019-10-24.csv",
                                 TEST_RAPPORT_FOLDER + "prep_rapport-2019-10-24-Lot.csv",
                                 TEST_RAPPORT_FOLDER + "prep_rapport-2019-10-24-Lot1.csv",
                                 TEST_RAPPORT_FOLDER + "prep_rapport-2019-10-24-Lot2.csv"
                                 ]

        automatic_toggl.load_prep_rapports(list_of_files_to_load)
        most_used_titles = automatic_toggl.get_most_used_titles(datetime_from, datetime_until)

        automatic_toggl.generate_rapport(datetime_from=datetime_from, datetime_until=datetime_until,
                                         most_used_title=most_used_titles)

    # def test_can_replace_title_if_total_time_used_is_less_than_timedelta_param(self):
    #     datetime_from = datetime.datetime.strptime("{} 08:30:00".format(self.today), "%Y-%m-%d %H:%M:%S")
    #     datetime_until = datetime.datetime.strptime("{} 17:00:00".format(self.today), "%Y-%m-%d %H:%M:%S")
    #
    #     titles_usages = self.toggl.get_usages(datetime_from, datetime_until)
    #     titles_usages_seconds = [x[1].seconds for x in titles_usages]
    #     # print(titles_usages)
    #     total_seconds = sum(titles_usages_seconds)
    #     for title_usage in titles_usages:
    #         # print("{} / {} = {}".format(title_usage[1].seconds, total_seconds,
    #         #                           str(title_usage[1].seconds / total_seconds)))
    #         pass
    #
    #     # self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
