# -*- coding: utf-8 -*-


def mock_headers(consumer_ip='127.0.0.1', host='', user_ip=None,
                 user_agent=None, accept_language=None,
                 cookie=None, referer=None, authorization=None, other=None):
    headers = {
        'Ya-Consumer-Real-Ip': consumer_ip,
        'Ya-Client-Host': host,
        'Ya-Consumer-Client-Ip': user_ip,
        'Ya-Client-User-Agent': user_agent,
        'Ya-Client-X-Forwarded-For': '%s' % consumer_ip,
        'Ya-Client-Accept-Language': accept_language,
        'Ya-Client-Cookie': cookie,
        'Ya-Client-Referer': referer,
        'Ya-Consumer-Authorization': authorization,
    }

    if other:
        headers.update(other)

    return dict(header for header in headers.items() if header[1] is not None)


def mock_grants(grants=None, roles=None, users=None):
    if grants is None:
        grants = [
            {
                'id': 1,
                'name': 'allow_search',
            },
            {
                'id': 2,
                'name': 'allow_phone_search',
            },
            {
                'id': 4,
                'name': 'show_person',
            },
            {
                'id': 5,
                'name': 'show_history',
            },
            {
                'id': 7,
                'name': 'show_hint_answer',
            },
            {
                'id': 8,
                'name': 'show_phones',
            },
            {
                'id': 9,
                'name': 'show_emails',
            },
            {
                'id': 21,
                'name': 'allow_restoration_link_create',
            },
            {
                'id': 22,
                'name': 'show_restoration_form',
            },
            {
                'id': 31,
                'name': 'allow_meltingpot_user_add',
            },
            {
                'id': 32,
                'name': 'show_meltingpot_users',
            },
            {
                'id': 33,
                'name': 'show_meltingpot_statistics',
            },
            {
                'id': 34,
                'name': 'show_meltingpot_group',
            },
            {
                'id': 35,
                'name': 'allow_meltingpot_group',
            },
            {
                'id': 36,
                'name': 'show_meltingpot_schedule',
            },
            {
                'id': 37,
                'name': 'allow_meltingpot_schedule',
            },
            {
                'id': 38,
                'name': 'set_public_id',
            },
            {
                'id': 39,
                'name': 'remove_public_id',
            },
            {
                'id': 40,
                'name': 'remove_all_public_id',
            },
            {
                'id': 41,
                'name': 'set_is_verified',
            },
            {
                'id': 42,
                'name': 'phonish.disable_auth',
            },
            {
                'id': 43,
                'name': 'set_takeout_subscription',
            },
            {
                'id': 44,
                'name': 'set_sms_2fa',
            },
        ]

    if roles is None:
        roles = [
            {
                'grants': [grant['id'] for grant in grants],
                'id': 1,
                'name': 'root',
            },
            {
                'grants': [1],
                'id': 2,
                'name': 'basic',
            },
            {
                # необходимые гранты для показа анкеты кроме просмотра КО
                'grants': [1, 4, 5, 8, 9, 22],
                'id': 3,
                'name': 'restricted_form_viewer',
            }
        ]

    if users is None:
        users = [
            {
                'roles': [1, 2],
                'username': 'admin',
            },
            {
                'roles': [],
                'username': 'looser',
            },
            {
                'roles': [2],
                'username': 'lite_support',
            },
            {
                'roles': [3],
                'username': 'support',
            },
        ]

    return dict(grants=grants, roles=roles, users=users)
