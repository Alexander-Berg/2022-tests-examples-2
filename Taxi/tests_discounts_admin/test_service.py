import json
from typing import List
from typing import Optional

import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from discounts_admin_plugins.generated_tests import *  # noqa


# Generated via `tvmknife unittest service -s 123 -d 2345`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIexCpEg:Hv3ePYa'
    'kdwt-qi_HD0jhU8WoNj-JX_2wxDfwiA7cwb38Npgw'
    'zCsgm0quaT38eR2lXX1HcF03_BdSbdK-5Hxh-mDTm'
    'xcLNOd0VuMBRN90paNzV8mmGbKqe-tpYP6IPZRFmt'
    'cepZdEYlDxKd1UI36ch3BGv6fgr8Eyh6EXqUHMXKs'
)

# Generated via `tvmknife unittest service -s 2345 -d 54321`
DISCOUNTS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIqRIQsagD:Lhg7nW'
    'pozxB1dzMo9Y9Sc41M16f80NhUvkHGP-WwKGjG3Am3'
    'AmNMNR4-kYAE2br9UbOprSUhBF1_dt_6vKzv-OWBIN'
    '6-8Ld8eJx5YhEKtynnxKo9563Gethl0mfsPkaC7XIb'
    'td-Bh91Tdv99iIHufF5fR21OiukzUy94J09TB8A'
)

# Generated via `tvmknife unittest service -s 2345 -d 5443`
AGGLOMERATIONS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQwyo:GT1-8yN'
    'ecTJhw45VNVhu_9nFJ7QWY7aV31s5IosBNANN5RX1o'
    'f06urcHn6Zx5LHinnl8PrSV-r0RXII3Pv7mewCeMf7'
    'p8f59EfZ093WD7ITFN_ebIyTsyX4RLs-v05-b8SCHd'
    'UF9D3ZamOMmNxPari90pd6yLCUj1kQOGrmXtG8'
)

# Generated via `tvmknife unittest service -s 2345 -d 222333`
BILLING_SUBVENTIONS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgcIqRIQ_cgN:CQcP61D'
    'B-Qqa5qJB3ek9C09EGAqPTy9vSn_ZisAsaiwaJuXz2o'
    'NOT-Sql0vvSi2RIAclXFnwNSh_6hX3nNmVRMsHcb5fE'
    '3aADsg3OuT8MJtEcrdOtwGyHuuMVv6MX67c0qCDr70n'
    'cSSLt1dwpTdlfrd1cCnmP8-xFCf_djBFpRI'
)

# Generated via `tvmknife unittest service -s 2345 -d 9494`
PASSENGER_TAGS_SUBVENTIONS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQlko:MFHsTTyzh'
    'FHqAy18LQaJX0xxt8SMUC9gYA2-GNqacg1aYER9GiIAc'
    'zTLGD1E0JVNdcmbeyOkxq1yDcMPkPJ0zpe83FbDDix_h'
    'NSYTljGKTXrnX_rJio8_By5Gepr_BeBHWPj_vk3Y_GiN'
    'Ylvjj0ujuc2pX9zSsIXpB91zJRHbLY'
)

# Generated via `tvmknife unittest service -s 2345 -d 9343`
APPROVALS_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIqRIQ_0g:Hboh5ChWF'
    'MDnUbCBKS9sy1w3uCXDZivxdABupkVqaRS8cECwKvv_C'
    '8fjf8dWfA-N4vKf4VoMAZg2k8SzzUJrzLdBdvon9Xqff'
    'tBgkvz9XSX3wchkuvvjk-_IRrRdB2iDyIYMRydWSajdI'
    'ESLYqEPKBRqZXtJszJeOIRlPtt87mA'
)

DEFAULT_DISCOUNTS_HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}

DEFAULT_TEST_DISCOUNT = {
    'discount': {
        'discount_series_id': '0120e1',
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
                'date_from': '2100-01-01T00:00:00',
                'timezone_type': 'utc',
            },
        },
        'zones_list': [1],
    },
}
ERROR_RESPONSE = {'message': 'Server error', 'code': '400'}

PARAMETRIZE_DISCOUNT_HISTORY_LIST = [
    ({'discount_series_id': 'Test_400'}, 400, ERROR_RESPONSE),
    ({'discount_series_id': 'Test_200'}, 200, DEFAULT_TEST_DISCOUNT),
]

ZONAL_LIST_VIEW = {
    'zone_type': 'tariff_zone',
    'zone_name': 'testsuite_zone',
    'enabled': True,
    'discounts': [
        {
            'discount_series_id': '0120e1',
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
            },
            'zones_list': [1],
        },
    ],
}

