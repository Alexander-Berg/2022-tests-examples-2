import copy
import datetime

import bson.timestamp


def replace(obj, replacement):
    def replace_helper(k, v, replacement):
        if k in replacement:
            return replace(v, replacement[k])
        else:
            return copy.deepcopy(v)

    if isinstance(obj, dict) and isinstance(replacement, dict):
        res = {k: replace_helper(k, v, replacement) for k, v in obj.items()}
        res.update({k: v for k, v in replacement.items() if k not in obj})
        return res
    else:
        return replacement


def projection(obj, proj):
    assert isinstance(obj, dict)

    if isinstance(proj, list):
        res = {}
        for p in proj:
            if isinstance(p, dict):
                res.update(projection(obj, p))
            elif isinstance(p, tuple):
                assert len(p) == 2
                if p[0] in obj:
                    tmp = projection(obj[p[0]], p[1])
                    if len(tmp) > 0:
                        res[p[0]] = tmp
            else:
                res.update(projection(obj, p))
        return res
    if isinstance(proj, dict):
        return projection(obj, [(k, v) for k, v in proj.items()])
    else:
        if proj in obj:
            return {proj: obj[proj]}
        else:
            return {}


def remove(obj, rem):
    assert isinstance(obj, dict)

    def flatten_list(list):
        res = []
        for item in list:
            if isinstance(item, dict):
                res += [(k, v) for k, v in item.items()]
            else:
                res.append(item)
        return res

    if isinstance(rem, list):
        rem = flatten_list(rem)
        res = {}
        keys = []
        for e in rem:
            if isinstance(e, tuple):
                assert len(e) == 2
                if e[0] in obj:
                    res[e[0]] = remove(obj[e[0]], e[1])
                    keys.append(e[0])
            else:
                keys.append(e)
        res.update({k: v for k, v in obj.items() if k not in keys})
        return res
    else:
        return remove(obj, [rem])


def datetime_to_str(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            return {k: datetime_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        for i in range(len(obj)):
            return [datetime_to_str(v) for v in obj]
    elif isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%dT%H:%M:%S+0000')

    return copy.deepcopy(obj)


def check_updated(updated_field):
    assert isinstance(updated_field, datetime.datetime)
    delta = datetime.datetime.utcnow() - updated_field
    assert datetime.timedelta() <= delta < datetime.timedelta(minutes=1)


def check_updated_ts(updated_field):
    assert isinstance(updated_field, bson.timestamp.Timestamp)
    check_updated(datetime.datetime.utcfromtimestamp(updated_field.time))
    assert updated_field.inc > 0


def updated(obj, upd):
    cp = copy.deepcopy(obj)
    cp.update(upd)
    return cp


def make_users_list_response(display_name=None):
    user = {
        'id': '1',
        'park_id': '123',
        'passport_uid': '11',
        'is_enabled': True,
        'is_confirmed': False,
        'is_superuser': False,
        'is_usage_consent_accepted': False,
    }
    if display_name is not None:
        user['display_name'] = display_name
    return {'users': [user], 'offset': 0}


def equals(first, second):
    return abs(float(first) - float(second)) < 0.00005
