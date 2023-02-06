import pytest

CURRENCY_RULES = {
    '__default__': {
        'code': 'RUB',
        'sign': '₽',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
    },
    'RUB': {
        'code': 'RUB',
        'sign': '₽',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
    },
    'BYN': {
        'code': 'BYN',
        'sign': 'р.',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'руб.',
    },
    'KZT': {
        'code': 'KZT',
        'sign': '₸',
        'template': '$VALUE$ $SIGN$$CURRENCY$',
        'text': 'тнг.',
    },
}


def currency_rules_config():
    return pytest.mark.config(EATS_ORDERS_INFO_CURRENCY_RULES=CURRENCY_RULES)


def get_actual_metrics(metrics_before_test, metrics_after_test):
    actual_metrics = {}
    for metric in metrics_after_test.keys():
        if metric in metrics_before_test.keys():
            actual_metrics[metric] = (
                metrics_after_test[metric] - metrics_before_test[metric]
            )
        else:
            actual_metrics[metric] = metrics_after_test[metric]
    return actual_metrics


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_digests_data.sql',),
)
@currency_rules_config()
@pytest.mark.parametrize(
    'request_body,status_code,places_count,'
    + 'has_active_place,has_no_orders_place,has_inactive_place',
    [
        pytest.param(
            {'digests': [{}]},
            400,
            0,
            False,
            False,
            False,
            id='digests_empty_request',
        ),
        pytest.param(
            {'digests': [{'place_id': 99, 'period_date': '2022-04-20'}]},
            200,
            0,
            False,
            False,
            False,
            id='digests_nonexisting_place_id_and_existing_date',
        ),
        pytest.param(
            {'digests': [{'place_id': 1, 'period_date': '2021-09-15'}]},
            200,
            0,
            False,
            False,
            False,
            id='digests_existing_place_id_and_nonexisting_date',
        ),
        pytest.param(
            {'digests': [{'place_id': 1, 'period_date': '2022-04-20'}]},
            200,
            1,
            True,
            False,
            False,
            id='digests_active_place',
        ),
        pytest.param(
            {'digests': [{'place_id': 2, 'period_date': '2022-04-20'}]},
            200,
            1,
            False,
            True,
            False,
            id='digests_no_orders_place',
        ),
        pytest.param(
            {'digests': [{'place_id': 3, 'period_date': '2022-04-20'}]},
            200,
            1,
            False,
            False,
            True,
            id='digests_inactive_place',
        ),
        pytest.param(
            {
                'digests': [
                    {'place_id': 1, 'period_date': '2022-04-20'},
                    {'place_id': 2, 'period_date': '2022-04-20'},
                    {'place_id': 3, 'period_date': '2022-04-20'},
                ],
            },
            200,
            3,
            True,
            True,
            True,
            id='digests_multiples_places',
        ),
    ],
)
async def test_get_digests(
        taxi_eats_report_storage,
        mock_catalog_storage,
        request_body,
        status_code,
        places_count,
        has_active_place,
        has_no_orders_place,
        has_inactive_place,
):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests', json=request_body,
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        digests = response.json()['digests']
        assert len(digests) == places_count
        assert (
            any(place['status'] == 'active' for place in digests)
            == has_active_place
        )
        assert (
            any(place['status'] == 'no_orders' for place in digests)
            == has_no_orders_place
        )
        assert (
            any(place['status'] == 'inactive' for place in digests)
            == has_inactive_place
        )


EXPECTED_RESPONSE = {
    'digests': [
        {
            'place_id': 1,
            'period_date': '2022-04-20',
            'place_name': 'Place1',
            'place_address': 'Москва',
            'status': 'active',
            'delivery_type': 'native',
            'orders_total_cnt': '100',
            'orders_total_cnt_delta': '(+11%)',
            'orders_success_cnt': '80',
            'orders_success_cnt_delta': '(-11%)',
            'avg_cheque': '188₽',
            'avg_cheque_delta': '(+11%)',
            'cancels_pcnt': '20%',
            'cancels_pcnt_delta': '(+20%)',
            'revenue_earned_lcy': '15 000₽',
            'revenue_earned_delta_lcy': '(-2%)',
            'revenue_lost_lcy': '128₽',
            'revenue_lost_delta_lcy': '(+ >300%)',
            'fines_lcy': '50₽',
            'fines_delta_lcy': '(+ >300%)',
            'delay_min': '100 мин',
            'delay_delta_min': '(-9%)',
            'rating': '4.5',
            'rating_delta': '(+0.1)',
            'availability_pcnt': '80%',
            'availability_delta_pcnt': '(-20%)',
        },
    ],
}


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_digests_data.sql',),
)
@currency_rules_config()
async def test_get_digests_correct_data(
        taxi_eats_report_storage, mock_catalog_storage,
):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests',
        json={'digests': [{'place_id': 1, 'period_date': '2022-04-20'}]},
    )
    assert response.status_code == 200
    assert response.json() == EXPECTED_RESPONSE


