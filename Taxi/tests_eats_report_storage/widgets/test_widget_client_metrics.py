import pytest

from tests_eats_report_storage.widgets.utils import consts


@pytest.mark.parametrize(
    'widget_slug, values, total_values, html, extra_main',
    [
        (
            'clients_gmv',
            [[0.8, 1.8, 2.8], [0.9, 1.9, 2.9]],
            [5.4, 5.7],
            '<h1>За выбранный период выручка составила: 11.10&nbsp;₽</h1><p></p>За счет постоянных: 5.40&nbsp;₽<br /> <p></p>За счет новых: 5.70&nbsp;₽<br />',  # noqa: E501
            'За выбранный период выручка составила: 11.10 ₽',
        ),
        ('clients_oldcommers_gmv_pcnt', [[7, 17, 27]], [48.65], None, None),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_clients_metrics_data.sql',),
)
async def test_return_clients_metrics(
        taxi_eats_report_storage,
        pgsql,
        mock_authorizer_200,
        mock_core_places_info_request,
        widget_slug,
        values,
        total_values,
        html,
        extra_main,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [1],
            'preset_period_type': 'custom',
            'period_begin': '2021-09-19T00:00:00+00:00',
            'period_end': '2021-09-21T00:00:00+00:00',
        },
    )

    data = response.json()['payload']
    for chart_id in range(len(data['charts'])):
        assert values[chart_id] == sorted(
            [
                item['value']
                for item in data['charts'][chart_id]['points_data']
            ],
        )
        assert (
            data['charts'][chart_id]['total_value']['value']
            == total_values[chart_id]
        )
    if html:
        assert data['html_content'] == html
    if extra_main:
        assert data['extra_content']['main_text'] == extra_main
