# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.conftest import exp3_config_promo_types
from tests_eats_report_storage.widgets.utils import consts


@pytest.mark.now('2022-02-22T03:00')
@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_promo_metrics_data.sql',),
)
@exp3_config_promo_types()
@pytest.mark.parametrize(
    'place_id, promo_type, widget_slug, period_begin, period_end, values',
    [
        (
            1,
            'gift',
            'promo_orders_number_value',
            '2021-11-01T00:00:00+00:00',
            '2021-11-07T00:00:00+00:00',
            [[1, 1, 1, 0, 0, 0, 0]],
        ),
        (
            1,
            'gift',
            'promo_new_users',
            '2021-11-01T00:00:00+00:00',
            '2021-11-30T00:00:00+00:00',
            [[0, 1, 0, 1, 0], [1, 0, 0, 1, 0]],
        ),
        (
            1,
            'gift',
            'promo_mean_receipt_value',
            '2021-05-25T00:00:00+00:00',
            '2021-11-07T00:00:00+00:00',
            [[0, 2, 0, 0, 2, 0, 0]],
        ),
        (
            1,
            'gift',
            'promo_proceeds',
            '2021-11-01T00:00:00Z',
            '2021-11-30T00:00:00Z',
            [[0, 1, 0, 1, 0]],
        ),
        (
            2,
            'discount',
            'promo_orders_number_value',
            '2021-11-01T00:00:00+00:00',
            '2021-11-07T00:00:00+00:00',
            [[1, 1, 1, 0, 0, 0, 0]],
        ),
        (
            2,
            'discount',
            'promo_new_users',
            '2021-11-01T00:00:00+00:00',
            '2021-11-30T00:00:00+00:00',
            [[0, 1, 0, 1, 0], [1, 0, 0, 1, 0]],
        ),
        (
            2,
            'discount',
            'promo_mean_receipt_value',
            '2021-05-25T00:00:00+00:00',
            '2021-11-07T00:00:00+00:00',
            [[0, 2, 0, 0, 2, 0, 0]],
        ),
        (
            2,
            'discount',
            'promo_proceeds',
            '2021-11-01T00:00:00Z',
            '2021-11-30T00:00:00Z',
            [[0, 1, 0, 1, 0]],
        ),
    ],
)
async def test_service_return_promo_metrics(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
        place_id,
        promo_type,
        widget_slug,
        period_begin,
        period_end,
        values,
):
    request = {
        'widget_slug': widget_slug,
        'places': [place_id],
        'preset_period_type': 'custom',
        'period_begin': period_begin,
        'period_end': period_end,
    }
    if promo_type != 'all':
        request['additional_filters'] = {'promo_type': promo_type}
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json=request,
    )

    assert 'total_value' in response.json()['payload']['charts'][0]
    data = response.json()['payload']
    for chart_id in range(len(data['charts'])):
        for point_id in range(len(data['charts'][chart_id]['points_data'])):
            assert (
                data['charts'][chart_id]['points_data'][point_id]['value']
                == values[chart_id][point_id]
            )


@pytest.mark.parametrize(
    'promo_type',
    [
        pytest.param('haha', id='config off - not support type'),
        pytest.param('gift', id='config off - support type'),
        pytest.param(
            'haha',
            marks=[exp3_config_promo_types()],
            id='config on - not support type',
        ),
    ],
)
async def test_service_return_400_if_nonexisting_promo_type(
        taxi_eats_report_storage, mock_authorizer_200, promo_type,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'promo_proceeds',
            'places': [1],
            'preset_period_type': 'custom',
            'additional_filters': {'promo_type': promo_type},
            'period_begin': '2015-05-30T00:00:00Z',
            'period_end': '2015-06-04T00:00:00Z',
        },
    )

    assert response.json() == {'code': '400', 'message': 'Unknown promo type'}
