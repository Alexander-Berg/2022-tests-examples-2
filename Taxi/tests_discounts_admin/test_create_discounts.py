import http

import pytest


@pytest.fixture()
async def discounts_handler(mockserver, discount_data):
    @mockserver.json_handler('/discounts/v1/admin/discounts/check')
    async def _create_discounts_handler(request):
        assert request.json == discount_data
        return {'id': 1, 'version': 1}


@pytest.fixture()
async def approvals_handler(
        mockserver,
        discount_data,
        description,
        multidraft_data,
        has_active_draft,
):
    @mockserver.json_handler('/taxi-approvals/drafts/create/')
    async def _create_draft_handler(request):
        request.json.pop('request_id')
        assert request.json == {
            'mode': 'push',
            'service_name': 'discounts',
            'api_path': 'admin_discounts_create_update',
            'run_manually': False,
            'data': discount_data,
            'tickets': {'existed': ['TAXIBACKEND-11']},
        }
        return {'id': 1, 'version': 1}

    @mockserver.json_handler('/taxi-approvals/drafts/list/')
    async def _list_handler(request):
        assert request.json == {
            'statuses': ['need_approval'],
            'change_doc_ids': ['discounts_0120e1'],
            'api_path': 'admin_discounts_create_update',
        }
        if has_active_draft:
            return [{'id': 100, 'version': 1}, {'id': 110, 'version': 1}]
        return []

    @mockserver.json_handler('/taxi-approvals/multidrafts/create/')
    async def _handler(request):
        request.json.pop('request_id')
        expected_data = {
            'attach_drafts': [{'id': 1, 'version': 1}],
            'tickets': {'existed': ['TAXIBACKEND-11']},
        }
        if description is not None:
            expected_data['description'] = description
        if multidraft_data is not None:
            expected_data['data'] = multidraft_data
        assert request.json == expected_data
        return {'id': 99}


@pytest.mark.usefixtures('approvals_handler', 'discounts_handler')
@pytest.mark.now('2020-01-01T00:00:00Z')
@pytest.mark.servicetest
@pytest.mark.config(
    DISCOUNTS_ADMIN_EXTERNAL_CLIENTS_ENABLED={
        'taxi-approvals': True,
        'discounts': True,
    },
)
@pytest.mark.parametrize(
    'discount_data,has_active_draft,expected_status,expected_data',
    (
        pytest.param(
            {
                'discount': {
                    'discount_series_id': '0120e1',
                    'discount_class': 'valid',
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
            },
            False,
            http.HTTPStatus.OK,
            {'multidraft_id': 99},
            id='Ok',
        ),
        pytest.param(
            {
                'discount': {
                    'discount_series_id': '0120e1',
                    'discount_class': 'valid',
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
            },
            True,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': 'EXISTED_DRAFT',
                'message': 'existing draft ids: 100, 110',
            },
            id='Has active draft',
        ),
        pytest.param(
            {'discount': {}},
            False,
            http.HTTPStatus.BAD_REQUEST,
            {
                'code': '400',
                'message': 'Field \'discount.discount_series_id\' is missing',
            },
            id='Invalid discount data',
        ),
    ),
)
@pytest.mark.parametrize('description', (None, 'test_description'))
@pytest.mark.parametrize('multidraft_data', (None, {'discount_id': 1000}))
async def test_create_discounts(
        taxi_discounts_admin,
        tvm_ticket,
        discount_data,
        expected_status,
        expected_data,
        has_active_draft,
        description,
        multidraft_data,
):
    body = {
        'tickets': {'existed': ['TAXIBACKEND-11']},
        'data': [discount_data],
    }
    if multidraft_data is not None:
        body['multidraft_data'] = multidraft_data

    if description is not None:
        body['description'] = description

    response = await taxi_discounts_admin.post(
        'v1/admin/discounts/bulk',
        headers={
            'X-Ya-Service-Ticket': tvm_ticket,
            'X-YaTaxi-Draft-Author': 'user2',
        },
        json=body,
    )
    assert response.status_code == expected_status, response.content
    assert response.json() == expected_data
