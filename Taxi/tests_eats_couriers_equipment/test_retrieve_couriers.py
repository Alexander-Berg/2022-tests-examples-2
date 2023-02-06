import pytest


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier_with_billing_type.sql',
        'add_uniform_types.sql',
        'add_places.sql',
        'add_users.sql',
        'add_many_couriers.sql',
        'add_relocations.sql',
    ],
)
@pytest.mark.parametrize(
    'request_data, expected_status, expected_ids, expected_meta',
    [
        ({}, 200, list(range(22, 2, -1)), {'total': 22, 'last': 2}),
        (
            {'search': {'phone': '79999999999'}},
            200,
            [1],
            {'total': 1, 'last': 1},
        ),
        (
            {'search': {'phone': '79999999999'}, 'page': 10000},
            200,
            [1],
            {'total': 1, 'last': 1},
        ),
        ({'search': {'edaId': 123457}}, 200, [2], {'total': 1, 'last': 1}),
        (
            {'search': {'edaId': 123457}, 'page': 10000},
            200,
            [2],
            {'total': 1, 'last': 1},
        ),
        (
            {'search': {'phone': '+70000000001'}, 'page': 2, 'perPage': 3},
            200,
            [10, 6],
            {'perPage': 3, 'current': 2, 'total': 5, 'last': 2},
        ),
        (
            {
                'filter': {'workRegion': [1]},
                'order': ['-projectType', '-edaId'],
            },
            200,
            [22, 16, 10, 4, 1, 18, 12, 6, 20, 14, 8, 2],
            {'total': 12, 'last': 1},
        ),
        (
            {
                'search': {'fullName': 'урье'},
                'filter': {'workRegion': [1]},
                'order': ['projectType', '-edaId'],
                'page': 4,
                'perPage': 2,
            },
            200,
            [6, 22],
            {'perPage': 2, 'current': 4, 'total': 12, 'last': 6},
        ),
        (
            {
                'search': {'phone': '+78888888888', 'fullName': 'ьеров Кур'},
                'order': ['-edaId', '-projectType', 'workStatus'],
                'perPage': 5,
                'page': 1,
                'filter': {
                    'workRegion': [1, 13],
                    'workStatus': [1, 2],
                    'vehicleStatus': ['given', 'not-given', 'can-not-have'],
                    'uniformStatus': ['not-given', 'given'],
                    'projectType': [1, 2],
                    'billingType': [2],
                },
            },
            200,
            [2],
            {'total': 1, 'last': 1, 'perPage': 5, 'current': 1},
        ),
        (
            {'filter': {'courierService': [1, 3]}},
            200,
            [22, 19, 17, 14, 12, 9, 7, 4],
            {'total': 8, 'last': 1},
        ),
        (
            {'search': {'bagNumber': 'NUMBER'}},
            200,
            [],
            {'current': 0, 'last': 0, 'perPage': 20, 'total': 0},
        ),
    ],
)
async def test_retrieve_couriers(
        taxi_eats_couriers_equipment,
        personal_find,
        request_data,
        expected_status,
        expected_ids,
        expected_meta,
):
    create_response = await taxi_eats_couriers_equipment.post(
        '/v1.0/couriers/retrieve', json=request_data,
    )
    assert create_response.status_code == expected_status, create_response.text
    data = create_response.json()['data']
    assert [item['id'] for item in data] == expected_ids
    if 'perPage' not in expected_meta:
        expected_meta['perPage'] = 20
    if 'current' not in expected_meta:
        expected_meta['current'] = 1
    assert create_response.json()['meta'] == expected_meta
    if request_data.get('search', {}).get('phone'):
        assert personal_find.times_called == 1
    else:
        assert not personal_find.has_calls


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier.sql',
        'add_uniform_types.sql',
        'add_many_couriers.sql',
    ],
)
@pytest.mark.parametrize(
    'request_data, expected_response, expected_status, personal_used',
    [
        (
            {'search': {'phone': 'bad phone'}},
            {
                'data': [],
                'meta': {'perPage': 20, 'current': 1, 'total': 0, 'last': 1},
            },
            200,
            False,
        ),
        (
            {'search': {'phone': '+12345678901'}},
            {
                'data': [],
                'meta': {'perPage': 20, 'current': 1, 'total': 0, 'last': 1},
            },
            200,
            True,
        ),
        (
            {'order': ['-badorder', 'verybadorder']},
            {
                'errors': [
                    {
                        'detail': 'Unexpected order parameter badorder',
                        'title': 'Invalid parameter',
                        'source': {'pointer': 'order'},
                    },
                    {
                        'detail': 'Unexpected order parameter verybadorder',
                        'title': 'Invalid parameter',
                        'source': {'pointer': 'order'},
                    },
                ],
            },
            422,
            False,
        ),
        (
            {
                'order': ['-badorder', 'verybadorder'],
                'search': {'phone': 'bad phone'},
                'perPage': 9999,
            },
            {
                'errors': [
                    {
                        'detail': 'perPage must be at most 1000',
                        'title': 'Invalid parameter',
                        'source': {'pointer': 'perPage'},
                    },
                    {
                        'detail': 'Unexpected order parameter badorder',
                        'title': 'Invalid parameter',
                        'source': {'pointer': 'order'},
                    },
                    {
                        'detail': 'Unexpected order parameter verybadorder',
                        'title': 'Invalid parameter',
                        'source': {'pointer': 'order'},
                    },
                ],
            },
            422,
            False,
        ),
    ],
)
async def test_retrieve_couriers_errors(
        taxi_eats_couriers_equipment,
        request_data,
        expected_response,
        expected_status,
        personal_used,
        personal_find,
):
    create_response = await taxi_eats_couriers_equipment.post(
        '/v1.0/couriers/retrieve', json=request_data,
    )
    assert create_response.status_code == expected_status, create_response.text
    assert create_response.json() == expected_response
    if not personal_used:
        assert not personal_find.has_calls
    else:
        call = personal_find.next_call()
        assert call['request'].json == {
            'value': request_data['search']['phone'],
            'primary_replica': False,
        }


