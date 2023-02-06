import datetime

from bson import json_util


class VarHook:
    def __init__(self, variables):
        self.variables = variables

    def __call__(self, obj):
        if '$var' in obj:
            varname = obj['$var']
            if varname in self.variables:
                return self.variables[varname]
            if '$default' in obj:
                return obj['$default']
            raise RuntimeError('Unknown variable name %s' % (varname,))
        return obj


def loads(string, *args, **kwargs):
    """Helper function that wraps `json.loads`.

    Automatically passes the object_hook for BSON type conversion.
    """

    default_hook = kwargs.pop('object_hook', None)
    mockserver = kwargs.pop('mockserver', None)
    now = kwargs.pop('now', datetime.datetime.utcnow())

    def object_hook(dct):
        if '$mockserver' in dct:
            if mockserver is None:
                raise RuntimeError('Need to pass mockserver')
            schema = ''
            if dct.get('$schema', True):
                schema = 'http://'
            return '%s%s:%d%s' % (
                schema,
                mockserver.host,
                mockserver.port,
                dct['$mockserver'],
            )
        if '$dateDiff' in dct:
            seconds = int(dct['$dateDiff'])
            return now + datetime.timedelta(seconds=seconds)
        if default_hook is not None:
            return default_hook(dct)
        return json_util.object_hook(dct)

    kwargs['object_hook'] = object_hook
    return json_util.json.loads(string, *args, **kwargs)


def dumps(obj, *args, **kwargs):
    """Helper function that wraps `json.dumps`.

    This function does NOT support `bson.binary.Binary` and
    `bson.code.Code` types. It just passes `default` argument to
    `json.dumps` function.
    """
    kwargs['ensure_ascii'] = kwargs.get('ensure_ascii', False)
    kwargs['sort_keys'] = kwargs.get('sort_keys', True)
    kwargs['indent'] = kwargs.get('indent', 2)
    kwargs['separators'] = kwargs.get('separators', (',', ': '))

    if 'default' not in kwargs:
        if kwargs.pop('relative_datetimes', False):
            kwargs['default'] = relative_dates_default
        else:
            kwargs['default'] = default
    return json_util.json.dumps(obj, *args, **kwargs)


def default(obj):
    obj = json_util.default(obj)
    if isinstance(obj, datetime.datetime):
        return obj.replace(tzinifo=None)
    return obj


def relative_dates_default(obj):
    """Add `$dateDiff` hook to `bson.json_util.default`."""
    if isinstance(obj, datetime.datetime):
        diff = obj.replace(tzinfo=None) - datetime.datetime.utcnow()
        seconds = int(diff.total_seconds())
        return {'$dateDiff': seconds}
    return default(obj)
