import pytest

from discounts_operation_calculations.generated.service.swagger.models import (
    api,
)
from discounts_operation_calculations.internals.statistics import (
    calc_discounts,
)


URL = '/v2/suggests/calc_discounts/'
URL_NEW = '/v2/suggests/v2/calc_discounts/'
SQL_FILES = [
    'fill_pg_suggests_v2.sql',
    'fill_pg_calc_segment_stats_tasks.sql',
    'fill_pg_segment_stats_all.sql',
    'fill_pg_city_stats.sql',
]
CONFIG = {'kt': {'control_share': 10}}
ELASTICITIES_CONFIG = {
    '0': 0,
    '1': 1.1,
    '2': 2,
    '3': 2.9,
    'ma_active_Hconv': 0,
    'ma_active_Lconv': 1.6,
    'ma_active_Mconv': 0.8,
    'ma_notactive_Hconv': 0,
    'ma_notactive_Lconv': 1.9,
    'ma_notactive_Mconv': 0.9,
    'not_ma_active_Hconv': 0,
    'not_ma_active_Lconv': 0.75,
    'not_ma_active_Mconv': 0,
    'not_ma_notactive_Hconv': 0,
    'not_ma_notactive_Lconv': 0.65,
    'not_ma_notactive_Mconv': 0.8,
    'random': 0.8,
}


