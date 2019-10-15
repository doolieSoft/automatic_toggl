import signal
import sys
from win32gui import GetWindowText, GetForegroundWindow
import datetime
import psutil, win32process, win32gui, time
import pprint
import os

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


def replace_title_if_default_title_exists_for_app(active_app):
    if active_app in app_logged.keys():
        return app_logged[active_app]['default_title']
    else:
        return ""


def get_app_name_and_title():
    app = active_window_process_name()
    default_title = replace_title_if_default_title_exists_for_app(app)

    if default_title != "":
        title = default_title
    else:
        title = GetWindowText(GetForegroundWindow())
        title = title.replace(",", " ")

    return app, title


def log_running_applications():
    global current_title
    global active_app
    global start
    global rapport
    global app_logged

    pprint.pprint(app_logged)

    new_title = ""
    while len(new_title) == 0:
        active_app, new_title = get_app_name_and_title()
        time.sleep(0.1)

    current_title = new_title
    print(current_title)

    rapport[current_title] = {}
    rapport[current_title]['exe'] = active_app
    rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
    rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
    rapport[current_title]['duration'] = datetime.timedelta()

    while True:
        # old_title = new_title
        time.sleep(1.0)
        new_title = ""
        active_app = None
        while len(new_title) == 0 or active_app is None:
            active_app, new_title = get_app_name_and_title()
            time.sleep(0.1)

        print("Switching to " + active_app)

        if current_title != new_title:
            current_time = datetime.datetime.now()
            time_used = current_time - start
            hours, minutes, seconds = hours_minutes_seconds(time_used)

            duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                                     minutes,
                                                     seconds)
            print("{0} --> time used : {1}".format(current_title, duration))

            if current_title not in rapport.keys():
                rapport[current_title] = {}
                rapport[current_title]['exe'] = active_app
                rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
                rapport[current_title]['duration'] = time_used
            else:
                rapport[current_title]['duration'] += time_used

            #            active_app = active_window_process_name()
            #            default_new_title = replace_title_if_default_title_exists_for_app(active_app)
            #            if default_new_title != "":
            #                new_title = default_new_title

            print(new_title)
            start = current_time
            # ff = (new_title + "," + start.strftime("%d/%m/%Y %H:%M:%S"))

            if new_title not in rapport.keys():
                rapport[new_title] = {}
                rapport[new_title]['exe'] = active_app
                rapport[new_title]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[new_title]['start_time'] = start.strftime("%H:%M:%S")
                rapport[new_title]['duration'] = datetime.timedelta()

            current_title = new_title


def generate_prep_rapport(*args, **kwargs):
    global current_title
    global start
    global rapport
    global app_logged
    global lines_to_keep_in_prep_rapport

    load_app_logged()

    print(active_app)
    corrected_current_title = replace_title_if_default_title_exists_for_app(active_app)
    if corrected_current_title != "":
        current_title = corrected_current_title
    print(current_title)

    current_time = datetime.datetime.now()
    time_used = current_time - start
    hours, minutes, seconds = hours_minutes_seconds(time_used)
    duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                             minutes,
                                             seconds)
    print("{0} --> time used : {1}".format(current_title, duration))

    if current_title not in rapport.keys():
        rapport[current_title]['exe'] = active_app
        rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
        rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
        rapport[current_title]['duration'] = time_used
    else:
        rapport[current_title]['duration'] += time_used

    print()

    f_prep_rapport = open("prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "w", encoding="utf8")
    f_prep_rapport.write("Active app,Email,Description,Project,Start date,Start time,Duration\n")

    print("Active app,Email,Description,Project,Start date,Start time,Duration")

    for line in lines_to_keep_in_prep_rapport:
        f_prep_rapport.write(line)

    for key, value in rapport.items():
        hours, minutes, seconds = hours_minutes_seconds(value['duration'])
        duration = "{0:02}:{1:02}:{2:02}".format(hours,
                                                 minutes,
                                                 seconds)
        title = key
        if value['exe'] in app_logged.keys():
            project = app_logged[value['exe']]['project']
        else:
            project = ""

        f_prep_rapport.write(
            value['exe'] + "," + "stefano.crapanzano@chu.ulg.ac.be" + "," + title + "," + project + "," +
            value['start_date'] + "," +
            value['start_time'] + "," + duration + "\n")
        print(
            value['exe'] + "," + "stefano.crapanzano@chu.ulg.ac.be" + "," + title + "," + project + "," +
            value[
                'start_date'] + "," +
            value['start_time'] + "," + duration)

    f_prep_rapport.close()
    print()

    generate_rapport_from_prep_rapport()
    sys.exit(0)


def generate_rapport_from_prep_rapport():
    lines_to_keep_in_rapport = []
    current_time = datetime.datetime.now()
    f_prep_rapport = open("prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "r", encoding="utf8")
    i = 0

    for line in f_prep_rapport:
        if i == 0:
            i += 1
            continue
        app, email, description, project, start_date, start_time, duration = line.split(",")
        if app in app_logged.keys():
            if app_logged[app]['default_title'] != "" and description != app_logged[app]['default_title']:
                description = replace_title_if_default_title_exists_for_app(app)

            lines_to_keep_in_rapport.append(
                email + "," + description + "," + project + "," + start_date + "," + start_time + "," + duration)

    f_rapport = open("rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "w", encoding="utf8")
    f_rapport.write("Email,Description,Project,Start date,Start time,Duration\n")

    print("Email,Description,Project,Start date,Start time,Duration")
    for line in lines_to_keep_in_rapport:
        f_rapport.write(line)
        print(line.rstrip("\n"))

    f_rapport.close()


def active_window_process_name():
    try:
        pid = win32process.GetWindowThreadProcessId(
            win32gui.GetForegroundWindow())  # This produces a list of PIDs active window relates to
        return psutil.Process(pid[-1]).name()  # pid[-1] is the most likely to survive last longer
    except:
        return None


def hours_minutes_seconds(td):
    return td.seconds // 3600, (td.seconds // 60) % 60, td.seconds % 60


if __name__ == '__main__':
    load_app_logged()

    signal.signal(signal.SIGINT, generate_prep_rapport)

    start = datetime.datetime.now()
    current_time = datetime.datetime.now()

    if os.path.exists("prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv") is True:
        f_prep_rapport = open("prep_rapport-" + current_time.strftime("%Y-%m-%d") + ".csv", "r", encoding="utf8")
        i = 0

        for line in f_prep_rapport:
            if i == 0:
                i += 1
                continue
            app, email, description, project, start_date, start_time, duration = line.split(",")
            print("Description = " + description)

            if app in app_logged.keys():
                if app_logged[app]['default_title'] != "" and description != app_logged[app]['default_title']:
                    description = replace_title_if_default_title_exists_for_app(app)

            lines_to_keep_in_prep_rapport.append(
                app + "," + email + "," + description + "," + project + "," + start_date + "," + start_time + "," + duration)

            if description not in rapport.keys():
                rapport[description] = {}
                rapport[description]['exe'] = app
                rapport[description]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[description]['start_time'] = start.strftime("%H:%M:%S")
                hh, mm, ss = duration.split(":")
                rapport[description]['duration'] = datetime.timedelta()
            else:
                print("Description in rapport.keys " + description)
                rapport[description]['exe'] = app
                rapport[description]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[description]['start_time'] = start.strftime("%H:%M:%S")
                hh, mm, ss = duration.split(":")
                rapport[description]['duration'] = datetime.timedelta()

        f_prep_rapport.close()

    log_running_applications()
