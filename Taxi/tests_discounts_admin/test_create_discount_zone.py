import http

import pytest


@pytest.fixture()
async def approvals_handler(mockserver, zone_data, rules):
    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    async def _create_draft_handler(request):
        request.json.pop('request_id')
        if request.json['api_path'] == 'admin_discounts_zonal_lists_update':
            assert request.json == {
                'mode': 'push',
                'service_name': 'discounts',
                'api_path': 'admin_discounts_zonal_lists_update',
                'run_manually': False,
                'data': zone_data,
                'tickets': {'existed': ['TAXIBACKEND-11']},
            }

            return {'id': 1, 'version': 1}

        for rule in request.json['data']['rules']:
            rule.pop('id')

        assert request.json == {
            'mode': 'push',
            'service_name': 'billing_subventions',
            'api_path': 'discount_payback_subventions_create',
            'run_manually': False,
            'data': {'rules': rules},
            'tickets': {'existed': ['TAXIBACKEND-11']},
        }
        return {'id': 2, 'version': 2}

    @mockserver.json_handler('/taxi-approvals/multidrafts/create/')
    async def _handler(request):
        request.json.pop('request_id')
        data = request.json
        assert data == {
            'attach_drafts': [
                {'id': 1, 'version': 1},
                {'id': 2, 'version': 2},
            ],
            'tickets': {'existed': ['TAXIBACKEND-11']},
        }
        return {'id': 99}


@pytest.fixture()
async def agglomerations_handler(mockserver):
    @mockserver.json_handler('/taxi-agglomerations/v1/geo_nodes/find_children')
    def _geo_nodes_find_children(request):
        assert request.json == {
            'geo_nodes': [{'name': 'russian', 'find_for': ['tariff_zone']}],
        }
        return {
            'items': [
                {
                    'geo_node': 'russian',
                    'contains': [
                        {
                            'type': 'tariff_zone',
                            'names': ['tomsk', 'boryasvo'],
                        },
                        {'type': 'geoarea', 'names': []},
                    ],
                },
            ],
        }


@pytest.fixture()
async def billing_subventions_handler(mockserver):
    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _handler(request):
        zone = request.json.pop('tariff_zone')
        assert zone in ['moscow', 'boryasvo', 'vko']
        assert request.json == {
            'time_range': {
                'start': '2020-01-01T00:00:00+00:00',
                'end': '2020-01-01T01:00:00+00:00',
            },
            'types': ['discount_payback'],
            'is_personal': False,
            'limit': 1,
        }
        if zone == 'boryasvo':
            return {
                'subventions': [
                    {
                        'tariff_zones': ['boryasvo'],
                        'status': 'enabled',
                        'start': '2018-08-01T12:59:23.231000+00:00',
                        'end': '2018-08-01T12:59:23.231000+00:00',
                        'type': 'discount_payback',
                        'is_personal': False,
                        'taxirate': 'TAXIRATE-322',
                        'subvention_rule_id': 'p_9c61aeabbeb9bfe4751aa322',
                        'cursor': 'test_cursor',
                        'tags': ['tag'],
                        'time_zone': {'id': 'test', 'offset': 'test'},
                        'updated': '2018-08-01T12:59:23.231000+00:00',
                        'currency': 'RUB',
                        'visible_to_driver': True,
                        'week_days': ['mon'],
                        'hours': [1],
                        'log': [],
                    },
                ],
            }
        return {'subventions': []}


@pytest.mark.now('2020-01-01T00:00:00Z')
@pytest.mark.servicetest
@pytest.mark.config(
    DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={
        'taxi-approvals': True,
        'discounts': True,
        'agglomerations': True,
        'billing-subventions': True,
    },
)
@pytest.mark.parametrize(
    'zone_data, rules',
    (
        pytest.param(
            {
                'zone_name': 'moscow',
                'zone_type': 'tariff_zone',
                'enabled': False,
                'discounts_list': [],
            },
            [
                {
                    'kind': 'discount_payback',
                    'begin_at': '2022-11-01T00:00:00',
                    'end_at': '2023-11-01T00:00:00',
                    'zone': 'moscow',
                },
            ],
            id='moscow',
        ),
        pytest.param(
            {
                'zone_name': 'br_russia',
                'zone_type': 'agglomeration',
                'enabled': True,
                'discounts_list': [],
            },
            [
                {
                    'kind': 'discount_payback',
                    'begin_at': '2022-11-01T00:00:00',
                    'end_at': '2023-11-01T00:00:00',
                    'zone': 'moscow',
                },
                {
                    'kind': 'discount_payback',
                    'begin_at': '2022-11-01T00:00:00',
                    'end_at': '2023-11-01T00:00:00',
                    'zone': 'vko',
                },
            ],
            id='br_russia',
        ),
    ),
)
@pytest.mark.parametrize(
    'subventions_data',
    (
        None,
        {'end_at': '2023-11-01T00:00:00', 'begin_at': '2022-11-01T00:00:00'},
    ),
)
@pytest.mark.usefixtures(
    'approvals_handler',
    'agglomerations_handler',
    'billing_subventions_handler',
)
async def test_create_discount_zone(
        taxi_discounts_admin, tvm_ticket, zone_data, rules, subventions_data,
):

    data = {'zone_data': zone_data, 'tickets': {'existed': ['TAXIBACKEND-11']}}
    if subventions_data is not None:
        data['subventions_data'] = subventions_data

    response = await taxi_discounts_admin.post(
        'v2/admin/zonal-lists',
        headers={
            'X-Ya-Service-Ticket': tvm_ticket,
            'X-YaTaxi-Draft-Author': 'user2',
        },
        json=data,
    )
    if subventions_data is None:
        assert response.status_code == http.HTTPStatus.BAD_REQUEST
        assert response.json() == {
            'code': 'ValidationError',
            'message': 'Need subventions_data',
        }
    else:
        assert response.status_code == http.HTTPStatus.OK
        assert response.json() == {'multidraft_id': 99}
