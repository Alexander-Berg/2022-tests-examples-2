#!/usr/bin/env python3
import collections
import os
import queue
import threading
import time


LOGS_DIR = '/taxi/logs'
BY_USER_DIR = os.path.join(LOGS_DIR, 'by_user')
BY_ORDER_DIR = os.path.join(LOGS_DIR, 'by_order')
LINKS_DIR = os.path.join(LOGS_DIR, 'links')
EATS_CORE_DIR = os.path.join(LOGS_DIR, 'eats-core')
SYMLINK_BASE = '../../links'

SLEEP_STEP = 0.01
SLEEP_MAX = 1

MAX_REQUEST_TIME = 120


def makedir(path):
    os.makedirs(path, exist_ok=True)
    os.chmod(path, 0o777)


def reader(log, line_queue):
    print('Start listening %s' % log.name)
    sleep = SLEEP_STEP
    while True:
        line = log.readline()
        if line:
            sleep = SLEEP_STEP
            line_queue.put(line)
        else:
            if sleep < SLEEP_MAX:
                sleep *= 2
            time.sleep(sleep)


def create_buffer():
    return {'started': time.time(), 'lines': []}


def link_append(link, lines):
    with open(os.path.join(LINKS_DIR, link + '.log'), 'a') as log:
        log.writelines(lines)


def make_symlink(link, target_id, target_dir, target_name):
    sname = os.path.join(SYMLINK_BASE, link + '.log')
    dirname = os.path.join(target_dir, target_id)
    makedir(dirname)
    os.symlink(sname, os.path.join(dirname, target_name))


# pylint: disable=too-many-branches
def writer(line_queue):
    print('Start line writer')
    log_buffers = collections.defaultdict(create_buffer)
    last_check = time.time()
    links = set()
    while True:
        line = line_queue.get()
        _mp = dict(x.split('=', 1) for x in line.split('\t') if '=' in x)
        link = _mp.get('link', '')
        if len(link) != 32:
            continue

        line_type = _mp.get('_type')
        if line_type == 'request':
            log_buffers[link]['lines'].append(line)

        elif line_type == 'response' and link in log_buffers:
            user_id = _mp.get('meta_user_id', '')
            order_id = _mp.get('meta_order_id', '')
            if (
                    'meta_type' not in _mp
                    or 'timestamp' not in _mp
                    or (len(user_id) != 32 and len(order_id) != 32)
            ):
                del log_buffers[link]
            else:
                meta_type = _mp['meta_type'].replace('/', '_')
                timestamp = _mp['timestamp'].replace(' ', 'T')
                fname = '%s_%s_%s.log' % (timestamp, meta_type, link)
                log_buffers[link]['lines'].append(line)
                link_append(link, log_buffers[link]['lines'])
                links.add(link)
                del log_buffers[link]

                for log_id, log_dir in (
                        (user_id, BY_USER_DIR),
                        (order_id, BY_ORDER_DIR),
                ):
                    if len(log_id) == 32:
                        make_symlink(link, log_id, log_dir, fname)

        elif line_type == 'log':
            if link in log_buffers:
                log_buffers[link]['lines'].append(line)
            elif link in links:
                link_append(link, [line])

        now = time.time()
        to_remove = []
        if (now - last_check) <= MAX_REQUEST_TIME:
            continue

        last_check = now
        for link, log_buffer in log_buffers.items():
            if now - log_buffer['started'] > MAX_REQUEST_TIME:
                print('%s timed out' % link)
                to_remove.append(link)
        for link in to_remove:
            del log_buffers[link]


def get_logs():
    logs = {}
    for log in os.listdir(LOGS_DIR):
        print('Found %s' % log)
        if os.path.isfile(os.path.join(LOGS_DIR, log)) and log.endswith(
                '.log',
        ):
            logs[log] = open(os.path.join(LOGS_DIR, log))
            # set position to the end of file for logs that existed on startup
            logs[log].seek(0, 2)
    return logs


def start_thread(target, *args):
    print('Starting thread')
    thread = threading.Thread(target=target, args=args, daemon=True)
    thread.start()
    return thread


def main():
    makedir(BY_USER_DIR)
    makedir(BY_ORDER_DIR)
    makedir(LINKS_DIR)
    makedir(EATS_CORE_DIR)
    print('Dirs created')

    logs = get_logs()

    line_queue = queue.Queue()
    start_thread(writer, line_queue)

    for log in logs.values():
        start_thread(reader, log, line_queue)

    while True:
        for log in os.listdir(LOGS_DIR):
            if (
                    log not in logs
                    and log.endswith('.log')
                    and os.path.isfile(os.path.join(LOGS_DIR, log))
            ):
                print('Found %s' % log)
                logs[log] = open(os.path.join(LOGS_DIR, log))
                start_thread(reader, logs[log], line_queue)

        time.sleep(0.1)


if __name__ == '__main__':
    main()