EXPECTED_RESPONSE_BY_STATS = {
    'digests': [
        {
            'place_id': 1,
            'period_date': '2022-04-20',
            'place_name': 'Place1',
            'place_address': 'Москва',
            'status': 'active',
            'delivery_type': 'native',
            'fines_lcy': '50₽',
            'fines_delta_lcy': '(+ >300%)',
            'delay_min': '100 мин',
            'delay_delta_min': '(-9%)',
            'rating': '4.5',
            'rating_delta': '(+0.1)',
            'availability_pcnt': '80%',
            'availability_delta_pcnt': '(-20%)',
        },
    ],
}


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_digests_data.sql',),
)
@currency_rules_config()
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_report_storage_digest_strategy',
    consumers=['eats_report_storage/digests'],
    clauses=[],
    default_value={'strategy': 'metrics'},
)
@pytest.mark.parametrize(
    'timezone,data',
    [
        pytest.param(
            'Europe/Moscow',
            {
                'orders_total_cnt': '40',
                'orders_total_cnt_delta': '(+100%)',
                'orders_success_cnt': '30',
                'orders_success_cnt_delta': '(+50%)',
                'avg_cheque': '10₽',
                'avg_cheque_delta': '(-33%)',
                'cancels_pcnt': '25%',
                'cancels_pcnt_delta': '(+25%)',
                'revenue_earned_lcy': '300₽',
                'revenue_earned_delta_lcy': '(0%)',
                'revenue_lost_lcy': '100₽',
                'revenue_lost_delta_lcy': '(+ >300%)',
            },
        ),
        pytest.param(
            'Europe/Saratov',
            {
                'orders_total_cnt': '220',
                'orders_total_cnt_delta': '(+100%)',
                'orders_success_cnt': '165',
                'orders_success_cnt_delta': '(+50%)',
                'avg_cheque': '10₽',
                'avg_cheque_delta': '(-33%)',
                'cancels_pcnt': '25%',
                'cancels_pcnt_delta': '(+25%)',
                'revenue_earned_lcy': '1 650₽',
                'revenue_earned_delta_lcy': '(0%)',
                'revenue_lost_lcy': '550₽',
                'revenue_lost_delta_lcy': '(+ >300%)',
            },
        ),
    ],
)
async def test_get_digests_data_from_metrics(
        taxi_eats_report_storage, mockserver, timezone, data,
):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        + 'eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _mock_catalog_storage(request):
        req = request.json
        assert req['place_ids'] == [1]
        assert req['projection'] == ['region']
        return {
            'places': [
                {
                    'id': 1,
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'time_zone': timezone,
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                },
            ],
            'not_found_place_ids': [],
        }

    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests',
        json={'digests': [{'place_id': 1, 'period_date': '2022-04-20'}]},
    )
    assert response.status_code == 200
    expected = EXPECTED_RESPONSE_BY_STATS.copy()
    expected['digests'][0].update(data)
    assert response.json() == expected


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_digests_data.sql',),
)
@currency_rules_config()
async def test_get_digests_empty_work_time(
        taxi_eats_report_storage, mock_catalog_storage,
):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests',
        json={'digests': [{'place_id': 4, 'period_date': '2022-04-20'}]},
    )
    assert response.status_code == 200
    expected = EXPECTED_RESPONSE.copy()
    expected['digests'][0].pop('availability_pcnt')
    expected['digests'][0].pop('availability_delta_pcnt')
    expected['digests'][0]['place_id'] = 4
    expected['digests'][0]['place_name'] = 'Place4'
    assert response.json() == expected


