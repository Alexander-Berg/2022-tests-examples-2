import pytest

from tests_eats_report_storage.widgets.utils import consts
from tests_eats_report_storage.widgets.utils import helpers


def get_honest_deltas_experiment(enabled: bool):
    return pytest.mark.experiments3(
        name='eats_report_storage_honest_deltas',
        consumers=['eats_report_storage/partner_id'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always true',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        is_config=True,
    )


def make_hour_values(pos_values):
    res = [0 for _ in range(0, 24)]
    for idx, val in pos_values.items():
        res[idx] = val
    return res


def make_hour_xlabels():
    return ['{}:00'.format(v) for v in range(0, 24)]


@pytest.mark.parametrize(
    'widget_slug, charts_len, points_len, total_value, delta_value, values',
    [
        pytest.param(
            'orderSuccessCount',
            1,
            4,
            '2 300',
            '1 625',
            [425, 525, 625, 725],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'orderSuccessCount',
            1,
            4,
            '2 300',
            '300',
            [425, 525, 625, 725],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'orderCancelCount',
            1,
            4,
            '2 000',
            '995',
            [500, 500, 500, 500],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'orderCancelCount',
            1,
            4,
            '2 000',
            '0',
            [500, 500, 500, 500],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'orderCount',
            1,
            4,
            '12 000',
            '5 970',
            [3000, 3000, 3000, 3000],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'orderCount',
            1,
            4,
            '12 000',
            '0',
            [3000, 3000, 3000, 3000],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'orderCancelPercentCount',
            1,
            4,
            '16.7 %',
            '0 %',
            [3, 2.5, 3, 2.5],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'orderCancelPercentCount',
            1,
            4,
            '16.7 %',
            '0.5 %',
            [3, 2.5, 3, 2.5],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'revenueEarned',
            1,
            4,
            '1 122.40 ₽',
            '769.40 ₽',
            [430.6, 330.6, 230.6, 130.6],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'revenueEarned',
            1,
            4,
            '1 122.40 ₽',
            '300 ₽',
            [430.6, 330.6, 230.6, 130.6],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'revenueLost',
            1,
            4,
            '241.76 ₽',
            '60.44 ₽',
            [60.44, 60.44, 60.44, 60.44],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'revenueLost',
            1,
            4,
            '241.76 ₽',
            '0 ₽',
            [60.44, 60.44, 60.44, 60.44],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'revenue',
            1,
            4,
            '576 002.80 ₽',
            '144 000.70 ₽',
            [144000.7, 144000.7, 144000.7, 144000.7],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'revenue',
            1,
            4,
            '576 002.80 ₽',
            '0 ₽',
            [144000.7, 144000.7, 144000.7, 144000.7],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'revenueAverage',
            1,
            4,
            '0.49 ₽',
            '2.31 ₽',
            [300.5, 300.5, 300.5, 300.5],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'revenueAverage',
            1,
            4,
            '0.49 ₽',
            '0 ₽',
            [300.5, 300.5, 300.5, 300.5],
            marks=(get_honest_deltas_experiment(False)),
        ),
        pytest.param(
            'placeAvailability',
            1,
            4,
            '50 %',
            '0 %',
            [50, 80.5, 50, 80.5],
            marks=(get_honest_deltas_experiment(True)),
        ),
        pytest.param(
            'placeAvailability',
            1,
            4,
            '50 %',
            '30.5 %',
            [50, 80.5, 50, 80.5],
            marks=(get_honest_deltas_experiment(False)),
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_common_data.sql',),
)
async def test_service_return_metrics_for_common_stats(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
        widget_slug,
        charts_len,
        points_len,
        total_value,
        delta_value,
        values,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': widget_slug,
            'places': [2],
            'preset_period_type': 'custom',
            'period_begin': '2021-11-08T00:00:00+00:00',
            'period_end': '2021-11-11T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    helpers.check_data_count(
        response.json()['payload'], charts_len, points_len,
    )
    helpers.check_data(
        response.json()['payload'],
        None,
        [total_value],
        [delta_value],
        [[v] for v in values],
        None,
        None,
        None,
        None,
    )
    assert [
        p['xlabel']
        for p in response.json()['payload']['charts'][0]['points_data']
    ] == ['08.11', '09.11', '10.11', '11.11']


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_common_data.sql',),
)
async def test_service_return_metrics_for_common_order_per_place(
        taxi_eats_report_storage,
        mock_authorizer_200,
        pgsql,
        mock_core_places_info_request,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'orderPerPace',
            'places': [1, 2],
            'preset_period_type': 'custom',
            'period_begin': '2021-11-08T00:00:00+00:00',
            'period_end': '2021-11-11T00:00:00+00:00',
        },
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    helpers.check_data_count(payload, 1, 4)
    points = payload['charts'][0]['points_data']
    assert [p['value'] for p in points] == [3000, 3000, 3000, 2000]
    assert [p['combined_count'] for p in points] == [1, 1, 1, 2]


@pytest.mark.parametrize(
    'group_by, charts_len, points_len, values, xlabels',
    [
        pytest.param(
            'day',
            1,
            7,
            [18, 23, 27, 32, 0, 0, 0],
            ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
        ),
        pytest.param(
            'hour',
            1,
            24,
            make_hour_values({3: 75, 15: 25}),
            make_hour_xlabels(),
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_common_data.sql',),
)
async def test_service_return_metrics_for_common_order_count_distribution(
        taxi_eats_report_storage,
        mock_authorizer_200,
        mock_core_places_info_request,
        pgsql,
        group_by,
        charts_len,
        points_len,
        values,
        xlabels,
):
    response = await taxi_eats_report_storage.post(
        '/4.0/restapp-front/reports/v1/place-metrics/widgets/get',
        headers={'X-YaEda-PartnerId': str(consts.PARTNER_ID)},
        json={
            'widget_slug': 'orderCountDistribution',
            'places': [2],
            'preset_period_type': 'custom',
            'period_begin': '2021-11-08T00:00:00+00:00',
            'period_end': '2021-11-11T00:00:00+00:00',
            'period_group_by': group_by,
        },
    )
    assert response.status_code == 200
    payload = response.json()['payload']
    helpers.check_data_count(payload, charts_len, points_len)
    points = payload['charts'][0]['points_data']
    assert [p['value'] for p in points] == values
    assert [p['xlabel'] for p in points] == xlabels
