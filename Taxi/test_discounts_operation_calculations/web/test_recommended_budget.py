import pytest

CONTROL_SHARE = 20
BUDGET_CALCULATION_SETTINGS = {
    'surge_rate_pushes_bound': 0.3,
    'window_for_smoothing': 209,
    'window_for_derivation': 15,
    'break_point_value': 1.07,
    'min_city_population': 100000,
    'min_data_size': 300,
    'min_avg_discount_for_push': 0.1,
}

SQL_FILES = [
    'fill_pg_suggests_v2.sql',
    'fill_pg_calc_segment_stats_tasks.sql',
    'fill_pg_segment_stats_all.sql',
    'fill_pg_city_stats.sql',
]

CONFIG = {
    'DISCOUNTS_OPERATION_CALCULATIONS_RECOMMEND_BUDGET': {
        'budget_calculation': BUDGET_CALCULATION_SETTINGS,
    },
    'DISCOUNTS_OPERATION_CALCULATIONS_ALGORITHMS_CONFIGS': {
        'kt': {'control_share': CONTROL_SHARE},
    },
}


def json_body(suggest_id=1, fixed_discounts=True, max_gmv_percent=None):
    res = {'suggest_id': suggest_id}

    if fixed_discounts:
        res['all_fixed_discounts'] = [
            {
                'algorithm_id': 'kt',
                'fixed_discounts': [
                    {'segment': 'control', 'discount_value': 0},
                    {'segment': 'random', 'discount_value': 12},
                ],
            },
        ]

    if max_gmv_percent is not None:
        res['max_gmv_percent'] = max_gmv_percent

    return res


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
async def test_basic(web_app_client):
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/', json=json_body(),
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(fixed_discounts=False),
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(max_gmv_percent=0.1),
    )
    assert response.status == 200


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget(web_app_client):
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/', json=json_body(),
    )
    assert response.status == 200
    content = await response.json()

    assert content == {
        'gmv': pytest.approx(400504613.40460014),
        'budgets': [
            {
                'algorithm_id': 'kt',
                'min_budget': pytest.approx(1790111.3425919996),
                'max_budget': pytest.approx(13258680.33762982),
                'min_budget_with_push': None,
            },
        ],
        'push_data': [
            {
                'algorithm_id': 'kt',
                'trips_with_surge_rate': pytest.approx(0.02238095238095238),
                'send_pushes': False,
            },
        ],
    }


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_no_fixed_discounts(web_app_client):
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(fixed_discounts=False),
    )
    assert response.status == 200
    content = await response.json()

    assert content == {
        'gmv': pytest.approx(400504613.40460014),
        'budgets': [
            {
                'algorithm_id': 'kt',
                'min_budget': pytest.approx(1288657.52064),
                'max_budget': pytest.approx(19014163.888642672),
                'min_budget_with_push': None,
            },
        ],
        'push_data': [
            {
                'algorithm_id': 'kt',
                'trips_with_surge_rate': pytest.approx(0.02238095238095238),
                'send_pushes': False,
            },
        ],
    }


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.parametrize(
    'query, suggest_id, expected_code',
    [
        (
            """
            UPDATE discounts_operation_calculations.suggests
            SET status='FINISHED' WHERE id=1
            """,
            1,
            'BadRequest::WrongStatus',
        ),  # published suggest
        ('', 100500, 'BadRequest::InvalidSuggest'),  # non existing suggest
        (
            """
            UPDATE discounts_operation_calculations.suggests
            SET calc_segments_params=null WHERE id=1
            """,
            1,
            'BadRequest::InvalidSuggest',
        ),  # invalid suggest params
        (
            """
            UPDATE discounts_operation_calculations.suggests
            SET id=200 WHERE id = 1
            """,
            200,
            'BadRequest::InvalidSuggest',
        ),  # not synced suggest
    ],
)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_400(
        web_app_client, pgsql, query, suggest_id, expected_code,
):
    if query:
        cursor = pgsql['discounts_operation_calculations'].cursor()
        cursor.execute(query)
        cursor.close()

    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(suggest_id=suggest_id),
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == expected_code


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_max_gmv_percent(web_app_client):
    gmv_percent = 0.01
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(max_gmv_percent=gmv_percent),
    )
    assert response.status == 200
    content = await response.json()

    gmv = 400504613.40460014

    assert content['budgets'][0]['max_budget'] <= gmv * gmv_percent


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_small_max_gmv_percent(
        web_app_client, taxi_config,
):
    max_gmv_percent = 0.00001
    gmv = 400504613.40460014
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(max_gmv_percent=0.00001),
    )
    assert response.status == 400
    content = await response.json()
    assert content['code'] == 'BadRequest::WrongParams'
    assert content['message'] == (
        '"max_gmv_percent" value is too small. '
        'Unable to calculate budgets smaller than '
        f'{max_gmv_percent}% of city gmv = {gmv}'
    )


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(
    **{
        **CONFIG,  # type: ignore
        'DISCOUNTS_OPERATION_CALCULATIONS_RECOMMEND_BUDGET': {
            'budget_calculation': {
                **BUDGET_CALCULATION_SETTINGS,
                'surge_rate_pushes_bound': 0.0,
                'min_avg_discount_for_push': 10,
            },
        },
    },
)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_pushes(web_app_client, taxi_config):
    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/', json=json_body(),
    )
    assert response.status == 200
    content = await response.json()

    assert content == {
        'gmv': pytest.approx(400504613.40460014),
        'budgets': [
            {
                'algorithm_id': 'kt',
                'min_budget': pytest.approx(1790111.3425919996),
                'max_budget': pytest.approx(13258680.33762982),
                'min_budget_with_push': None,
            },
        ],
        'push_data': [
            {
                'algorithm_id': 'kt',
                'trips_with_surge_rate': pytest.approx(0.02238095238095238),
                'send_pushes': False,
            },
        ],
    }


@pytest.mark.pgsql('discounts_operation_calculations', files=SQL_FILES)
@pytest.mark.config(**CONFIG)
@pytest.mark.skip('this handle is totally broken anyway')
async def test_recommend_budget_fixed_discounts_from_table(
        web_app_client, pgsql,
):
    cursor = pgsql['discounts_operation_calculations'].cursor()
    # change suggest_id for segment_stats
    query = """UPDATE discounts_operation_calculations.segment_stats_all
    SET suggest_id = 2"""
    cursor.execute(query)
    cursor.close()

    response = await web_app_client.post(
        '/v2/suggests/recommended_budget/',
        json=json_body(suggest_id=2, fixed_discounts=False),
    )
    assert response.status == 200
    content = await response.json()

    assert content == {
        'gmv': pytest.approx(400504613.40460014),
        'budgets': [
            {
                'algorithm_id': 'kt',
                'min_budget': pytest.approx(12965335.961689657),
                'max_budget': pytest.approx(25125040.475854002),
                'min_budget_with_push': 12965335.961689657,
            },
        ],
        'push_data': [
            {
                'algorithm_id': 'kt',
                'trips_with_surge_rate': pytest.approx(0.02238095238095238),
                'send_pushes': True,
            },
        ],
    }
