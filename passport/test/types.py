# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from copy import deepcopy
from datetime import (
    datetime,
    timedelta,
)
import logging

from passport.backend.social.common.chrono import now
from passport.backend.social.common.useragent import Response
import pytz


log = logging.getLogger('passport.backend.social.common.test')

DEFAULT_DELTA = 5


class ApproximateNumber(object):
    def __new__(cls, value, tolerance=1):
        integer = object.__new__(cls)
        integer._value = value
        integer._tolerance = tolerance
        return integer

    def __repr__(self):
        return '<%s(%s +- %s)>' % (
            type(self).__name__,
            self._value,
            self._tolerance,
        )

    def __str__(self):
        return str(self._value)

    def __eq__(self, other):
        return abs(self._value - other) <= self._tolerance

    def __ne__(self, other):
        return not (self == other)

    def __hash__(self):
        raise TypeError('unhashable type: %s' % type(self).__name__)


class ApproximateInteger(ApproximateNumber):
    def __new__(cls, value, tolerance=1):
        return ApproximateNumber.__new__(cls, int(value), tolerance)

    def __eq__(self, other):
        assert isinstance(other, int), '%r is not int' % other
        return super(ApproximateInteger, self).__eq__(other)


class ApproximateFloat(ApproximateNumber):
    def __new__(cls, value, tolerance=0.4):
        return ApproximateNumber.__new__(cls, float(value), tolerance)

    def __eq__(self, other):
        assert isinstance(other, float), '%r is not float' % other
        return super(ApproximateFloat, self).__eq__(other)


class DatetimeNow(datetime):
    """
    datetime.now() плюс-минус.

    При сравнении с объектом datetime возвращает True, если
    разница между ним и временем сравнения меньше delta
    секунд.
    """
    def __new__(cls, delta=DEFAULT_DELTA, convert_to_datetime=False,
                format_='%Y-%m-%d %H:%M:%S', utc=False, timestamp=None):
        if timestamp is None:
            timestamp = now()
            if utc:
                timestamp = timestamp.astimezone(pytz.utc)

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

    def __add__(self, *args, **kwargs):
        return self.__wrapped_call('__add__', *args, **kwargs)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return self.__wrapped_call('__sub__', other)

        if self.tzinfo is not None and other.tzinfo is None:
            self = self.__wrapped_call('replace', tzinfo=None)
        elif self.tzinfo is None and other.tzinfo is not None:
            self = self.__wrapped_call('replace', tzinfo=other.tzinfo)

        return super(DatetimeNow, self).__sub__(other)

    def __deepcopy__(self, memo):
        return DatetimeNow(
            delta=self._delta.total_seconds(),
            convert_to_datetime=deepcopy(self._convert_to_datetime, memo),
            format_=deepcopy(self._format, memo),
            timestamp=self,
        )

    def replace(self, *args, **kwargs):
        return self.__wrapped_call('replace', *args, **kwargs)

    def __wrapped_call(self, method_name, *args, **kwargs):
        method = getattr(super(DatetimeNow, self), method_name)
        timestamp = method(*args, **kwargs)
        return self.__class__(
            self._delta.total_seconds(),
            self._convert_to_datetime,
            self._format,
            timestamp=timestamp,
        )


class FakeResponse(Response):
    def __init__(self, value, status_code, headers=None):
        super(FakeResponse, self).__init__(
            status_code,
            value,
            duration=0,
            headers=headers,
        )
        self.value = self.data

    @classmethod
    def werkzeug_build(cls, status=None, mimetype=None):
        return cls(value='', status_code=status)

    def update_headers(self, headers):
        for key, value in headers.iteritems():
            self.headers[key.lower()] = value

    def to_zora_response(self):
        if not (
            self.getheader('X-Yandex-Orig-Http-Code') or
            self.getheader('X-Yandex-Http-Code')
        ):
            self.update_headers({'X-Yandex-Orig-Http-Code': str(self.status_code)})
            self.status_code = 200
        return self
