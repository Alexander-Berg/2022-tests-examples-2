from copy import deepcopy

from nile.processing.record import Record

EVENT_ATTRIBUTES = dict(
    logdatabase='database_name',
    logdebug='query_name',
    loghost='host',
    logmessage='message',
    logpid='p123',
    logsession='con123',
    logseverity='LOG',
    loguser='user_name',
    logtime='3020-01-01 10:10:00.123456',
    logsessiontime='3020-01-01 10:10:00'
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


event = DefaultRecord(EVENT_ATTRIBUTES)
