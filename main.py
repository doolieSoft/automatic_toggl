import signal
import sys

import wmi
from win32gui import GetWindowText, GetForegroundWindow
import datetime
import win32process, win32gui, time
import pprint
import os
import glob

c = wmi.WMI()

PREP_RAPPORT_FOLDER = "prep_rapport\\"
RAPPORT_FOLDER = "rapport\\"

EMAIL_ACCOUNT = "stefano.crapanzano@chu.ulg.ac.be"

HEADER_PREP_RAPPORT = "Active app,Email,Description,Project,Start date,Start time,Duration"

HEADER_RAPPORT = "Email,Description,Project,Start date,Start time,Duration"

NB_COLUMN_IN_PREP_RAPPORT = 7

rapport = {}
start = datetime.datetime.now()
active_app = None
current_title = None

app_logged = {}
lines_to_keep_in_prep_rapport = []


def load_app_logged():
    global line, app, project
    f_app_logged = open("app_logged.csv", "r", encoding="utf8")
    i = 0
    for line in f_app_logged:
        if i == 0:
            i += 1
            continue

        app, project, default_title = line.split(";")
        app_logged[app] = {}
        app_logged[app]['project'] = project
        app_logged[app]['default_title'] = default_title.rstrip("\n")
    f_app_logged.close()


def get_default_title_for_app(app):
    if app in app_logged.keys():
        return app_logged[app]['default_title']
    else:
        return ""


def get_active_app_name_and_title():
    active_app = None
    while active_app is None:
        active_app = get_app_name(win32gui.GetForegroundWindow())
        time.sleep(0.1)

    default_title = get_default_title_for_app(active_app)

    if default_title != "":
        title = default_title
    else:
        title = ""
        while len(title) == 0:
            title = GetWindowText(GetForegroundWindow())
            title = title.strip()
            time.sleep(0.1)

        title = title.strip().replace(",", " ").replace("\"", " ")

    return active_app, title


def log_running_applications():
    global current_title
    global active_app
    global start
    global rapport
    global app_logged

    pprint.pprint(app_logged)

    active_app, new_title = get_active_app_name_and_title()

    current_title = new_title
    print()
    print(current_title)

    start = start_timer(current_title)

    while True:
        time.sleep(1.0)
        current_app = active_app
        active_app, new_title = get_active_app_name_and_title()

        if current_app != active_app:
            print("Switching to " + active_app)
        else:
            print(current_app)

        if current_title != new_title:
            time_used = stop_timer(current_title)
            hours, minutes, seconds = hours_minutes_seconds(time_used)

            duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                                     minutes,
                                                     seconds)

            print("{0} --> time used : {1}".format(current_title, duration))
            print()
            print(new_title)
            start = start_timer(new_title)

            current_title = new_title


def start_timer(description):
    print()
    start = datetime.datetime.now()

    if description not in rapport.keys():
        rapport[description] = []
        rapport[description].append({})
        rapport[description][-1]['exe'] = active_app
        rapport[description][-1]['start_date'] = start.strftime("%Y-%m-%d")
        rapport[description][-1]['start_time'] = start.strftime("%H:%M:%S")
        rapport[description][-1]['duration'] = datetime.timedelta()
    else:
        rapport[description].append({})
        rapport[description][-1]['exe'] = active_app
        rapport[description][-1]['start_date'] = start.strftime("%Y-%m-%d")
        rapport[description][-1]['start_time'] = start.strftime("%H:%M:%S")
        rapport[description][-1]['duration'] = datetime.timedelta()

    print("In start timer")
    print(description)
    print(rapport[description][-1]['start_time'])
    print()

    return start


def stop_timer(current_title):
    global start
    global rapport
    global active_app
    stop_time = datetime.datetime.now()
    time_used = stop_time - start
    rapport[current_title][-1]['duration'] += time_used

    print()
    print("In stop timer")
    print(current_title)
    print(rapport[current_title][-1]['start_time'])
    print(time_used)
    print()
    return time_used


