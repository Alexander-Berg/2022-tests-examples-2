import json

import pytest


@pytest.mark.parametrize(
    'yandex_uid,items,should_suggest',
    [
        ('yuid1', [], True),  # users not found
        (
            'yuid1',
            [
                {
                    'id': 'id1',
                    'updated': '2019-07-23T13:00:00+0000',
                    'yandex_uid': '4010989734',
                    'yandex_uid_type': 'phonish',
                },
                {
                    'id': 'id2',
                    'updated': '2019-08-23T13:00:00+0000',
                    'yandex_uid': '4010989734',
                    'yandex_uid_type': 'undefined',
                },
            ],
            False,
        ),  # test sorting
        (
            'yuid1',
            [
                {
                    'id': 'id1',
                    'updated': '2019-09-23T13:00:00+0000',
                    'yandex_uid': '4010989734',
                    'yandex_uid_type': 'phonish',
                },
            ],
            True,
        ),  # test user phonish
        (
            'uid1',
            [
                {
                    'id': 'id1',
                    'updated': '2019-09-23T13:00:00+0000',
                    'yandex_uid': 'uid1',
                    'yandex_uid_type': 'undefined',
                },
            ],
            False,
        ),  # most recent undefined
    ],
)
async def test_simple(
        taxi_zalogin, mockserver, yandex_uid, items, should_suggest,
):
    @mockserver.handler('/user-api/users/search')
    def _users_search(request):
        assert request.json['phone_ids'] == ['phoneid1']
        return mockserver.make_response(json.dumps({'items': items}), 200)

    response = await taxi_zalogin.post(
        '/v1/internal/suggest-portal-signin',
        headers={'X-Yandex-UID': yandex_uid, 'X-YaTaxi-PhoneId': 'phoneid1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['suggest_portal_signin'] == should_suggest


@pytest.mark.parametrize(
    'yandex_uid,should_suggest', [('uid1', False), ('uid2', True)],
)
async def test_user_portal(
        taxi_zalogin, mockserver, yandex_uid, should_suggest,
):
    @mockserver.handler('/user-api/users/search')
    def _users_search(request):
        assert request.json['phone_ids'] == ['phoneid1']
        items = [
            {
                'id': 'id1',
                'updated': '2019-09-23T13:00:00+0000',
                'yandex_uid': yandex_uid,
                'yandex_uid_type': 'portal',
            },
        ]
        return mockserver.make_response(json.dumps({'items': items}), 200)

    response = await taxi_zalogin.post(
        '/v1/internal/suggest-portal-signin',
        headers={'X-Yandex-UID': 'uid1', 'X-YaTaxi-PhoneId': 'phoneid1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['suggest_portal_signin'] == should_suggest


async def test_cursor(taxi_zalogin, mockserver):
    @mockserver.handler('/user-api/users/search')
    def _users_search_paginated(request):
        assert request.json['phone_ids'] == ['phoneid1']
        items = [
            {
                'id': '0',
                'updated': '2019-09-23T13:00:00+0000',
                'yandex_uid': 'uid1',
                'yandex_uid_type': 'undefined',
            },
            {
                'id': '1',
                'updated': '2019-08-23T13:00:00+0000',
                'yandex_uid': 'uid2',
                'yandex_uid_type': 'undefined',
            },
            {
                'id': '2',
                'updated': '2019-10-23T13:00:00+0000',
                'yandex_uid': 'uid3',
                'yandex_uid_type': 'phonish',
            },
        ]

        # Возвращает по одному элементу за раз с курсором
        if 'cursor' in request.json:
            cursor = int(request.json['cursor'])
            result = {'items': [items[cursor]]}
            if cursor < len(items) - 1:
                result['cursor'] = str(cursor + 1)
        else:
            result = {'items': [items[0]], 'cursor': '1'}

        return mockserver.make_response(json.dumps(result), 200)

    response = await taxi_zalogin.post(
        '/v1/internal/suggest-portal-signin',
        headers={'X-Yandex-UID': 'uid3', 'X-YaTaxi-PhoneId': 'phoneid1'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data['suggest_portal_signin']
