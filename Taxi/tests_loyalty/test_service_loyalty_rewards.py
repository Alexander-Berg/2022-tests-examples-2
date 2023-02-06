import pytest

from . import utils as test_utils


@pytest.mark.parametrize(
    'unique_driver_id, tags, zone_name, response_number, status_code',
    [
        ('000000000000000000000003', ['tag'], 'moscow', '1', 200),
        ('000000000000000000000001', ['tag'], 'moscow', '2', 200),
        ('000000000000000000000016', ['tag'], 'moscow', '3', 200),
        ('000000000000000000000017', ['tag'], 'moscow', '4', 200),
    ],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_recall(
        taxi_loyalty,
        experiments3,
        tags_mocks,
        load_json,
        unique_driver_id,
        tags,
        zone_name,
        response_number,
        status_code,
):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3('false'),
    )
    tags_mocks.set_tags_info(
        entity_type='udid', entity_value=unique_driver_id, entity_tags=tags,
    )

    body = {
        'driver_rewards': ['recall'],
        'data': {'unique_driver_id': unique_driver_id, 'zone_name': zone_name},
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == status_code
    response = response.json()
    expected_response = load_json(
        'response/recall' + response_number + '.json',
    )
    assert response == expected_response


@pytest.mark.parametrize(
    'unique_driver_id, tags, zone_name, activity, priority,'
    'response_number, status_code, with_priority',
    [
        (
            '000000000000000000000003',
            ['tag'],
            'moscow',
            100,
            100,
            '1',
            200,
            False,
        ),
        (
            '000000000000000000000001',
            ['tag'],
            'moscow',
            100,
            100,
            '2',
            200,
            False,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            100,
            100,
            '3',
            200,
            False,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            100,
            100,
            '4',
            200,
            False,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            60,
            60,
            '5',
            200,
            False,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            60,
            60,
            '6',
            200,
            False,
        ),
        ('0000000000000000000000', ['tag'], 'moscow', 60, 60, '7', 200, False),
        (
            '000000000000000000000016',
            ['bad_driver'],
            'moscow',
            100,
            100,
            '8',
            200,
            False,
        ),
        (
            '000000000000000000000003',
            ['tag'],
            'moscow',
            100,
            100,
            '1',
            200,
            True,
        ),
        (
            '000000000000000000000001',
            ['tag'],
            'moscow',
            100,
            100,
            '2',
            200,
            True,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            100,
            100,
            '3',
            200,
            True,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            100,
            100,
            '4x',
            200,
            True,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            60,
            60,
            '5',
            200,
            True,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            60,
            60,
            '6x',
            200,
            True,
        ),
        ('0000000000000000000000', ['tag'], 'moscow', 60, 60, '7', 200, True),
        (
            '000000000000000000000016',
            ['bad_driver'],
            'moscow',
            100,
            100,
            '8',
            200,
            True,
        ),
    ],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_point_b(
        taxi_loyalty,
        driver_metrics_storage,
        experiments3,
        tags_mocks,
        load_json,
        unique_driver_id,
        tags,
        activity,
        priority,
        zone_name,
        response_number,
        status_code,
        with_priority,
):
    driver_metrics_storage.set_priority_value(
        zone_name, unique_driver_id, tags, priority,
    )
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(with_priority),
    )
    tags_mocks.set_tags_info(
        entity_type='udid', entity_value=unique_driver_id, entity_tags=tags,
    )
    body = {
        'driver_rewards': ['point_b'],
        'data': {
            'unique_driver_id': unique_driver_id,
            'zone_name': zone_name,
            'activity': activity,
        },
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == status_code
    response = response.json()
    expected_response = load_json(
        'response/point_b' + response_number + '.json',
    )
    assert response == expected_response


@pytest.mark.parametrize(
    'unique_driver_id, tags,zone_name, activity, priority,'
    'response_number, status_code, with_priority',
    [
        (
            '000000000000000000000003',
            ['tag'],
            'moscow',
            100,
            100,
            '1',
            200,
            False,
        ),
        (
            '000000000000000000000001',
            ['tag'],
            'moscow',
            100,
            100,
            '2',
            200,
            False,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            100,
            100,
            '3',
            200,
            False,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            100,
            100,
            '4',
            200,
            False,
        ),
        (
            '000000000000000000000003',
            ['tag'],
            'moscow',
            100,
            100,
            '1',
            200,
            True,
        ),
        (
            '000000000000000000000001',
            ['tag'],
            'moscow',
            100,
            100,
            '2',
            200,
            True,
        ),
        (
            '000000000000000000000016',
            ['tag'],
            'moscow',
            100,
            100,
            '3',
            200,
            True,
        ),
        (
            '000000000000000000000017',
            ['tag'],
            'moscow',
            100,
            100,
            '4x',
            200,
            True,
        ),
    ],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_compose(
        taxi_loyalty,
        driver_metrics_storage,
        experiments3,
        tags_mocks,
        load_json,
        unique_driver_id,
        tags,
        activity,
        priority,
        zone_name,
        response_number,
        status_code,
        with_priority,
):
    driver_metrics_storage.set_priority_value(
        zone_name, unique_driver_id, tags, priority,
    )
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(with_priority),
    )
    tags_mocks.set_tags_info(
        entity_type='udid', entity_value=unique_driver_id, entity_tags=tags,
    )
    body = {
        'driver_rewards': ['point_b', 'recall'],
        'data': {
            'unique_driver_id': unique_driver_id,
            'zone_name': zone_name,
            'activity': activity,
        },
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == status_code
    response = response.json()
    expected_response = load_json(
        'response/' + 'compose' + response_number + '.json',
    )
    assert response == expected_response


@pytest.mark.parametrize(
    'priority, zone_name, expected_show_point_b, '
    'exp_clause_zone, exp_clause_thr, add_exp_clause',
    [
        (40, 'moscow', True, 'moscow', 39, True),
        (40, 'moscow', True, 'br_tsentralnyj_fo', 39, True),
        (40, 'moscow', True, 'br_russia', 39, True),
        (40, 'moscow', False, 'kazan', 39, True),
        (40, 'moscow', False, 'moscow', 39, False),
        (99, 'moscow', True, 'moscow', 39, False),
    ],
)
@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_priority_exp_zones_kwarg(
        taxi_loyalty,
        driver_metrics_storage,
        experiments3,
        tags_mocks,
        priority,
        zone_name,
        expected_show_point_b,
        exp_clause_zone,
        exp_clause_thr,
        add_exp_clause,
):
    unique_driver_id = '000000000000000000000017'
    tags = ['tag']

    driver_metrics_storage.set_priority_value(
        zone_name, unique_driver_id, tags, priority,
    )

    clauses = None
    if add_exp_clause:
        clauses = [
            test_utils.get_priority_exp_zones_clause(
                exp_clause_zone, exp_clause_thr,
            ),
        ]

    experiments3.add_experiment(
        **test_utils.make_priority_experiment3(True, clauses),
    )
    tags_mocks.set_tags_info(
        entity_type='udid', entity_value=unique_driver_id, entity_tags=tags,
    )
    body = {
        'driver_rewards': ['point_b', 'recall'],
        'data': {
            'unique_driver_id': unique_driver_id,
            'zone_name': zone_name,
            'activity': 100,
        },
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == 200

    response = response.json()

    value = (
        exp_clause_thr if add_exp_clause and exp_clause_zone != 'kazan' else 90
    )
    point_b = {
        'lock_reasons': {'priority': value},
        'show_point_b': expected_show_point_b,
    }
    if not (
            (
                exp_clause_zone != 'kazan'
                and add_exp_clause
                and priority >= exp_clause_thr
            )
            or (not add_exp_clause and priority >= 90)
    ):
        point_b['filtered_by'] = 'priority'

    expected_response = {
        'matched_driver_rewards': {
            'point_b': point_b,
            'recall': {'recall_type': 'recall'},
        },
    }

    assert response == expected_response


@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
@pytest.mark.match_tags(
    entity_type='udid',
    entity_value='000000000000000000000003',
    entity_tags=['tag'],
)
async def test_empty(taxi_loyalty, experiments3, pgsql, load_json):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3('false'),
    )
    body = {
        'driver_rewards': ['recall'],
        'data': {'unique_driver_id': '000000000000000000000003'},
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'loyalty', files=['loyalty_accounts.sql', 'loyalty_rewards.sql'],
)
async def test_tags(taxi_loyalty, experiments3, driver_tags_mocks):
    experiments3.add_experiment(
        **test_utils.make_priority_experiment3('false'),
    )
    driver_tags_mocks.set_tags_info('dbid', 'uuid', tags=['tag'])
    body = {
        'driver_rewards': ['point_b', 'recall'],
        'data': {
            'unique_driver_id': '000000000000000000000001',
            'park_id': 'dbid',
            'driver_profile_id': 'uuid',
            'zone_name': 'moscow',
            'activity': 100,
        },
    }
    response = await taxi_loyalty.post(
        '/service/loyalty/v1/rewards',
        json=body,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )
    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'matched_driver_rewards': {
            'recall': {},
            'point_b': {'lock_reasons': {}, 'show_point_b': False},
        },
    }
    assert response == expected_response
    assert driver_tags_mocks.v1_match_profile.times_called == 1
