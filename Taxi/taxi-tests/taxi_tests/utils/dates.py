import datetime

import pytz


def timestring(stamp=None, tzn='Europe/Moscow', fmt='%Y-%m-%dT%H:%M:%S%z'):
    """Преобразует таймстамп UTC (предположительно, взятый из монги)
    в строку нужного формата со смещением в нужный часовой пояс.

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param tzn: часовой пояс, принимаемый pytz.timezone
    :param fmt: формат строки, в которую нужно преобразовать время
                   (как для strftime)
    :return: строка со временем нужного формата
    """
    return localize(stamp=stamp, tzn=tzn).strftime(fmt)


def localize(stamp=None, tzn='Europe/Moscow'):
    """Преобразует таймстамп UTC (предположительно, взятый из монги)
    в локализованное время.

    :param stamp: datetime (если naive, то считается, что это UTC!)
    :param tzn: часовой пояс, принимаемый pytz.timezone
    :return: локализованное время
    """
    if stamp is None:
        stamp = datetime.datetime.utcnow()
    elif not isinstance(stamp, datetime.datetime):  # datetime.date
        stamp = datetime.datetime(stamp.year, stamp.month, stamp.day)

    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=pytz.utc)

    return stamp.astimezone(pytz.timezone(tzn))