SEARCH_DISCOUNTS_BY_TAGS_FOUND_RESPONSE = {
    'items': [
        {
            'tag': '0',
            'description': 'discount1',
            'discount_series_id': 'discount1',
            'zone_name': 'moscow',
        },
        {
            'tag': 'discounts_tag',
            'description': 'discount2',
            'discount_series_id': 'discount2',
            'zone_name': 'che',
        },
    ],
}


def _get_ride_discounts_response(hierarchy_name: str) -> dict:
    return {
        'discounts_data': {
            'hierarchy_name': hierarchy_name,
            'discounts_info': [
                {
                    'discount_id': '123',
                    'name': '123',
                    'create_draft_id': '123',
                    'conditions': [
                        {
                            'condition_name': 'tag',
                            'value': f'ride_discounts_{hierarchy_name}_tag',
                        },
                    ],
                },
            ],
        },
    }


TAGS_DEFAULT_RESPONSE = {
    'items': [
        {'tag': 'mastercard', 'topic': 'discounts', 'is_financial': True},
        {'tag': 'My_cared', 'topic': 'discounts', 'is_financial': True},
        {'tag': 'careless', 'topic': 'discounts', 'is_financial': True},
    ],
    'limit': 10,
    'offset': 0,
}


@pytest.mark.servicetest
@pytest.mark.tvm2_ticket({9494: PASSENGER_TAGS_SUBVENTIONS_SERVICE_TICKET})
async def test_v1_admin_suggest_tags(taxi_discounts_admin, mockserver):
    @mockserver.json_handler('/passenger-tags/v1/topics/items')
    def _passenger_tags_topics_items(request):
        return TAGS_DEFAULT_RESPONSE

    request_param = {'tag_substring': 'ca'}

    resp = await taxi_discounts_admin.get(
        '/v1/admin/suggest-tags',
        params=request_param,
        headers=DEFAULT_DISCOUNTS_HEADERS,
    )
    assert resp.status_code == 200
    response_json = resp.json()
    assert response_json['tags'] == ['careless', 'My_cared', 'mastercard']