@pytest.fixture(scope='function')
def mock_calc_multidraft_params(monkeypatch):
    async def calc_params(*_, **__):
        chart = api.ChartsItem(
            algorithm_id='algorithm_id',
            plot=api.Plot(
                x_label='Цена поездки',
                y_label='Скидка',
                label='segment',
                data=[[1.2, 0.0]],
            ),
        )
        return api.MultidraftParams(charts=[chart]), []

    monkeypatch.setattr(
        calc_discounts.DiscountsCalculator,
        '_calc_multidraft_params',
        calc_params,
    )


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS=CONFIG)
@pytest.mark.parametrize(
    'budget, expected_budget, expected_budget_share',
    [
        (100000.0, 100000.0, None),
        ({'gmv_share': 0.9}, 400503 * 0.9, 0.9),
        ({'gmv_share': 1.0}, 400503, 1),
        ({'gmv_share': 0.04}, 400503 * 0.04, 0.04),
    ],
)
@pytest.mark.usefixtures('mock_calc_multidraft_params')
async def test_calc_discounts_budget_save_to_db(
        web_app_client, pgsql, budget, expected_budget, expected_budget_share,
):
    data = {'suggest_id': 1, 'max_absolute_value': 600, 'budget': budget}
    response = await web_app_client.post(URL, json=data)
    assert response.status == 200, await response.text()

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        """
        SELECT budget, budget_share_in_gmv
        FROM discounts_operation_calculations.suggests
        WHERE id=1
        """,
    )
    [(res_budget, budget_share_in_gmv)] = list(cursor)
    assert res_budget == pytest.approx(expected_budget)
    assert budget_share_in_gmv == expected_budget_share

    cursor.close()


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS=CONFIG)
@pytest.mark.parametrize(
    'budget', [{'gmv_share': 1.2}, {'gmv_share': -14}, {'gmv_share': 0}, None],
)
async def test_calc_discounts_budget_error(web_app_client, budget):
    data = {
        'suggest_id': 1,
        'max_absolute_value': 600,
        **({'budget': budget} if budget else {}),
    }
    response = await web_app_client.post(URL, json=data)
    assert response.status == 400, await response.text()


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS=CONFIG)
@pytest.mark.usefixtures('mock_calc_multidraft_params')
@pytest.mark.parametrize(
    'input_data, output',
    [
        (
            {'suggest_id': 1, 'max_absolute_value': 600, 'budget': 100000.0},
            {
                'max_absolute_value': 600,
                'suggest_id': 1,
                'budget': 100000.0,
                'all_fixed_discounts': [
                    {'algorithm_id': 'kt', 'fixed_discounts': []},
                ],
            },
        ),
        (
            {
                'suggest_id': 1,
                'max_absolute_value': 12345,
                'budget': {'gmv_share': 0.33},
            },
            {
                'max_absolute_value': 12345,
                'suggest_id': 1,
                'budget': pytest.approx(0.33 * 400503.0),
                'budget_share_in_gmv': 0.33,
                'all_fixed_discounts': [
                    {'algorithm_id': 'kt', 'fixed_discounts': []},
                ],
            },
        ),
        (
            {
                'suggest_id': 1,
                'max_absolute_value': 12345,
                'budget': {'gmv_share': 1.0},
            },
            {
                'max_absolute_value': 12345,
                'suggest_id': 1,
                'budget': 400503.0,
                'budget_share_in_gmv': 1,
                'all_fixed_discounts': [
                    {'algorithm_id': 'kt', 'fixed_discounts': []},
                ],
            },
        ),
    ],
)
async def test_calc_discounts_budget_in_out(
        web_app_client, input_data, output,
):
    response = await web_app_client.post(URL, json=input_data)
    assert response.status == 200, await response.text()

    response = await web_app_client.get(f'/v2/suggests/1/detailed_info')
    assert response.status == 200, await response.text()

    data = await response.json()
    assert data['calc_discounts_params'] == output


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS=CONFIG)
@pytest.mark.usefixtures('mock_calc_multidraft_params')
@pytest.mark.parametrize(
    'budget, expected_budget, expected_budget_share',
    [
        (100000.0, 100000.0, None),
        ({'gmv_share': 0.9}, 400503 * 0.9, 0.9),
        ({'gmv_share': 1.0}, 400503, 1),
        ({'gmv_share': 0.04}, 400503 * 0.04, 0.04),
    ],
)
async def test_calc_discounts_v2_budget_save_to_db(
        web_app_client, pgsql, budget, expected_budget, expected_budget_share,
):
    data = {'suggest_id': 1, 'max_absolute_value': 600, 'budget': budget}
    response = await web_app_client.post(URL_NEW, json=data)
    assert response.status == 200, await response.text()

    cursor = pgsql['discounts_operation_calculations'].cursor()
    cursor.execute(
        """
        SELECT budget, budget_share_in_gmv
        FROM discounts_operation_calculations.suggests
        WHERE id=1
        """,
    )
    [(res_budget, budget_share_in_gmv)] = list(cursor)
    assert res_budget == pytest.approx(expected_budget)
    assert budget_share_in_gmv == expected_budget_share

    cursor.close()


@pytest.mark.config(
    DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS=CONFIG,
    DISCOUNTS_OPERATION_CALCULATIONS_SEGMENTS_MEAN_ELASTICITIES=(
        ELASTICITIES_CONFIG
    ),
)
@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
async def test_calc_discount_fallback_discount(
        web_app_client, set_segments_stats_suggest,
):
    # change suggest_id for segment_stats
    # to suggest with fallback discount and no push
    fallback_disc = 6
    suggest_id = 3
    set_segments_stats_suggest(suggest_id)
    data = {
        'suggest_id': suggest_id,
        'max_absolute_value': 600,
        'budget': 10000000,
    }
    response = await web_app_client.post(URL_NEW, json=data)
    assert response.status == 200

    content = await response.json()
    charts = content['multidraft_params']['charts']

    for chart in charts:
        if 'fallback' in chart['algorithm_id']:
            assert all(
                disc in (fallback_disc, 0)
                for bucket, disc in chart['plot']['data']
            )
        else:
            assert all(
                disc >= fallback_disc or disc == 0
                for bucket, disc in chart['plot']['data']
            )

    segments_with_disc = {c['plot']['label'] for c in charts}

    # fixed discounts
    assert 'random' in segments_with_disc
    assert 'control' in segments_with_disc
