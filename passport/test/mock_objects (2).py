# -*- coding: utf-8 -*-

from passport.backend.core.test.time_utils.time_utils import (
    DatetimeNow,
    TimeNow,
)
from passport.backend.utils.common import (
    merge_dicts,
    noneless_dict,
)


def mock_headers(
        consumer_ip='127.0.0.1', host='test.dev.yandex', user_ip=None,
        user_agent=None, x_forwarded_for=False,
        accept_language=None, cookie=None, referer=None,
        authorization=None, user_ticket=None, other=None):
    headers = {
        'X-Real-Ip': consumer_ip,
        'Ya-Client-Host': host,
        'Ya-Consumer-Client-Ip': user_ip,
        'Ya-Client-User-Agent': user_agent,
        'Ya-Client-X-Forwarded-For': '%s' % consumer_ip,
        'Ya-Client-Accept-Language': accept_language,
        'Ya-Client-Cookie': cookie,
        'Ya-Client-Referer': referer,
        'Ya-Consumer-Authorization': authorization,
        'X-Ya-User-Ticket': user_ticket,
    }

    if x_forwarded_for and user_ip:
        headers.update({'Ya-Client-X-Forwarded-For': '%s, %s' % (user_ip, consumer_ip)})

    if other:
        headers.update(other)

    return noneless_dict(headers)


def _base_statbox_entries(consumer):
    return {
        'tskv_format': 'passport-log',
        'unixtime': TimeNow(),
        'timestamp': DatetimeNow(convert_to_datetime=True),
        'timezone': '+0300',
        'py': '1',
        'consumer': consumer,
    }


def mock_frodobox_karma(login='-', consumer='dev', old_karma='-', new_karma='0', action='karma',
                        registration_datetime=None, user_ip='127.0.0.1', user_agent='-', uid='1', suid='-'):
    if registration_datetime is None:
        registration_datetime = DatetimeNow(convert_to_datetime=True)

    result = merge_dicts(
        _base_statbox_entries(consumer),
        {
            'destination': 'frodo',
            'event': 'account_modification',
            'entity': 'karma',
            'action': action,
            'registration_datetime': registration_datetime,
            'login': login,
            'old': old_karma,
            'new': new_karma,
            'ip': user_ip,
            'uid': uid,
            'suid': suid,
        },
    )

    if user_agent is not None:
        result['user_agent'] = user_agent
    return result


def _base_statbox_modification_entries(operation, uid, consumer, user_ip, user_agent):
    return merge_dicts(
        _base_statbox_entries(consumer),
        {
            'event': 'account_modification',
            'operation': operation,
            'uid': uid,
            'ip': user_ip,
            'user_agent': user_agent,
        },
    )


def mock_statbox_account_modification_entries(operation='created', names_values=None,
                                              consumer='dev', uid='1', user_ip='127.0.0.1',
                                              user_agent='-', **kwargs):
    base_entry = _base_statbox_modification_entries(operation, uid, consumer, user_ip, user_agent)

    result = []

    if names_values is not None:
        for entity, old, new in names_values:
            entry = dict(base_entry, entity=entity, **kwargs)
            if old is not None:
                entry['old'] = old
            if new is not None:
                entry['new'] = new
            result.append(entry)

    return result


def mock_statbox_subscriptions_entries(operation='created', sids=None,
                                       consumer='dev', uid='1', user_ip='127.0.0.1',
                                       user_agent='-', suid=None, **kwargs):
    base_entry = _base_statbox_modification_entries(operation, uid, consumer, user_ip, user_agent)

    result = []

    if sids is not None:
        for sid in sids:
            entry = dict(base_entry, entity='subscriptions', sid=sid, **kwargs)
            if suid is not None:
                entry['suid'] = suid
            result.append(entry)

    return result
