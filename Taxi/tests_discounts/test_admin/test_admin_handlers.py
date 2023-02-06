# pylint: disable=too-many-lines
import copy
import json

import pytest

from tests_discounts.test_admin import admin_test_utils

PARAMETRIZE_ZONAL_LISTS = [
    (
        {
            'zone_name': 'no_such_tariff_zone',
            'enabled': True,
            'discounts_list': [],
        },
        400,
    ),
    (
        {
            'zone_name': 'br_moscow',
            'enabled': True,
            'zone_type': 'agglomeration',
            'discounts_list': [],
        },
        200,
    ),
    (
        {
            'zone_name': 'no_such_agglomeration',
            'enabled': True,
            'zone_type': 'agglomeration',
            'discounts_list': [],
        },
        400,
    ),
    (  # try set empty list for existing non-empty zonal list
        {'zone_name': 'testsuite_zone', 'enabled': True, 'discounts_list': []},
        400,
    ),
    ({'zone_name': 'test_zone', 'enabled': True, 'discounts_list': []}, 200),
    (
        {
            'zone_name': 'testsuite_zone',
            'enabled': True,
            'discounts_list': [
                {'discount_series_id': '0120e1'},
                {'discount_series_id': 'deafbeef'},
            ],
        },
        200,
    ),
    (
        {
            'zone_name': 'testsuite_zone',
            'enabled': True,
            'discounts_list': [
                {'discount_series_id': 'deafbeef'},
                {'discount_series_id': '0120e1'},
            ],
        },
        200,
    ),
]

