import signal
import sys
from win32gui import GetWindowText, GetForegroundWindow
import datetime
import psutil, win32process, win32gui, time
import pprint

rapport = {}
start = datetime.datetime.now()
active_app = None
current_title = None

app_logged = {}
f_app_logged = open("app_logged.csv", "r")
for line in f_app_logged:
    app_logged[line.rstrip("\n")] = ""
f_app_logged.close()


def get_titles():
    global current_title
    global active_app
    global start
    global rapport
    global app_logged

    pprint.pprint(app_logged)

    new_title = GetWindowText(GetForegroundWindow())
    while len(new_title) == 0:
        new_title = GetWindowText(GetForegroundWindow())
        time.sleep(0.5)

    current_title = new_title
    print(current_title)
    active_app = active_window_process_name()
    rapport[current_title] = {}
    rapport[current_title]['exe'] = active_app
    rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
    rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
    rapport[current_title]['duration'] = datetime.timedelta()

    while True:
        # old_title = new_title
        time.sleep(1.0)
        new_title = GetWindowText(GetForegroundWindow())

        active_app = active_window_process_name()
        if active_app is not None:
            print("Switching to " + active_app)

        if len(new_title) == 0:
            time.sleep(0.1)
            continue

        if current_title != new_title:
            current_time = datetime.datetime.now()
            time_used = current_time - start
            print("{3} --> time used : {0:02}:{1:02}:{2:02}".format(int(time_used.seconds / 60 / 60), int(
                time_used.seconds / 60), int(time_used.seconds), current_title))

            if current_title not in rapport.keys():
                rapport[current_title] = {}
                rapport[current_title]['exe'] = active_app
                rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
                rapport[current_title]['duration'] = time_used
            else:
                rapport[current_title]['duration'] += time_used

            print(new_title)
            current_title = new_title
            start = current_time
            # ff = (new_title + "," + start.strftime("%d/%m/%Y %H:%M:%S"))

            if current_title not in rapport.keys():
                rapport[current_title] = {}
                rapport[current_title]['exe'] = active_app
                rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
                rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
                rapport[current_title]['duration'] = datetime.timedelta()


def print_rapport(*args, **kwargs):
    global current_title
    global start
    global rapport
    global app_logged

    active_app = active_window_process_name()
    if active_app is not None:
        print(active_app)

    current_time = datetime.datetime.now()
    time_used = current_time - start
    print("{3} --> time used : {0:02}:{1:02}:{2:02}".format(int(time_used.seconds / 60 / 60), int(
        time_used.seconds / 60), int(time_used.seconds), current_title))
    # print("time used : " + str(time_used))
    print(current_title)
    if current_title not in rapport.keys():
        rapport[current_title]['exe'] = active_app
        rapport[current_title]['start_date'] = start.strftime("%Y-%m-%d")
        rapport[current_title]['start_time'] = start.strftime("%H:%M:%S")
        rapport[current_title]['duration'] = time_used
    else:
        rapport[current_title]['duration'] += time_used

    print()

    f = open("prep_rapport.csv", "w")
    f.write("Active app,Email,Description,Project,Start date,Start time,Duration\n")
    print("Active app,Email,Description,Project,Start date,Start time,Duration")
    for key, value in rapport.items():
        duration = "{0:02}:{1:02}:{2:02}".format(int(value['duration'].seconds / 60 / 60),
                                                 int(value['duration'].seconds / 60),
                                                 int(value['duration'].seconds))
        f.write(value['exe'] + "," + "stefano.crapanzano@chu.ulg.ac.be" + "," + key + ",," + value['start_date'] + "," +
                value['start_time'] + "," + duration + "\n")
        print(value['exe'] + "," + "stefano.crapanzano@chu.ulg.ac.be" + "," + key + ",," + value['start_date'] + "," +
              value['start_time'] + "," + duration)

    print()
    f = open("rapport.csv", "w")
    f.write("Email,Description,Project,Start date,Start time,Duration\n")
    print("Email,Description,Project,Start date,Start time,Duration")
    for key, value in rapport.items():
        if value['exe'] in app_logged.keys():
            duration = "{0:02}:{1:02}:{2:02}".format(int(value['duration'].seconds / 60 / 60),
                                                     int(value['duration'].seconds / 60),
                                                     int(value['duration'].seconds))
            f.write("stefano.crapanzano@chu.ulg.ac.be" + "," + key + ",," + value['start_date'] + "," +
                    value['start_time'] + "," + duration + "\n")
            print("stefano.crapanzano@chu.ulg.ac.be" + "," + key + ",," + value['start_date'] + "," +
                  value['start_time'] + "," + duration)

    f.close()
    sys.exit(0)


def handler_sigterm():
    print("sigterm")
    sys.exit(0)


def active_window_process_name():
    try:
        pid = win32process.GetWindowThreadProcessId(
            win32gui.GetForegroundWindow())  # This produces a list of PIDs active window relates to
        return psutil.Process(pid[-1]).name()  # pid[-1] is the most likely to survive last longer
    except:
        return None


if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handler_sigterm)
    signal.signal(signal.SIGINT, print_rapport)
    start = datetime.datetime.now()
    get_titles()