@pytest.mark.servicetest
@pytest.mark.parametrize('req, code, res', PARAMETRIZE_DISCOUNT_HISTORY_LIST)
@pytest.mark.tvm2_ticket({54321: DISCOUNTS_SERVICE_TICKET})
async def test_discounts_history_get(
        taxi_discounts_admin, req, code, res, mockserver,
):
    @mockserver.json_handler('/v1/admin/discount-history')
    def _discounts_handler(request):
        if request.args['discount_series_id'] == 'Test_400':
            return mockserver.make_response(json=ERROR_RESPONSE, status=400)
        return mockserver.make_response(json=DEFAULT_TEST_DISCOUNT, status=200)

    response = await taxi_discounts_admin.get(
        '/v1/admin/discount-history',
        params=req,
        headers=DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == code
    assert response.json() == res


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'req,code', [({'zone_id': 1}, 200), ({'zone_id': 100}, 400)],
)
@pytest.mark.tvm2_ticket({54321: DISCOUNTS_SERVICE_TICKET})
async def test_discounts_zonal_lists_view(
        taxi_discounts_admin, req, code, mockserver,
):
    @mockserver.json_handler('/v1/admin/zonal-lists/view')
    def _discounts_handler(request):
        if request.args['zone_id'] == '100':
            return mockserver.make_response(json.dumps(ERROR_RESPONSE), 400)
        return mockserver.make_response(json.dumps(ZONAL_LIST_VIEW), 200)

    response = await taxi_discounts_admin.get(
        '/v1/admin/zonal-lists/view',
        params=req,
        headers=DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == code
    if code == 200:
        assert response.json() == ZONAL_LIST_VIEW


@pytest.mark.servicetest
@pytest.mark.tvm2_ticket({54321: DISCOUNTS_SERVICE_TICKET})
async def test_error_proxy(taxi_discounts_admin):
    response = await taxi_discounts_admin.get(
        '/v1/admin/hacker-proxy', headers=DEFAULT_DISCOUNTS_HEADERS,
    )
    assert response.status_code == 404


@pytest.mark.servicetest
@pytest.mark.config(
    DISCOUNT_AGGLOMERATION_SETTINGS={
        'use_geo_nodes': True,
        'hierarchy_type': 'BR',
    },
)
@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={
                    'discounts': True,
                    'billing-subventions': True,
                    'agglomerations': True,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={
                    'discounts': False,
                    'billing-subventions': False,
                    'agglomerations': False,
                },
            ),
        ),
    ],
)
async def test_v1_admin_check_subventions(
        taxi_discounts_admin, mockserver, taxi_config,
):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    def _select(request):
        data = request.json
        if (
                data['tariff_zone'] == 'test_bad_tariff_from_agl'
                or data['tariff_zone'] == 'test_bad_tariff_from_tariff'
        ):
            return {'subventions': []}
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

    @mockserver.json_handler('/taxi-agglomerations/v1/geo_nodes/find_children')
    def _geo_nodes_find_children(request):
        return {
            'items': [
                {
                    'geo_node': 'test_agglomeration',
                    'contains': [
                        {
                            'type': 'tariff_zone',
                            'names': [
                                'test_tariff',
                                'test_bad_tariff_from_agl',
                            ],
                        },
                        {'type': 'geoarea', 'names': []},
                    ],
                },
            ],
        }

    request_param = {
        'zones': [
            {'name': 'test_agglomeration', 'type': 'agglomeration'},
            {'name': 'test_good_tariff_zone', 'type': 'tariff_zone'},
            {'name': 'test_bad_tariff_from_tariff', 'type': 'tariff_zone'},
            {'name': 'test_bad_tariff_from_agl', 'type': 'tariff_zone'},
        ],
    }

    resp = await taxi_discounts_admin.post(
        '/v1/admin/check-subventions',
        data=json.dumps(request_param),
        headers=DEFAULT_DISCOUNTS_HEADERS,
    )
    if not taxi_config.get('DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED')[
            'discounts'
    ]:
        assert resp.status_code == 500, resp.json()
        assert resp.json() == {
            'code': 'Client disabled',
            'message': 'Client for billing-subventions disabled',
        }
    else:
        assert resp.status_code == 200, resp.json()
        response_json = resp.json()
        assert response_json['tariff_zones'] == [
            'test_bad_tariff_from_agl',
            'test_bad_tariff_from_tariff',
        ]


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'req, resp, has_new_hierarchy',
    [
        pytest.param(
            {'action': 'append', 'tags': []},
            'allowed',
            False,
            id='append_empty',
        ),
        pytest.param(
            {'action': 'remove', 'tags': []},
            'allowed',
            False,
            id='remove_empty',
        ),
        pytest.param(
            {
                'action': 'append',
                'tags': [
                    'ride_discounts_full_discounts_tag',
                    'ride_discounts_payment_method_discounts_tag',
                    'not_ride_discounts_full_discounts_tag',
                    'not_ride_discounts_payment_method_discounts_tag',
                ],
            },
            'allowed',
            False,
            id='append',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['not_ride_discounts_tag']},
            'allowed',
            False,
            id='allowed_remove',
        ),
        pytest.param(
            {'action': 'remove', 'tags': ['not_ride_discounts_tag']},
            'prohibited',
            True,
            id='prohibited_has_new_hierarchy',
        ),
        pytest.param(
            {
                'action': 'remove',
                'tags': [
                    'ride_discounts_full_discounts_tag',
                    'ride_discounts_payment_method_discounts_tag',
                    'not_discounts_tag',
                    'not_ride_discounts_full_discounts_tag',
                    'not_ride_discounts_payment_method_discounts_tag',
                ],
            },
            'prohibited',
            False,
            id='prohibited_remove',
        ),
    ],
)
@pytest.mark.parametrize(
    'enabled, is_timeout',
    (
        pytest.param(False, False, id='disabled'),
        pytest.param(True, False, id='not_timeout'),
        pytest.param(True, True, id='timeout'),
    ),
)
@pytest.mark.tvm2_ticket({54321: DISCOUNTS_SERVICE_TICKET})
async def test_tags_deletion(
        taxi_discounts_admin,
        taxi_config,
        req: dict,
        resp: str,
        has_new_hierarchy: bool,
        mockserver,
        enabled: bool,
        is_timeout: bool,
):
    taxi_config.set(
        DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={'ride_discounts': enabled},
        DISCOUNTS_ADMIN_TAG_DELETION_CHECK_SETTINGS={
            'services': ['ride_discounts'],
        },
    )

    @mockserver.json_handler(
        '/ride-discounts/v1/admin/match-discounts/hierarchy-descriptions',
    )
    def _hierarchies_handler(request):
        data = {
            'hierarchies': [
                {
                    'name': 'full_discounts',
                    'conditions': [
                        {
                            'condition_name': 'tag',
                            'type': 'text',
                            'default': {'value_type': 'Other'},
                            'support_any': True,
                            'support_other': True,
                            'exclusions_for_any': True,
                            'exclusions_for_other': True,
                            'exclusions_for_type': False,
                        },
                    ],
                },
                {
                    'name': 'payment_method_discounts',
                    'conditions': [
                        {
                            'condition_name': 'tag',
                            'type': 'text',
                            'default': {'value_type': 'Other'},
                            'support_any': True,
                            'support_other': True,
                            'exclusions_for_any': True,
                            'exclusions_for_other': True,
                            'exclusions_for_type': False,
                        },
                    ],
                },
                {
                    'name': 'experimental_discounts',
                    'conditions': [
                        {
                            'condition_name': 'tag_from_experiment',
                            'type': 'text',
                            'default': {'value_type': 'Other'},
                            'support_any': True,
                            'support_other': True,
                            'exclusions_for_any': True,
                            'exclusions_for_other': True,
                            'exclusions_for_type': False,
                        },
                    ],
                },
            ],
        }
        if has_new_hierarchy:
            data['hierarchies'].append(
                {
                    'name': 'new_hierarchy',
                    'conditions': [
                        {
                            'condition_name': 'tag',
                            'type': 'text',
                            'default': {'value_type': 'Other'},
                            'support_any': True,
                            'support_other': True,
                            'exclusions_for_any': True,
                            'exclusions_for_other': True,
                            'exclusions_for_type': False,
                        },
                    ],
                },
            )
        return data

    @mockserver.json_handler(
        '/ride-discounts/v1/admin/match-discounts/find-discounts',
    )
    def _ride_discounts_handler(request):
        if is_timeout:
            raise mockserver.TimeoutError()

        json_data = request.json
        assert json_data['type'] == 'WEAK_MATCH'
        hierarchy_name = json_data['hierarchy_name']
        assert hierarchy_name in ['full_discounts', 'payment_method_discounts']
        tags: Optional[List[str]] = None
        for condition in json_data['conditions']:
            if condition['condition_name'] == 'tag':
                tags = condition['values']
        assert tags is not None
        if f'ride_discounts_{hierarchy_name}_tag' in tags:
            return mockserver.make_response(
                json.dumps(_get_ride_discounts_response(hierarchy_name)), 200,
            )
        return mockserver.make_response(
            json.dumps(
                {
                    'discounts_data': {
                        'hierarchy_name': hierarchy_name,
                        'discounts_info': [],
                    },
                },
            ),
            200,
        )

    response = await taxi_discounts_admin.post(
        '/v1/check-tags-deletion',
        headers=DEFAULT_DISCOUNTS_HEADERS,
        data=json.dumps(req),
    )

    if req['action'] == 'append' or not req['tags']:
        assert response.status_code == 200, response.json()
        assert response.json()['permission'] == resp
        assert _ride_discounts_handler.times_called == 0
        return

    assert response.status_code == 200, response.json()

    if is_timeout:
        errors = response.json()['details']['errors']
        assert (
            'Error in \'POST /v1/admin/match-discounts/find-discounts\': '
            'Timeout happened, url: '
            + mockserver.base_url
            + 'ride-discounts/v1/admin/match-discounts/find-discounts'
            in errors
        ), response.json()
    else:
        assert response.status_code == 200, response.json()
        assert response.json()['permission'] == resp


