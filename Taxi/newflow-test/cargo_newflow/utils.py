import configparser
import contextlib
import json
import pathlib
import shutil
import socket
import subprocess
import time


class HttpError(Exception):
    pass


class HttpConflictError(HttpError):
    pass


def read_json(path):
    with open(path) as f:
        return json.load(f)


def get_tvmknife():
    tvmknife = shutil.which('tvmknife')
    if tvmknife:
        return [tvmknife]
    yatool = shutil.which('ya')
    if yatool:
        return [yatool, 'tool', 'tvmknife']
    raise RuntimeError(
        'Please install tvmknife program:\n\n'
        '  * apt-get install yandex-passport-tvmknife\n'
        '  * or install ya tool: https://wiki.yandex-team.ru/yatool/',
    )


def get_tvm_ticket(dest_service_id):
    return subprocess.check_output(
        [
            *get_tvmknife(),
            'get_service_ticket',
            'sshkey',
            '--src',
            '2013636',
            '--dst',
            dest_service_id,
        ],
    ).strip()


def guess_address():
    try:
        with contextlib.closing(
                socket.create_connection(('yandex.net', 80), timeout=1.0),
        ) as sock:
            sock: socket.socket
            return sock.getsockname()[0]
    except socket.error:
        return '127.0.0.1'


def retry_on_conflict(func):
    def decorated(*args, **kwargs):
        for _ in range(3):
            try:
                return func(*args, **kwargs)
            except HttpConflictError as exc:
                print('got http conflict, retrying...', exc)
                time.sleep(1)
        return func(*args, **kwargs)

    return decorated


def load_config(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    if not config.has_section('default'):
        raise Exception('No [default] section in config.')
    return config


def get_project_root() -> pathlib.Path:
    return pathlib.Path(__file__).parent.parent