def generate_prep_rapport(*args, **kwargs):
    global current_title
    global start
    global rapport
    global app_logged
    global lines_to_keep_in_prep_rapport

    load_app_logged()

    print(active_app)
    corrected_current_title = get_default_title_for_app(active_app)
    if corrected_current_title != "":
        current_title = corrected_current_title
    print(current_title)

    time_used = stop_timer(current_title)
    hours, minutes, seconds = hours_minutes_seconds(time_used)
    duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                             minutes,
                                             seconds)
    print("{0} --> time used : {1}".format(current_title, duration))

    print()

    f_prep_rapport = open(PREP_RAPPORT_FOLDER + "prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "w",
                          encoding="utf8")
    f_prep_rapport.write(HEADER_PREP_RAPPORT + "\n")

    print(HEADER_PREP_RAPPORT)

    for key, value in rapport.items():
        for i in range(len(value)):
            hours, minutes, seconds = hours_minutes_seconds(value[i]['duration'])
            duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                                     minutes,
                                                     seconds)
            title = key
            if value[i]['exe'] in app_logged.keys():
                project = app_logged[value[i]['exe']]['project']
            else:
                project = ""

            f_prep_rapport.write(
                value[i]['exe'] + "," + EMAIL_ACCOUNT + "," + title + "," + project + "," +
                value[i]['start_date'] + "," +
                value[i]['start_time'] + "," + duration + "\n")
            print(
                value[i]['exe'] + "," + EMAIL_ACCOUNT + "," + title + "," + project + "," +
                value[i][
                    'start_date'] + "," +
                value[i]['start_time'] + "," + duration)

    f_prep_rapport.close()
    print()

    generate_rapport_from_prep_rapport()
    sys.exit(0)


def generate_rapport_from_prep_rapport():
    lines_to_keep_in_rapport = []
    current_time = datetime.datetime.now()
    prep_rapport_files = [PREP_RAPPORT_FOLDER + "prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv"]
    prep_rapport_files.extend(
        sorted(glob.glob(PREP_RAPPORT_FOLDER + "prep_rapport-" + current_time.strftime("%Y-%m-%d") + "-Lot*.csv"),
               reverse=False))

    for prep_rapport_file in prep_rapport_files:
        f_prep_rapport = open(prep_rapport_file, "r", encoding="utf8")
        i = 0

        for line in f_prep_rapport:
            if i == 0:
                i += 1
                continue
            if len(line.split(",")) != NB_COLUMN_IN_PREP_RAPPORT:
                print("Probleme avec la ligne. Elle ne contient pas assez de colonne : " + line)
                os.system("pause")
                continue
            app, email, description, project, start_date, start_time, duration = line.split(",")
            if app in app_logged.keys():
                if app_logged[app]['default_title'] != "" and description != app_logged[app]['default_title']:
                    description = get_default_title_for_app(app)

                hours, minutes, seconds = duration.split(":")
                td = datetime.timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds))
                if td.seconds >= 2:
                    lines_to_keep_in_rapport.append(
                        email + "," + description + "," + project + "," + start_date + "," + start_time + "," + duration)
        f_prep_rapport.close()

    f_rapport = open(RAPPORT_FOLDER + "rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "w", encoding="utf8")
    f_rapport.write(HEADER_RAPPORT + "\n")

    print(HEADER_RAPPORT)
    for line in lines_to_keep_in_rapport:
        f_rapport.write(line)
        print(line.rstrip("\n"))

    f_rapport.close()


def get_app_name(hwnd):
    """Get application filename given hwnd."""
    exe = ""
    try:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        for p in c.query('SELECT Name FROM Win32_Process WHERE ProcessId = %s' % str(pid)):
            exe = p.Name
            break
    except:
        return None
    else:
        return exe

def hours_minutes_seconds(td):
    return td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60


if __name__ == '__main__':
    load_app_logged()

    signal.signal(signal.SIGINT, generate_prep_rapport)

    start = datetime.datetime.now()
    current_time = datetime.datetime.now()

    prep_name = "prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv"
    prep_new_name = "prep_rapport-" + current_time.strftime("%Y-%m-%d") + "-Lot"

    if os.path.exists(PREP_RAPPORT_FOLDER + prep_name) is True:
        prep_files_list_to_upload = sorted(
            glob.glob(PREP_RAPPORT_FOLDER + "prep_rapport-" + current_time.strftime("%Y-%m-%d") + "-Lot*.csv"),
            reverse=True)
        if len(prep_files_list_to_upload) > 0:
            pprint.pprint(prep_files_list_to_upload)
            print(prep_files_list_to_upload[0])
            num_seq = len(prep_files_list_to_upload)

            prep_new_name_with_num_seq = prep_new_name + str(num_seq)
            i = num_seq
            if os.path.exists(PREP_RAPPORT_FOLDER + prep_new_name_with_num_seq + ".csv") is True:
                while os.path.exists(prep_new_name + str(i) + ".csv") is True:
                    i += 1
            os.rename(PREP_RAPPORT_FOLDER + prep_name, PREP_RAPPORT_FOLDER + prep_new_name + str(i) + ".csv")
        else:
            os.rename(PREP_RAPPORT_FOLDER + prep_name, PREP_RAPPORT_FOLDER + prep_new_name + ".csv")

    log_running_applications()