@pytest.mark.pgsql(
    'eats_report_storage',
    files=('eats_report_storage_digests_data_for_metrics.sql',),
)
@currency_rules_config()
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_report_storage_digest_strategy',
    consumers=['eats_report_storage/digests'],
    clauses=[],
    default_value={'strategy': 'metrics'},
)
@pytest.mark.parametrize(
    'place_id,expected_metrics',
    [
        pytest.param(
            1,
            {
                'orders_total_cnt_diff': 0,
                'orders_total_cnt_delta_diff': 0,
                'orders_success_cnt_diff': 0,
                'orders_success_cnt_delta_diff': 0,
                'revenue_earned_lcy_diff': 0,
                'revenue_earned_delta_lcy_diff': 0,
                'revenue_lost_lcy_diff': 0,
                'revenue_lost_delta_lcy_diff': 0,
            },
            id='same_data',
        ),
        pytest.param(
            2,
            {
                'orders_total_cnt_diff': 1,
                'orders_total_cnt_delta_diff': 1,
                'orders_success_cnt_diff': 1,
                'orders_success_cnt_delta_diff': 1,
                'revenue_earned_lcy_diff': 0,
                'revenue_earned_delta_lcy_diff': 0,
                'revenue_lost_lcy_diff': 0,
                'revenue_lost_delta_lcy_diff': 0,
            },
            id='different_orders',
        ),
        pytest.param(
            3,
            {
                'orders_total_cnt_diff': 0,
                'orders_total_cnt_delta_diff': 0,
                'orders_success_cnt_diff': 0,
                'orders_success_cnt_delta_diff': 0,
                'revenue_earned_lcy_diff': 1,
                'revenue_earned_delta_lcy_diff': 1,
                'revenue_lost_lcy_diff': 1,
                'revenue_lost_delta_lcy_diff': 1,
            },
            id='different_revenue',
        ),
        pytest.param(
            4,
            {
                'orders_total_cnt_diff': 1,
                'orders_total_cnt_delta_diff': 1,
                'orders_success_cnt_diff': 1,
                'orders_success_cnt_delta_diff': 1,
                'revenue_earned_lcy_diff': 1,
                'revenue_earned_delta_lcy_diff': 1,
                'revenue_lost_lcy_diff': 1,
                'revenue_lost_delta_lcy_diff': 1,
            },
            id='zero_fact_work_time',
        ),
        pytest.param(
            5,
            {
                'orders_total_cnt_diff': 1,
                'orders_total_cnt_delta_diff': 1,
                'orders_success_cnt_diff': 1,
                'orders_success_cnt_delta_diff': 1,
                'revenue_earned_lcy_diff': 1,
                'revenue_earned_delta_lcy_diff': 1,
                'revenue_lost_lcy_diff': 1,
                'revenue_lost_delta_lcy_diff': 1,
            },
            id='no_orders',
        ),
    ],
)
async def test_get_digests_stats_diff_metrics(
        taxi_eats_report_storage,
        taxi_eats_report_storage_monitor,
        mockserver,
        place_id,
        expected_metrics,
):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/'
        + 'eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    async def _mock_catalog_storage(request):
        req = request.json
        assert req['place_ids'] == [place_id]
        assert req['projection'] == ['region']
        return {
            'places': [
                {
                    'id': place_id,
                    'region': {
                        'id': 1,
                        'geobase_ids': [],
                        'time_zone': 'Europe/Moscow',
                    },
                    'revision_id': 1,
                    'updated_at': '2022-04-22T11:44:47.385057+00:00',
                },
            ],
            'not_found_place_ids': [],
        }

    metrics_before_test = await taxi_eats_report_storage_monitor.get_metric(
        metric_name='digests-component',
    )

    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests',
        json={
            'digests': [{'place_id': place_id, 'period_date': '2022-04-20'}],
        },
    )
    assert response.status_code == 200

    metrics_after_test = await taxi_eats_report_storage_monitor.get_metric(
        metric_name='digests-component',
    )

    actual_metrics = get_actual_metrics(
        metrics_before_test['digests-stats'],
        metrics_after_test['digests-stats'],
    )

    assert actual_metrics == expected_metrics


@pytest.mark.pgsql(
    'eats_report_storage', files=('eats_report_storage_digests_data.sql',),
)
@currency_rules_config()
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    is_config=True,
    name='eats_report_storage_digest_strategy',
    consumers=['eats_report_storage/digests'],
    clauses=[],
    default_value={'strategy': 'fallback'},
)
async def test_get_digests_data_from_fallback(
        taxi_eats_report_storage, mock_catalog_storage,
):
    response = await taxi_eats_report_storage.post(
        '/internal/place-metrics/v1/digests',
        json={'digests': [{'place_id': 1, 'period_date': '2022-04-20'}]},
    )
    assert response.status_code == 200
    expected = EXPECTED_RESPONSE_BY_STATS.copy()
    expected['digests'][0].update(
        {
            'orders_total_cnt': '200',
            'orders_total_cnt_delta': '(+33%)',
            'orders_success_cnt': '100',
            'orders_success_cnt_delta': '(-33%)',
            'avg_cheque': '30₽',
            'avg_cheque_delta': '(+50%)',
            'cancels_pcnt': '50%',
            'cancels_pcnt_delta': '(+50%)',
            'revenue_earned_lcy': '3 000₽',
            'revenue_earned_delta_lcy': '(0%)',
            'revenue_lost_lcy': '1 000₽',
            'revenue_lost_delta_lcy': '(+ >300%)',
        },
    )
    assert response.json() == expected
