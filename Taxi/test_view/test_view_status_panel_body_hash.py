import json

import pytest

from tests_driver_fix import common

EMPTY_ITEMS_HASH = 'v1:17a83bb01c89bae39c6189204e7ce3f78ca0f991'
ITEMS_HASH = 'v1:2488ab6e8c004b6b8bc881d2590153e802975d6d'


@pytest.mark.parametrize('panel_body_hash', (None, 'hash', EMPTY_ITEMS_HASH))
@pytest.mark.parametrize('calc_panel_body_hash', (True, False))
@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_panel_body_hash_empty_items(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        panel_body_hash,
        calc_panel_body_hash,
):
    taxi_config.set_values(
        dict(DRIVER_FIX_CALCULATE_PANEL_BODY_HASH=calc_panel_body_hash),
    )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom', 'business']

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        assert json.loads(request.get_data()) == {
            'driver': {'db_id': 'dbid', 'uuid': 'uuid'},
            'types': ['driver_fix'],
        }
        return {
            'subventions': [
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': '2019-01-01T00:00:01+03:00',
                        'end_time': '2019-01-02T00:00:00+03:00',
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': 600,
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {'amount': '1000', 'currency': 'RUB'},
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            ],
        }

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(None, panel_body_hash),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )

    assert response.status_code == 200

    expected_response = {
        'keep_in_busy': False,
        'panel_body': {'items': []},
        'panel_header': {
            'icon': 'time',
            'subtitle': '10;1000 ₽',
            'title': 'Driver-fix',
        },
        'reminiscent_overlay': {'text': '10'},
        'status': 'subscribed',
    }
    if calc_panel_body_hash:
        if panel_body_hash == EMPTY_ITEMS_HASH:
            expected_response.pop('panel_body')
        else:
            expected_response['panel_body']['hash'] = EMPTY_ITEMS_HASH

    assert response.json() == expected_response

    assert response.headers['X-Polling-Delay'] == '60'


@pytest.mark.parametrize(
    'value_arr',
    (
        (
            {
                'amount': 61,
                'time': 6000,
                'start': '2019-01-01T00:00:00+02:00',
                'end': '2019-01-02T00:00:00+02:00',
            },
        ),
        (
            {
                'amount': 61,
                'time': 30,
                'start': '2018-12-31T12:00:01+03:00',
                'end': '2019-01-01T12:00:01+03:00',
            },
            {
                'amount': 61,
                'time': 30,
                'start': '2018-12-31T12:00:01+03:00',
                'end': '2019-01-01T12:00:01+03:00',
            },
        ),
    ),
)
@pytest.mark.parametrize('panel_body_hash', (None, 'hash', ITEMS_HASH))
@pytest.mark.parametrize('calc_panel_body_hash', (True, False))
@pytest.mark.config(DRIVER_FIX_STATUS_PANEL_ITEMS=['restrictions'])
@pytest.mark.now('2019-01-01T12:00:00+0300')
@pytest.mark.config(
    DRIVER_FIX_STATUS_SCREEN_CUT_SETTINGS={
        'show_on_busy': 'restrictions',
        'show_on_free': 'restrictions',
    },
)
@pytest.mark.geoareas(sg_filename='subvention_geoareas.json')
async def test_status_panel_body_hash(
        taxi_driver_fix,
        mockserver,
        mock_offer_requirements,
        taxi_config,
        taxi_dms_mock,
        taxi_vbd_mock,
        panel_body_hash,
        calc_panel_body_hash,
        value_arr,
):
    taxi_config.set_values(
        dict(DRIVER_FIX_CALCULATE_PANEL_BODY_HASH=calc_panel_body_hash),
    )

    common.default_init_mock_offer_requirements(mock_offer_requirements)
    mock_offer_requirements.profiles_value['classes'] = ['econom']
    mock_offer_requirements.rules_select_value['profile_tariff_classes'] = [
        'econom',
        'business',
    ]

    @mockserver.json_handler('/billing_subventions/v1/virtual_by_driver')
    async def _get_by_driver(request):
        subventions = []
        for val in value_arr:
            subventions.append(
                {
                    'type': 'driver_fix',
                    'subvention_rule_id': 'subvention_rule_id',
                    'payoff': {'amount': '0', 'currency': 'RUB'},
                    'period': {
                        'start_time': val['start'],
                        'end_time': val['end'],
                    },
                    'commission_info': {
                        'payoff_commission': {
                            'amount': '10',
                            'currency': 'RUB',
                        },
                    },
                    'details': {
                        'accounted_time_seconds': val['time'],
                        'cash_income': {'amount': '0', 'currency': 'RUB'},
                        'guarantee': {
                            'amount': str(val['amount']),
                            'currency': 'RUB',
                        },
                        'cash_commission': {'amount': '0', 'currency': 'RUB'},
                    },
                },
            )
        return {'subventions': subventions}

    response = await taxi_driver_fix.get(
        'v1/view/status',
        params=common.get_enriched_params(None, panel_body_hash),
        headers=common.DEFAULT_HEADERS_FROM_DRIVER_AUTHPROXY,
    )
    assert response.status_code == 200
    doc = response.json()

    assert doc['status'] == 'subscribed'

    if calc_panel_body_hash:
        if panel_body_hash == ITEMS_HASH:
            assert 'panel_body' not in doc
            return
        assert doc['panel_body']['hash'] == ITEMS_HASH
    else:
        assert 'hash' not in doc['panel_body']

    ctor = doc['panel_body']['items'][0]
    assert ctor['title'] == 'Не те классы (preview)'
    assert (
        ctor['payload']['items'][1]['title'] == 'Нужны классы Эконом, Комфорт'
    )

    assert (
        doc['panel_body']['collapsed_panel_last_item_busy'] == 'restrictions'
    )
    assert (
        doc['panel_body']['collapsed_panel_last_item_free'] == 'restrictions'
    )
