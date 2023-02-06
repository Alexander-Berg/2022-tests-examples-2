from copy import deepcopy
import hashlib

from dmp_suite import datetime_utils as dtu

from nile.processing.record import Record

EVENT_ATTRIBUTES = dict(
    appmetrica_device_id='qwerty',
    appmetrica_uuid='foo',
    yandex_uid=None,
    event_value={},
    scenario='scenario_0',
    subscenario='subscenario_0',
    screen='screen_0',
    application_version='42',
    order_id=None,
    active_order_cnt=None,
    battery_level=None
)

class DefaultRecord(object):
    def __init__(self, default_attributes=None):
        if default_attributes is None:
            default_attributes = {}
        self._default_attributes = deepcopy(default_attributes)

    def __call__(self, **kwargs):
        attributes = deepcopy(self._default_attributes)
        attributes.update(**kwargs)
        return Record(**attributes)


class DefaultEventRecord(DefaultRecord):
    def __call__(self, **kwargs):
        # generate unique event id
        attributes = {
            'event_id': hashlib.md5(dtu.format_datetime_microseconds(dtu.utcnow()).encode('utf-8')).hexdigest()
        }
        attributes.update(kwargs)
        return super(DefaultEventRecord, self).__call__(**attributes)


event = DefaultEventRecord(EVENT_ATTRIBUTES)
application = dict
scenario = dict
subscenario = dict
screen = dict
