import datetime
import functools
import logging
import os
import os.path
import threading

import pytz

EPOCH = datetime.datetime.utcfromtimestamp(0)


class BaseError(Exception):
    pass


class CommandNotFoundError(BaseError):
    pass


def build_driver_id(clid, uuid):
    return '%s_%s' % (clid, uuid)


def timestamp(stamp):
    return (stamp - EPOCH).total_seconds()


def to_utc(stamp):
    if stamp.tzinfo is not None:
        stamp = stamp.astimezone(pytz.utc).replace(tzinfo=None)
    return stamp


# pylint: disable=redefined-builtin
def timestring(stamp=None, timezone='Europe/Moscow',
               format='%Y-%m-%dT%H:%M:%S%z'):
    """Преобразует таймстамп UTC (предположительно, взятый из монги)
    в строку нужного формата со смещением в нужный часовой пояс.

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param timezone: часовой пояс, принимаемый pytz.timezone
    :param format: формат строки, в которую нужно преобразовать время
                   (как для strftime)
    :return: строка со временем нужного формата
    """
    return localize(stamp=stamp, timezone=timezone).strftime(format)


def localize(stamp=None, timezone='Europe/Moscow'):
    """Преобразует таймстамп UTC (предположительно, взятый из монги)
    в локализованное время.

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param timezone: часовой пояс, принимаемый pytz.timezone
    :return: локализованное время
    """
    if stamp is None:
        stamp = datetime.datetime.utcnow()
    elif not isinstance(stamp, datetime.datetime):  # datetime.date
        stamp = datetime.datetime(stamp.year, stamp.month, stamp.day)

    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=pytz.utc)

    return stamp.astimezone(pytz.timezone(timezone))


# https://gist.github.com/vadimg/2902788
def timeout(duration, default=None):
    def decorator(func):
        class InterruptableThread(threading.Thread):
            def __init__(self, args, kwargs):
                threading.Thread.__init__(self)
                self.args = args
                self.kwargs = kwargs
                self.result = default
                self.daemon = True

            def run(self):
                try:
                    self.result = func(*self.args, **self.kwargs)
                except Exception:  # pylint: disable=broad-except
                    pass

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            thread = InterruptableThread(args, kwargs)
            thread.start()
            thread.join(duration)
            if thread.isAlive():
                logging.warning('timeout in function %s: args: %s, kwargs: %s',
                                func, args, kwargs)
            return thread.result
        return wrap
    return decorator


def which(command, extra_path=None):
    pathes = os.environ.get('PATH', '').split(':')
    if extra_path:
        pathes.extend(extra_path)
    for path in pathes:
        fullpath = os.path.join(path, command)
        if os.path.exists(fullpath):
            return fullpath
    raise CommandNotFoundError('%s: command not found' % (command,))