PARAMETRIZE_ZONAL_BULK_LISTS = [
    (
        {
            'items': [
                {
                    'zone_name': 'testsuite_zone',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
                {
                    'zone_name': 'testsuite_zone_2',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
            ],
        },
        200,
    ),
    (
        {
            'items': [
                {
                    'zone_name': 'testsuite_zone',
                    'enabled': False,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
                {
                    'zone_name': 'testsuite_zone_2',
                    'enabled': False,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
            ],
        },
        200,
    ),
    ({'items': [{'zone_name': 'testsuite_zone', 'enabled': False}]}, 200),
    (
        {
            'items': [
                {
                    'zone_name': 'testsuite_zone',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': 'deafbeef'},
                        {'discount_series_id': '0120e1'},
                    ],
                },
                {
                    'zone_name': 'testsuite_zone_2',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': 'deafbeef'},
                        {'discount_series_id': '0120e1'},
                    ],
                },
            ],
        },
        200,
    ),
    (
        {
            'items': [
                {
                    'zone_name': 'testsuite_zone',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
                {
                    'zone_name': 'no_such_tariff_zone',
                    'enabled': True,
                    'discounts_list': [
                        {'discount_series_id': '0120e1'},
                        {'discount_series_id': 'deafbeef'},
                    ],
                },
            ],
        },
        400,
    ),
]

TAGS_DEFAULT_RESPONSE = {
    'items': [
        {'tag': 'mega_user1', 'topic': 'discounts', 'is_financial': True},
        {
            'tag': 'individual_entrepreneur',
            'topic': 'discounts',
            'is_financial': True,
        },
        {'tag': 'mastercard', 'topic': 'discounts', 'is_financial': True},
        {'tag': 'new_user', 'topic': 'discounts', 'is_financial': True},
        {'tag': 'lightbox', 'topic': 'discounts', 'is_financial': True},
    ],
    'limit': 10,
    'offset': 0,
}


async def test_ping(taxi_discounts):
    response = await taxi_discounts.get('ping')
    assert response.status_code == 200


async def test_get_discounts(taxi_discounts):
    response = await taxi_discounts.get(
        '/v1/admin/discounts',
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200


@pytest.fixture(name='taxi-agglomerations', autouse=True)
def _mock_agglomerations(mockserver):
    @mockserver.json_handler('/taxi-agglomerations/v1/agglomerations/get_info')
    def _get_info(request):
        data = {
            'items': [
                {
                    'agglomeration': 'testsuite_zone',
                    'currency': 'RUB',
                    'time_zone': 'Europe/Moscow',
                },
                {
                    'agglomeration': 'test_zone',
                    'currency': 'RUB',
                    'time_zone': 'Europe/Moscow',
                },
            ],
        }
        if request.json.get('agglomerations')[0] == 'no_such_agglomeration':
            return mockserver.make_response('No such agglomeration', 404)
        return mockserver.make_response(json.dumps(data), 200)

    @mockserver.json_handler('/taxi-agglomerations/v1/geo_nodes/get_info/')
    def _get_info_geo_nodes(request):
        data = {
            'items': [
                {
                    'name': 'testsuite_zone',
                    'created_at': '2020-03-31T14:01:38+03:00',
                    'hierarchy_type': 'BR',
                    'node_type': 'agglomeration',
                },
                {
                    'name': 'test_zone',
                    'created_at': '2020-03-31T14:01:38+03:00',
                    'hierarchy_type': 'BR',
                    'node_type': 'agglomeration',
                },
            ],
        }
        if request.json.get('geo_nodes')[0] == 'no_such_agglomeration':
            return mockserver.make_response(
                'geo_node (no_such_agglomeration) not found', 404,
            )
        return mockserver.make_response(json.dumps(data), 200)


@pytest.mark.config(
    VALIDATION_ZONES_FOR_ZONAL_DISCOUNTS=True,
    USERVICE_AGGLOMERATIONS_CACHE_SETTINGS={
        '__default__': {
            'enabled': True,
            'log_errors': True,
            'verify_on_updates': True,
        },
    },
)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DISCOUNT_LIST_QUERIES)
@pytest.mark.parametrize('req,expected_code', PARAMETRIZE_ZONAL_LISTS)
async def test_v1_admin_zonal_lists_post(
        taxi_discounts, req, expected_code, pgsql, mockserver,
):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_discounts.post(
        'v1/admin/zonal-lists',
        data=json.dumps(req),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        expected_resp = copy.deepcopy(req)
        if 'zone_type' not in expected_resp:
            expected_resp['zone_type'] = 'tariff_zone'
        assert resp == expected_resp


@pytest.mark.config(VALIDATION_ZONES_FOR_ZONAL_DISCOUNTS=True)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DISCOUNT_LIST_QUERIES)
async def test_v1_admin_zonal_lists_change(taxi_discounts, pgsql, mockserver):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    data = {
        'zone_name': 'testsuite_zone',
        'enabled': True,
        'discounts_list': [
            {'discount_series_id': 'deafbeef'},
            {'discount_series_id': '0120e1'},
        ],
    }

    # save zone with first deafbeef discount
    response = await taxi_discounts.post(
        'v1/admin/zonal-lists',
        data=json.dumps(data),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    resp = response.json()
    expected_resp = copy.deepcopy(data)
    if 'zone_type' not in expected_resp:
        expected_resp['zone_type'] = 'tariff_zone'
    assert resp == expected_resp

    # check zone with first deafbeef discount
    response = await taxi_discounts.get(
        'v1/admin/zonal-lists/view',
        params={'zone_id': 1},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['discounts'][0]['discount_series_id'] == 'deafbeef'  # not fail

    # swap 2 discounts
    data['discounts_list'] = [
        {'discount_series_id': '0120e1'},
        {'discount_series_id': 'deafbeef'},
    ]
    # save zone with first 0120e1 discount
    response = await taxi_discounts.post(
        'v1/admin/zonal-lists',
        data=json.dumps(data),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200

    resp = response.json()
    expected_resp = copy.deepcopy(data)
    if 'zone_type' not in expected_resp:
        expected_resp['zone_type'] = 'tariff_zone'
    assert resp == expected_resp

    # check zone with first 0120e1 discount
    response = await taxi_discounts.get(
        'v1/admin/zonal-lists/view',
        params={'zone_id': 1},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    resp = response.json()
    assert resp['discounts'][0]['discount_series_id'] == '0120e1'  # not fail


@pytest.mark.config(VALIDATION_ZONES_FOR_ZONAL_DISCOUNTS=True)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DISCOUNT_LIST_QUERIES)
@pytest.mark.parametrize('req,expected_code', PARAMETRIZE_ZONAL_BULK_LISTS)
async def test_v1_admin_zonal_lists_bulk_post(
        taxi_discounts, req, expected_code, pgsql, mockserver,
):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_discounts.post(
        'v1/admin/zonal-lists-bulk',
        data=json.dumps(req),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        expected_resp = copy.deepcopy(req)
        for item in expected_resp['items']:
            if 'zone_type' not in expected_resp:
                item['zone_type'] = 'tariff_zone'
            item.setdefault(
                'discounts_list',
                [
                    {'discount_series_id': '0120e1'},
                    {'discount_series_id': 'deafbeef'},
                ],
            )
        assert resp == expected_resp
    else:
        resp = response.json()
        assert resp['code'] == 'Discount zone validation failed'


@pytest.mark.config(VALIDATION_ZONES_FOR_ZONAL_DISCOUNTS=True)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DISCOUNT_LIST_QUERIES)
@pytest.mark.parametrize('req,expected_code', PARAMETRIZE_ZONAL_LISTS)
async def test_v1_admin_zonal_lists_check(
        taxi_discounts, req, expected_code, pgsql, mockserver,
):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_discounts.post(
        'v1/admin/zonal-lists/check',
        data=json.dumps(req),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        assert 'data' in resp
        assert resp['data'] == req


@pytest.mark.config(VALIDATION_ZONES_FOR_ZONAL_DISCOUNTS=True)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DISCOUNT_LIST_QUERIES)
@pytest.mark.parametrize('req,expected_code', PARAMETRIZE_ZONAL_BULK_LISTS)
async def test_v1_admin_zonal_lists_bulk_check(
        taxi_discounts, req, expected_code, pgsql, mockserver,
):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_discounts.post(
        'v1/admin/zonal-lists-bulk/check',
        data=json.dumps(req),
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp = response.json()
        for item, exp_data in zip(resp['data']['items'], req['items']):
            assert item == exp_data
        for draft_lock, zone in zip(resp['lock_ids'], req['items']):
            assert draft_lock['id'] == zone['zone_name']

    else:
        resp = response.json()
        assert resp['code'] == 'Discount zone validation failed'


@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES
        ('testsuite_zone1',true,'tariff_zone'),
        ('testsuite_zone2',true,'tariff_zone'),
        ('testsuite_zone3',false,'agglomeration')
        """,
    ],
)
async def test_v1_admin_zonal_lists_get(taxi_discounts, mockserver):
    @mockserver.handler('taxi-tariffs/v1/tariff_settings/bulk_retrieve')
    def _updates(request):
        zone = request.args['zone_names']
        zone_response = {'zone': zone}
        if zone == 'no_such_tariff_zone':
            zone_response.update({'status': 'not_found'})
        else:
            zone_response.update({'status': 'found'})
        response = {'zones': [zone_response]}
        return mockserver.make_response(json.dumps(response), 200)

    response = await taxi_discounts.get(
        'v1/admin/zonal-lists',
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'items' in response_json
    zones = sorted(
        response_json['items'], key=lambda x: (x['zone_name'], x['zone_type']),
    )
    assert zones == [
        {
            'enabled': True,
            'zone_name': 'testsuite_zone1',
            'zone_type': 'tariff_zone',
            'zone_id': 1,
        },
        {
            'enabled': True,
            'zone_name': 'testsuite_zone2',
            'zone_type': 'tariff_zone',
            'zone_id': 2,
        },
        {
            'enabled': False,
            'zone_name': 'testsuite_zone3',
            'zone_type': 'agglomeration',
            'zone_id': 3,
        },
    ]


@pytest.mark.config(DISCOUNTS_USE_AB_GEO_AS_LISTS=True)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'request_params,expected_code',
    [({'zone_id': 1}, 200), ({'zone_id': 100}, 400)],
)
async def test_v1_admin_zonal_list_view(
        taxi_discounts, request_params, expected_code,
):
    response = await taxi_discounts.get(
        'v1/admin/zonal-lists/view',
        params=request_params,
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        response_json = response.json()
        assert response_json == {
            'zone_type': 'tariff_zone',
            'zone_name': 'testsuite_zone',
            'enabled': True,
            'discounts': [
                {
                    'discount_series_id': '0120e1',
                    'discount_class': 'valid_class',
                    'reference_entity_id': 1,
                    'description': 'testsuite_discount',
                    'enabled': False,
                    'discount_method': 'full',
                    'calculation_params': {
                        'round_digits': 3,
                        'calculation_method': 'calculation_table',
                        'discount_calculator': {
                            'table': [{'cost': 100.0, 'discount': 0.2}],
                        },
                    },
                    'select_params': {
                        'classes': ['econom'],
                        'discount_target': 'all',
                        'datetime_params': {
                            'date_from': '2019-01-01T00:00:00',
                            'timezone_type': 'utc',
                        },
                        'geoarea_a_list': ['Himki'],
                        'geoarea_b_list': ['Aprelevka'],
                    },
                    'zones_list': [1],
                },
            ],
        }


@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES ('testsuite_zone',true,'tariff_zone') """,
    ],
    files=['old_history.sql'],
)
@pytest.mark.config(
    DISCOUNTS_USE_AB_GEO_AS_LISTS=True, DISCOUNTS_CLASSES=['valid_class'],
)
async def test_v1_admin_discounts_history(taxi_discounts, pgsql):
    request1 = {
        'discount': {
            'discount_series_id': '0120e1',
            'discount_class': 'valid_class',
            'description': 'testsuite_discount_12',
            'enabled': False,
            'discount_method': 'full',
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'select_params': {
                'classes': ['econom'],
                'discount_target': 'all',
                'datetime_params': {
                    'date_from': '2100-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
                'geoarea_a': 'Himki',
                'geoarea_b': 'Aprelevka',
            },
            'zones_list': [1],
        },
    }
    await admin_test_utils.create_discount(
        request1,
        taxi_discounts,
        pgsql,
        200,
        admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    request2 = copy.deepcopy(request1)
    request2['discount']['reference_entity_id'] = 1
    request2['discount']['enabled'] = True
    request2['discount']['select_params']['classes'].append('vip')
    await admin_test_utils.create_discount(
        request2,
        taxi_discounts,
        pgsql,
        200,
        {
            **admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
            **{'X-YaTaxi-Draft-Id': 'new_draft1'},
        },
    )

    request3 = copy.deepcopy(request2)
    request3['discount']['reference_entity_id'] = 2
    request3['discount']['enabled'] = False
    request3['discount']['select_params']['discount_target'] = 'tag_service'
    request3['discount']['select_params']['user_tags'] = ['10']
    await admin_test_utils.create_discount(
        request3,
        taxi_discounts,
        pgsql,
        200,
        {
            **admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
            **{'X-YaTaxi-Draft-Id': 'new_draft2'},
        },
    )
    response = await taxi_discounts.get(
        'v1/admin/discount-history',
        params={'discount_series_id': '0120e1'},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_response = [
        data['discount'] for data in (request3, request2, request1)
    ]

    expected_response[0]['reference_entity_id'] = 3
    expected_response[0]['zones_list'] = []
    expected_response[1]['reference_entity_id'] = 2
    expected_response[1]['zones_list'] = []
    expected_response[2]['reference_entity_id'] = 1
    expected_response[2]['zones_list'] = []
    for i in range(3):
        expected_response[i]['select_params']['geoarea_a_list'] = ['Himki']
        expected_response[i]['select_params']['geoarea_b_list'] = ['Aprelevka']
        expected_response[i]['select_params'].pop('geoarea_a')
        expected_response[i]['select_params'].pop('geoarea_b')

    discounts_response = []
    for item in response_json['items']:
        discounts_response.append(item['discount'])

    assert discounts_response == expected_response
    assert 'old_history' not in response_json

    response = await taxi_discounts.get(
        'v1/admin/discount-history',
        params={'discount_series_id': '0120e1', 'zone_name': 'testsuite_zone'},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    discounts_response = []
    for item in response_json['items']:
        discounts_response.append(item['discount'])

    assert discounts_response == expected_response
    assert 'old_history' in response_json


@pytest.mark.config(
    DISCOUNTS_USE_AB_GEO_AS_LISTS=True, DISCOUNTS_CLASSES=['valid_class'],
)
@pytest.mark.pgsql('discounts', queries=admin_test_utils.DEFAULT_QUERIES)
async def test_v1_admin_discounts_history_with_meta_info(
        taxi_discounts, pgsql,
):
    discount0 = {
        'discount': {
            'discount_series_id': '0120e1',
            'discount_class': 'valid_class',
            'reference_entity_id': 1,
            'description': 'testsuite_discount',
            'enabled': False,
            'select_params': {
                'classes': ['econom'],
                'datetime_params': {
                    'date_from': '2019-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
                'geoarea_a': 'Himki',
                'geoarea_b': 'Aprelevka',
                'discount_target': 'all',
            },
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'discount_method': 'full',
        },
    }
    request1 = {
        'discount': {
            'discount_series_id': '0120e1',
            'discount_class': 'valid_class',
            'reference_entity_id': 1,
            'description': 'testsuite_discount',
            'enabled': True,
            'discount_method': 'subvention-fix',
            'calculation_params': {
                'round_digits': 4,
                'calculation_method': 'calculation_formula',
                'discount_calculator': {
                    'calculation_formula_v1_a1': 1.0,
                    'calculation_formula_v1_a2': 2.0,
                    'calculation_formula_v1_p1': 3.0,
                    'calculation_formula_v1_p2': 4.0,
                    'calculation_formula_v1_c1': 5.0,
                    'calculation_formula_v1_c2': 6.0,
                    'calculation_formula_v1_threshold': 100.0,
                },
            },
            'select_params': {
                'classes': ['business', 'econom'],
                'discount_target': 'all',
                'datetime_params': {
                    'date_from': '2100-02-01T00:00:00',
                    'timezone_type': 'utc',
                },
                'geoarea_a': 'Himki',
                'geoarea_b': 'Aprelevka',
            },
            'zones_list': [1],
        },
    }
    await admin_test_utils.create_discount(
        request1,
        taxi_discounts,
        pgsql,
        200,
        headers={
            'X-Ya-Service-Ticket': admin_test_utils.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Author': 'user1',
            'X-YaTaxi-Draft-Approvals': 'user3,user4',
            'X-YaTaxi-Draft-Tickets': 'ticket-1',
            'X-YaTaxi-Draft-Id': '1000',
        },
    )
    request2 = copy.deepcopy(request1)
    request2['discount']['reference_entity_id'] = 2
    request2['discount']['enabled'] = True
    request2['discount']['select_params']['classes'].append('vip')
    await admin_test_utils.create_discount(
        request2,
        taxi_discounts,
        pgsql,
        200,
        headers={
            'X-Ya-Service-Ticket': admin_test_utils.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Author': 'user2',
            'X-YaTaxi-Draft-Approvals': 'user3,user4',
            'X-YaTaxi-Draft-Tickets': 'ticket-2',
            'X-YaTaxi-Draft-Id': '1001',
        },
    )

    response = await taxi_discounts.get(
        'v1/admin/discount-history',
        params={'discount_series_id': '0120e1'},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200, response.json()
    expected_discount_response = [
        data['discount'] for data in (request2, request1, discount0)
    ]
    expected_discount_response[0]['reference_entity_id'] = 3
    expected_discount_response[0]['zones_list'] = []
    expected_discount_response[1]['reference_entity_id'] = 2
    expected_discount_response[1]['zones_list'] = []
    expected_discount_response[2]['reference_entity_id'] = 1
    expected_discount_response[2]['zones_list'] = []

    for i in range(3):
        expected_discount_response[i]['select_params']['geoarea_a_list'] = [
            'Himki',
        ]
        expected_discount_response[i]['select_params']['geoarea_b_list'] = [
            'Aprelevka',
        ]
        expected_discount_response[i]['select_params'].pop('geoarea_a')
        expected_discount_response[i]['select_params'].pop('geoarea_b')

    expected_response = [
        {
            'discount': expected_discount_response[0],
            'update_meta_info': {
                'user_login': 'user2',
                'tickets': ['ticket-2'],
            },
        },
        {
            'discount': expected_discount_response[1],
            'update_meta_info': {
                'user_login': 'user1',
                'tickets': ['ticket-1'],
            },
        },
        {'discount': expected_discount_response[2]},
    ]

    for (response_item, expected_item) in zip(
            response.json()['items'], expected_response,
    ):
        print(json.dumps(response_item['discount']))
        assert response_item['discount'] == expected_item['discount']
        assert response_item.keys() == expected_item.keys()
        if 'update_meta_info' in expected_item:
            response_meta_info = response_item['update_meta_info']
            expected_meta_info = expected_item['update_meta_info']
            login = 'user_login'
            assert response_meta_info[login] == expected_meta_info[login]
            assert (
                response_meta_info['tickets'] == expected_meta_info['tickets']
            )
            assert 'date' in response_meta_info


@pytest.mark.config(
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={
        '__default__': False,
        'passenger-tags': True,
    },
)
async def test_v1_admin_discounts_tags(taxi_discounts, mockserver):
    @mockserver.json_handler('/passenger-tags/v1/topics/items')
    def _topics_items(request):
        return TAGS_DEFAULT_RESPONSE

    resp = await taxi_discounts.get(
        '/v1/admin/discounts-tags',
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert resp.status_code == 200
    response_json = resp.json()
    assert response_json['tags'] == [
        'mega_user1',
        'individual_entrepreneur',
        'mastercard',
        'new_user',
        'lightbox',
    ]


@pytest.fixture(autouse=True)
def select_rules_request(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _rules_select(request):
        return {
            'subventions': [
                {
                    'tariff_zones': ['moscow'],
                    'status': 'enabled',
                    'start': '2009-01-01T00:00:00Z',
                    'end': '9999-12-31T23:59:59Z',
                    'type': 'discount_payback',
                    'is_personal': False,
                    'taxirate': '',
                    'subvention_rule_id': '__moscow__',
                    'cursor': '',
                    'tags': [],
                    'time_zone': {'id': '', 'offset': ''},
                    'updated': '2019-01-01T00:00:00Z',
                    'currency': 'rub',
                    'visible_to_driver': False,
                    'week_days': [],
                    'hours': [],
                    'log': [],
                    'tariff_classes': [],
                },
            ],
        }


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.config(DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={'__default__': True})
async def test_discounts_search_by_tags(taxi_discounts):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()
    data = {'tags': ['tag0']}

    response = await taxi_discounts.post(
        '/v1/admin/tags-search-discounts',
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps(data),
    )

    response_json = response.json()
    assert response.status_code == 200
    assert response_json['items'][0]['tag'] == 'tag0'
    assert response_json['items'][0]['description'] == 'discount1'


@pytest.mark.parametrize(
    'discount_series_id,expected_status,expected_content',
    (
        (
            'discount1',
            200,
            {
                'discount': {
                    'calculation_params': {
                        'calculation_method': 'calculation_formula',
                        'discount_calculator': {
                            'calculation_formula_v1_a1': 0.0,
                            'calculation_formula_v1_a2': 0.0,
                            'calculation_formula_v1_c1': 1.0,
                            'calculation_formula_v1_c2': 1.0,
                            'calculation_formula_v1_p1': 50.0,
                            'calculation_formula_v1_p2': 50.0,
                            'calculation_formula_v1_threshold': 300.0,
                        },
                        'max_value': 0.5,
                        'min_value': 0.0,
                        'newbie_max_coeff': 1.5,
                        'newbie_num_coeff': 0.15,
                        'recalc_type': 'surge_price',
                        'round_digits': 2,
                    },
                    'description': 'discount1',
                    'discount_class': 'discount_class1',
                    'discount_method': 'subvention-fix',
                    'discount_series_id': 'discount1',
                    'enabled': True,
                    'limit_id': 'discount1_limit_id',
                    'reference_entity_id': 1,
                    'select_params': {
                        'classes': ['econom'],
                        'datetime_params': {
                            'date_from': '2019-01-01T00:00:00',
                            'timezone_type': 'utc',
                        },
                        'discount_target': 'tag_service',
                        'geoarea_a': 'Himki',
                        'geoarea_b': 'Aprelevka',
                        'payment_types': ['applepay', 'card', 'cash'],
                        'user_tags': ['tag3', 'tag0'],
                    },
                    'zones_list': [1],
                },
            },
        ),
    ),
)
@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
async def test_v1_view_discount(
        taxi_discounts,
        discount_series_id,
        expected_status,
        expected_content,
        mockserver,
):
    await taxi_discounts.invalidate_caches()
    await taxi_discounts.invalidate_caches()

    @mockserver.json_handler('/billing-limits/v1/get')
    def _limits_mock(request):
        if request.json['ref'] == 'discount2_limit_id':
            return {
                'currency': 'rub',
                'label': 'Limit 2',
                'account_id': 'account_id',
                'approvers': ['staff_login'],
                'tags': [],
                'ref': 'discount2_limit_id',
                'tickets': ['TAXIBACKEND-11'],
                'windows': [
                    {
                        'type': 'tumbling',
                        'value': '1',
                        'size': 10,
                        'label': 'label of limit 1',
                    },
                ],
            }
        # will be error
        return {}

    response = await taxi_discounts.get(
        '/v1/admin/discounts/view',
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
        params={'discount_series_id': discount_series_id},
    )

    content = response.json()
    content['discount']['select_params']['payment_types'].sort()
    assert response.status_code == 200, content
    assert content == expected_content


@pytest.mark.pgsql(
    'discounts',
    files=[
        'zonal_lists.sql',
        'discounts_entities.sql',
        'discounts_lists.sql',
        'user_discounts.sql',
    ],
)
@pytest.mark.parametrize(
    'expected_discount_classes',
    (
        pytest.param(
            ['discount_class1', 'discount_class2'],
            marks=[
                pytest.mark.config(
                    DISCOUNTS_CLASSES=[
                        'discount_class1',
                        'discount_class2',
                        'default',
                    ],
                    DISCOUNTS_ENABLED_DISCOUNTS_CLASSES_BY_ZONE={
                        '__default__': True,
                    },
                ),
            ],
        ),
        pytest.param(
            ['discount_class2', 'discount_class1'],
            marks=[
                pytest.mark.config(
                    DISCOUNTS_CLASSES=[
                        'discount_class2',
                        'discount_class1',
                        'default',
                    ],
                    DISCOUNTS_ENABLED_DISCOUNTS_CLASSES_BY_ZONE={
                        '__default__': True,
                    },
                ),
            ],
        ),
    ),
)
async def test_zonal_list_view_classes(
        taxi_discounts, expected_discount_classes,
):
    response = await taxi_discounts.get(
        'v1/admin/zonal-lists/view',
        params={'zone_id': 1},
        headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    discount_classes = [
        discount['discount_class'] for discount in response_json['discounts']
    ]
    assert discount_classes == expected_discount_classes
