import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os
import csv
from pynput import keyboard
import time
from datetime import datetime, timedelta


DFMT = '%Y%m%d'
TODAY = datetime.today().strftime(DFMT)
FMT = '%Y-%m-%d %H:%M:%S'
COLOR_MAP = {0: '#aa98a9', 1: '#394f70'}
DATADIR = 'timedata'

today_log = []
logger_on = False
terminated = False


def start_log():
    global today_log
    global logger_on
    global terminated
    if logger_on and not terminated:
        return
    terminated = False
    print()
    print("Starting task ...")
    logger_on = True
    starttime = datetime.today().strftime(FMT)
    today_log.append([starttime, None])
    print(today_log)


def stop_log():
    print()
    print("Stopping task ...")
    global today_log
    global logger_on
    logger_on = False
    endtime = datetime.today().strftime(FMT)
    today_log[-1][1] = endtime
    print(today_log)


def terminate():
    global today_log
    fpath = os.path.join(DATADIR, TODAY)
    with open(fpath, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in today_log:
            writer.writerow(row)
    today_log = []


LOGGER_ACTION = {'1': start_log, '2': stop_log}


def on_press(key):
    try:
        action = LOGGER_ACTION.get(key.char, lambda: None)
        action()
    except AttributeError:
        pass


def on_release(key):
    if key == keyboard.Key.esc:
        print()
        print("Exiting ...")
        if logger_on:
            stop_log()
        terminate()
        os._exit(1)  # return False to stop listener


def timedelta_min(date1, date2):
    d1 = datetime.strptime(date1, FMT)
    d2 = datetime.strptime(date2, FMT)

    # Convert to Unix timestamp
    d1_ts = time.mktime(d1.timetuple())
    d2_ts = time.mktime(d2.timetuple())

    # They are now in seconds, subtract and then divide by 60 to get minutes.
    return int(d2_ts-d1_ts) / 60


def split_clock(sizes, colors):
    inner_sizes, inner_colors, outer_sizes, outer_colors = [], [], [], []
    sums = 0
    for i in range(len(sizes)):
        if sums + sizes[i] >= 720:  # this will always hit, so cnt will always be assigned
            last = 720 - sums
            inner_sizes.append(last)
            inner_colors.append(colors[i])
            cnt = sums + sizes[i] - 720
            break
        inner_sizes.append(sizes[i])
        inner_colors.append(colors[i])
        sums += sizes[i]

    if cnt:
        outer_sizes.append(cnt)
        outer_colors.append(colors[i])

    for j in range(i+1, len(sizes)):
        outer_sizes.append(sizes[j])
        outer_colors.append(colors[j])
    return inner_sizes, inner_colors, outer_sizes, outer_colors

LW = 0.2
SZ = 0.12
WP = {"width": SZ, "edgecolor": "w", 'linewidth': LW, 'linestyle': 'solid', 'antialiased': True}


def draw_clock(sizes, colors, pg, ax, title):
    inner_sizes, inner_colors, outer_sizes, outer_colors = split_clock(sizes, colors)
    print("Drawing the clock ...")
    print((inner_sizes, inner_colors, outer_sizes, outer_colors))

    ax.pie(outer_sizes, colors=outer_colors, startangle=90, counterclock=False, radius=1.0, wedgeprops=WP)
    ax.pie(inner_sizes, colors=inner_colors, startangle=90, counterclock=False, radius=0.9, wedgeprops=WP)
    ax.text(0, 0, str(int(pg)) + " min", ha='center')
    ax.set_title(title)


def visualize_lastweek(last7, fig, gs):
    for day in range(min(len(last7), 6)):
        fpath = os.path.join(DATADIR, last7[day])
        with open(fpath, 'r', encoding='utf-8') as f:
            r = csv.reader(f)
            ax = fig.add_subplot(gs[(6 - len(last7) + day) // 2, (6 - len(last7) + day) % 2])
            visualize_clock(r, ax, last7[day])


def visualize_clock(log, ax, dt):
    prev_end = datetime.strptime(TODAY, DFMT).strftime(FMT) \
        if dt == 'Today' else datetime.strptime(dt, DFMT).strftime(FMT)
    nextday = (datetime.strptime(TODAY, DFMT) + timedelta(days=1)).strftime(FMT) \
        if dt == 'Today' else (datetime.strptime(dt, DFMT) + timedelta(days=1)).strftime(FMT)

    times = []
    color = []
    pg = 0

    laston = False
    data = list(log)
    for i, row in enumerate(data):
        curr_start = row[0]
        times.append(timedelta_min(prev_end, curr_start))
        color.append(COLOR_MAP[0])

        curr_end = row[1]
        if not curr_end:
            if i != len(data)-1:
                continue  # error, fail safe -- skips this row
            else:
                laston = True
        else:
            td = timedelta_min(curr_start, curr_end)
            times.append(td)
            color.append(COLOR_MAP[1])
            pg += td
        prev_end = curr_end

    if laston:
        td = timedelta_min(curr_start, nextday)
        times.append(td)
        color.append(COLOR_MAP[1])
        pg += td
    else:
        times.append(timedelta_min(prev_end, nextday))
        color.append(COLOR_MAP[0])

    draw_clock(times, color, pg, ax, dt)


def log_todays(today_csv, fig, gs):
    global today_log
    global terminated
    global TODAY

    if today_csv:
        fpath = os.path.join(DATADIR, today_csv)
        with open(fpath, 'r', encoding='utf-8') as f:
            r = csv.reader(f)
            for row in r:
                today_log.append(row)

    if logger_on:
        start_log()

    listener = keyboard.Listener(
        on_press=on_press,
        on_release=on_release)
    listener.start()

    ax = fig.add_subplot(gs[:, 3:])

    visualize_clock(today_log, ax, 'Today')

    while True:
        plt.pause(10)
        ax.clear()
        curr_day = datetime.today().strftime('%Y%m%d')
        if curr_day != TODAY:
            terminated = True
            TODAY = curr_day
            terminate()
            return
        print("Rendering ...")
        visualize_clock(today_log, ax, 'Today')
        time.sleep(110)


def show_screen():
    global TODAY
    while True:
        dir_files = [f for f in os.listdir(DATADIR) if not f.startswith('.')]
        dir_files = sorted(dir_files)

        if len(dir_files) > 7:
            last7day_log_files = dir_files[-7:]
        else:
            last7day_log_files = dir_files

        TODAY = datetime.today().strftime('%Y%m%d')

        today_log_file = None
        if last7day_log_files:
            # print(last7day_log_files[-1])
            if last7day_log_files[-1] != TODAY:
                last7day_log_files = last7day_log_files[1:]
                today_log_file = None
            else:
                today_log_file = last7day_log_files[-1]
                last7day_log_files = last7day_log_files[:-1]

        fig = plt.figure(constrained_layout=True, figsize=(10, 6))
        gs = GridSpec(3, 5, figure=fig)
        visualize_lastweek(last7day_log_files, fig, gs)
        log_todays(today_log_file, fig, gs)


if __name__ == "__main__":
    show_screen()