@pytest.mark.servicetest
@pytest.mark.parametrize(
    'handler', ['v1/admin/discounts', 'v1/admin/zonal-lists'],
)
@pytest.mark.config(
    DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={'taxi-approvals': True},
)
async def test_approvals_proxy(taxi_discounts_admin, mockserver, handler):
    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    def _mock_approvals(request):
        data = json.loads(request.get_data())
        data['id'] = _mock_approvals.times_called
        data['status'] = 'need_approval'
        data['version'] = 1
        return data

    discount = {
        'tickets': {
            'existed': ['Ticket1'],
            'create_data': {'description': 'test', 'summary': 'test'},
        },
        'discount': {
            'discount_series_id': '0120e1',
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
                    'date_from': '2100-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
            },
            'zones_list': [1],
        },
    }
    req_data = {'data': discount}

    response = await taxi_discounts_admin.post(
        handler,
        headers={
            'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Author': 'user2',
        },
        data=json.dumps(req_data),
    )

    assert response.status_code == 200, response.json()
    resp_json = response.json()
    assert resp_json['response']['data'] == discount


@pytest.mark.config(DISCOUNTS_CLASSES=['first', 'second'])
async def test_discount_classes(taxi_discounts_admin):
    response = await taxi_discounts_admin.get(
        '/v1/admin/discount-classes',
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {'classes': ['first', 'second']}


@pytest.mark.config(DISCOUNTS_RIDE_PROPERTIES=['first', 'second'])
async def test_ride_properties(taxi_discounts_admin):
    response = await taxi_discounts_admin.get(
        '/v1/admin/discount-ride-properties',
        headers={'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {'ride_properties': ['first', 'second']}