@pytest.mark.pgsql(
    'outsource-lavka-transport',
    files=[
        'add_courier_relations.sql',
        'add_courier_with_billing_type.sql',
        'add_lavka_courier.sql',
        'add_uniform_types.sql',
        'add_places.sql',
        'add_users.sql',
        'link_couriers.sql',
    ],
)
async def test_retrieve_couriers_format(taxi_eats_couriers_equipment):
    create_response = await taxi_eats_couriers_equipment.post(
        '/v1.0/couriers/retrieve', json={},
    )
    assert create_response.status_code == 200, create_response.text
    assert create_response.json() == {
        'data': [
            {
                'id': 3,
                'type': 'courier',
                'attributes': {
                    'firstName': 'Лавка',
                    'middleName': 'Лавкович',
                    'lastName': 'Лавков',
                    'phonePdId': '38d9c9ed14cf46538263a0a51f8a473a',
                    'edaId': 123458,
                    'uniformStatus': 'depremization',
                    'vehicleStatus': 'self-gave',
                    'updatedAt': '2017-09-08T00:00:00+0000',
                    'createdAt': '2017-09-08T00:00:00+0000',
                },
                'relationships': {
                    'workRegion': {'data': {'id': 2, 'type': 'region'}},
                    'workStatus': {
                        'data': {'id': 2, 'type': 'courier-work-status'},
                    },
                    'projectType': {
                        'data': {'id': 2, 'type': 'courier-project'},
                    },
                    'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
                    'courierService': {
                        'data': {'id': 1, 'type': 'courier-service'},
                    },
                },
            },
            {
                'id': 2,
                'type': 'courier',
                'attributes': {
                    'firstName': 'Курьер',
                    'middleName': 'Курьерович',
                    'lastName': 'Курьеров',
                    'phonePdId': '28d9c9ed14cf46538263a0a51f8a473a',
                    'edaId': 123457,
                    'uniformStatus': 'not-given',
                    'vehicleStatus': 'can-not-have',
                    'updatedAt': '2017-09-08T00:00:00+0000',
                    'createdAt': '2017-09-08T00:00:00+0000',
                },
                'relationships': {
                    'billingType': {'data': {'id': 2, 'type': 'billing-type'}},
                    'workRegion': {'data': {'id': 1, 'type': 'region'}},
                    'workStatus': {
                        'data': {'id': 1, 'type': 'courier-work-status'},
                    },
                    'projectType': {
                        'data': {'id': 1, 'type': 'courier-project'},
                    },
                },
            },
            {
                'id': 1,
                'type': 'courier',
                'attributes': {
                    'firstName': 'Курьер',
                    'lastName': 'Курьеров',
                    'phonePdId': '18d9c9ed14cf46538263a0a51f8a473a',
                    'edaId': 123456,
                    'uniformStatus': 'given',
                    'vehicleStatus': 'not-given',
                    'updatedAt': '2017-09-08T00:00:00+0000',
                    'createdAt': '2017-09-08T00:00:00+0000',
                },
                'relationships': {
                    'billingType': {'data': {'id': 1, 'type': 'billing-type'}},
                    'workRegion': {'data': {'id': 1, 'type': 'region'}},
                    'workStatus': {
                        'data': {'id': 1, 'type': 'courier-work-status'},
                    },
                },
            },
        ],
        'included': [
            {'id': 1, 'type': 'region', 'attributes': {'name': 'Москва'}},
            {'id': 2, 'type': 'region', 'attributes': {'name': 'Ярославль'}},
            {
                'id': 1,
                'type': 'courier-work-status',
                'attributes': {'name': 'active', 'description': 'Активен'},
            },
            {
                'id': 2,
                'type': 'courier-work-status',
                'attributes': {'name': 'dismissed', 'description': 'Уволен'},
            },
            {
                'id': 1,
                'type': 'courier-project',
                'attributes': {'name': 'eda', 'description': 'Еда'},
            },
            {
                'id': 2,
                'type': 'courier-project',
                'attributes': {'name': 'lavka', 'description': 'Лавка'},
            },
            {
                'id': 1,
                'type': 'courier-service',
                'attributes': {'name': 'Autotest courier service'},
            },
            {
                'id': 2,
                'type': 'billing-type',
                'attributes': {
                    'name': 'courier_service',
                    'description': 'Курьерская служба',
                },
            },
            {
                'id': 1,
                'type': 'billing-type',
                'attributes': {
                    'name': 'self_employed',
                    'description': 'Самозанят',
                },
            },
        ],
        'meta': {'current': 1, 'perPage': 20, 'last': 1, 'total': 3},
    }
