# pylint: disable=import-only-modules

import pytest

from tests_eats_report_storage.conftest import make_rating_response
from tests_eats_report_storage.widgets.utils import consts


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_advert_stats.sql',),
)
async def test_advert_conversion_percent_multiplier(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'advert_conversion',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )
    chart = response.json()['payload']['charts'][0]
    assert [v['value'] for v in chart['points_data']] == [30.0, 20.0, 10.0]
    assert chart['total_value']['value'] == 50.0


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_advert_stats.sql',),
)
async def test_check_advert_gmv_with_html_without_extra(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_eats_place_rating,
        mock_core_places_info_request,
        rating_response,
):
    rating_response.set_data(make_rating_response(show_rating=True))
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'advert_gmv',
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )

    data = response.json()['payload']
    assert data['html_content'] == 'Тест html'
    assert 'extra_content' not in data
