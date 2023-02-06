# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import (
    datetime,
    timedelta,
)
import logging
import time

from passport.backend.utils.time import (
    datetime_to_unixtime,
    unixtime_to_datetime,
)


DEFAULT_DELTA = 30

log = logging.getLogger('passport.test')


def unixtime_to_statbox_datetime(value):
    return unixtime_to_datetime(value).strftime('%Y-%m-%d %H:%M:%S')


class DatetimeNow(datetime):
    """
    datetime.now() плюс-минус.

    При сравнении с объектом datetime возвращает True, если
    разница между ним и временем сравнения меньше delta
    секунд.

    !!ВАЖНО!! использовать только именованные параметры при создании экземпляра этого класса,
    так как начиная с Python 3.8 класс datetime стал внутри создавать не datetime объекты,
    а type(self), то есть вызывать конструктор нашего класса DatetimeNow, что без хака приводит
    к генерации следующего исключения:
        TypeError: __new__() takes from 1 to 6 positional arguments but 9 were given
    """
    def __new__(cls, delta=DEFAULT_DELTA, convert_to_datetime=False,
                format_='%Y-%m-%d %H:%M:%S', utc=False, timestamp=None, *args):
        if args:
            # Хак для Python 3.8+, смотри описание класса
            return datetime.__new__(cls, delta, convert_to_datetime, format_, utc, timestamp, *args)
        if timestamp is None:
            timestamp = datetime.utcnow() if utc else datetime.now()
        time = datetime.__new__(
            cls,
            timestamp.year,
            timestamp.month,
            timestamp.day,
            timestamp.hour,
            timestamp.minute,
            timestamp.second,
            timestamp.microsecond,
            timestamp.tzinfo,
        )
        time._delta = timedelta(seconds=delta)
        time._format = format_
        time._convert_to_datetime = convert_to_datetime
        return time

    def __repr__(self):
        return "<Datetime: %s +/- %ds>" % (
            super(DatetimeNow, self).__str__(),
            self._delta.total_seconds(),
        )

    def __eq__(self, other):
        if self._convert_to_datetime:
            try:
                other = datetime.strptime(other, self._format)
            except (TypeError, ValueError):
                log.debug('Unable to convert to Datetime, continue anyway.')
        if not isinstance(other, datetime):
            return False
        return abs(self - other) < self._delta

    def __ne__(self, other):
        return not (self == other)

    def __add__(self, other):
        return self.__wrapped_call(u'__add__', other)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return self.__wrapped_call(u'__sub__', other)
        else:
            return super(DatetimeNow, self).__sub__(other)

    def __deepcopy__(self, memo):
        return DatetimeNow(
            delta=self._delta.total_seconds(),
            convert_to_datetime=deepcopy(self._convert_to_datetime, memo),
            format_=deepcopy(self._format, memo),
            timestamp=self,
        )

    def replace(self, *args, **kwargs):
        return self.__wrapped_call(u'replace', *args, **kwargs)

    def __wrapped_call(self, method_name, *args, **kwargs):
        method = getattr(super(DatetimeNow, self), method_name)
        timestamp = method(*args, **kwargs)
        return self.__class__(
            delta=self._delta.total_seconds(),
            convert_to_datetime=self._convert_to_datetime,
            format_=self._format,
            timestamp=timestamp,
        )


class TimeSpan(object):
    def __init__(self, value=0, delta=DEFAULT_DELTA):
        self.delta = delta
        self.time = value

    def __eq__(self, other):
        if isinstance(other, TimeSpan):
            other = other.time
        else:
            try:
                other = float(other)
            except (ValueError, TypeError):
                # ValueError - например, от строки, TypeError - от None. None может прилетать,
                # например, из БД, куда не записали атрибут (а рассчитывали записать).
                return False

        return abs(self.time - other) < self.delta

    def __repr__(self):
        return '<%s: %s +- %ds>' % (self.__class__.__name__, self.time, self.delta)


class TimeNow(TimeSpan):
    def __init__(self, delta=DEFAULT_DELTA, as_milliseconds=False, offset=0):
        super(TimeNow, self).__init__(
            value=time.time() + offset,
            delta=delta,
        )
        if as_milliseconds:
            self.time *= 1000
            self.delta *= 1000


def unixtime(year, month, day, hour=0, minute=0, second=0):
    return int(datetime_to_unixtime(datetime(year, month, day, hour, minute, second)))
