import datetime
from typing import List

import pytest

from rida.logic import rating
from rida.models import user_rating as user_rating_models
from test_rida import experiments_utils
from test_rida import helpers


_NOW = datetime.datetime(2020, 2, 26, 13, 50)
RIDA_RATING_SETTINGS_NO_FAKE = dict(
    driver=dict(
        rating_window_size=4,
        new_user_ratings_count=0,
        new_user_ratings_average=5,
    ),
    user=dict(
        rating_window_size=4,
        new_user_ratings_count=0,
        new_user_ratings_average=5,
    ),
)


@pytest.mark.parametrize(
    [
        'rating_window_size',
        'fake_ratings_count',
        'fake_ratings_average',
        'real_ratings_count',
        'real_ratings_average',
        'expected_rating',
    ],
    [
        pytest.param(40, 20, 5, 0, 3, 5.0, id='fake_orders_only'),
        pytest.param(40, 20, 5, 10, 3, 4.33, id='mostly_fake'),
        pytest.param(40, 20, 5, 20, 3, 4.0, id='fake_and_real'),
        pytest.param(40, 20, 5, 30, 3, 3.5, id='mostly_real'),
        pytest.param(40, 20, 5, 60, 3, 3.0, id='real_only'),
    ],
)
def test_rating_math(
        rating_window_size: int,
        fake_ratings_count: int,
        fake_ratings_average: float,
        real_ratings_count: int,
        real_ratings_average: float,
        expected_rating: float,
):
    new_rating = rating._calc_rating(  # pylint: disable=protected-access
        rating_settings={
            'rating_window_size': rating_window_size,
            'new_user_ratings_count': fake_ratings_count,
            'new_user_ratings_average': fake_ratings_average,
        },
        review_stats=user_rating_models.ReviewStats(
            avg_rating=real_ratings_average, total_reviews=real_ratings_count,
        ),
        offers_stats=None,
        cancel_penalty_rules=None,
    )
    assert new_rating.value == expected_rating


@pytest.mark.parametrize('review_type', ['user_review', 'driver_review'])
@pytest.mark.parametrize('request_body_as_query', [True, False])
async def test_create_review(
        web_app_client, review_type: str, request_body_as_query: bool,
):
    request_body = {
        'comment': 'Lol',
        'driver_guid': '2fb03e4e-fdb4-4d07-8233-82ae98e7e7db',
        'offer_guid': 'EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
        'rating': 5,
        'review_type': review_type,
        'user_guid': '4fa5f519-8fc7-4315-af81-dcf580f5d9df',
    }
    request_params = {'headers': helpers.get_auth_headers(user_id=1234)}
    if request_body_as_query:
        request_body['rating'] = str(request_body['rating'])
        request_params['data'] = request_body
    else:
        request_params['json'] = request_body

    response = await web_app_client.post('/v1/createReview', **request_params)
    assert response.status == 200


async def _create_ratings(
        web_app,
        review_type: str,
        user_guid: str,
        driver_guid: str,
        ratings: List[int],
) -> None:
    query_tpl = """
    INSERT INTO user_ratings (
        offer_guid,
        user_guid,
        driver_guid,
        review_type,
        rating,
        created_at,
        updated_at
    ) VALUES (
        '{offer_guid}',
        '{user_guid}',
        '{driver_guid}',
        '{review_type}',
        {rating},
        '{created_at}',
        '{updated_at}'
    )
    """
    async with web_app['context'].pg.rw_pool.acquire() as connection:
        for i, review_rating in enumerate(ratings):
            now = _NOW + datetime.timedelta(seconds=i)
            query = query_tpl.format(
                offer_guid=str(i).rjust(36),
                user_guid=user_guid,
                driver_guid=driver_guid,
                review_type=review_type,
                rating=review_rating,
                created_at=now.isoformat(sep=' '),
                updated_at=now.isoformat(sep=' '),
            )
            await connection.execute(query)


async def create_passenger_ratings(
        web_app, user_guid: str, ratings: List[int],
) -> None:
    await _create_ratings(
        web_app=web_app,
        review_type='driver_review',
        user_guid=user_guid,
        driver_guid='EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
        ratings=ratings,
    )


async def create_driver_ratings(
        web_app, driver_guid: str, ratings: List[int],
) -> None:
    await _create_ratings(
        web_app=web_app,
        review_type='user_review',
        user_guid='EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
        driver_guid=driver_guid,
        ratings=ratings,
    )


async def check_passenger_rating(
        web_app, user_guid: str, expected_rating: float,
) -> None:
    query = f"""
    SELECT avg_rating
    FROM users
    WHERE guid='{user_guid}'
    """
    async with web_app['context'].pg.ro_pool.acquire() as connection:
        record = await connection.fetchrow(query)
    assert float(record['avg_rating']) == expected_rating


async def check_driver_rating(
        web_app, driver_guid: str, expected_rating: float,
) -> None:
    query = f"""
    SELECT avg_rating
    FROM drivers
    WHERE guid='{driver_guid}'
    """
    async with web_app['context'].pg.ro_pool.acquire() as connection:
        record = await connection.fetchrow(query)
    assert float(record['avg_rating']) == expected_rating


@pytest.mark.config(
    RIDA_RATING_SETTINGS=dict(
        driver=dict(
            rating_window_size=4,
            new_user_ratings_count=2,
            new_user_ratings_average=5,
        ),
        user=dict(
            rating_window_size=4,
            new_user_ratings_count=2,
            new_user_ratings_average=5,
        ),
    ),
)
@pytest.mark.parametrize('review_type', ['user_review', 'driver_review'])
@pytest.mark.parametrize(
    ['existing_ratings', 'new_rating', 'expected_rating'],
    [
        pytest.param([], 2, 4.0, id='1real_2fake_ratings_counted'),
        pytest.param([1], 1, 3.0, id='2real_2fake_ratings_counted'),
        pytest.param([1, 5], 1, 3.0, id='3real_1fake_ratings_counted'),
        pytest.param([1, 5, 5], 1, 3.0, id='4real_ratings_counted'),
        pytest.param([1, 5, 5, 5, 5], 1, 4.0, id='last_4real_ratings_counted'),
    ],
)
async def test_set_rating(
        web_app,
        web_app_client,
        review_type: str,
        existing_ratings: List[int],
        new_rating: int,
        expected_rating: int,
):
    user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B'
    driver_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
    if review_type == 'user_review':
        await create_driver_ratings(web_app, driver_guid, existing_ratings)
    else:
        await create_passenger_ratings(web_app, user_guid, existing_ratings)

    response = await web_app_client.post(
        '/v1/createReview',
        headers=helpers.get_auth_headers(user_id=1234),
        json={
            'offer_guid': 'EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
            'driver_guid': driver_guid,
            'user_guid': user_guid,
            'review_type': review_type,
            'rating': new_rating,
        },
    )
    assert response.status == 200

    if review_type == 'user_review':
        await check_driver_rating(web_app, driver_guid, expected_rating)
    else:
        await check_passenger_rating(web_app, user_guid, expected_rating)


@pytest.mark.config(RIDA_RATING_SETTINGS=RIDA_RATING_SETTINGS_NO_FAKE)
async def test_upsert_existing_review(web_app, web_app_client):
    driver_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
    for expected_rating in range(4, 6):
        response = await web_app_client.post(
            '/v1/createReview',
            headers=helpers.get_auth_headers(user_id=1234),
            json={
                'offer_guid': 'EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
                'driver_guid': driver_guid,
                'user_guid': '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
                'review_type': 'user_review',
                'rating': expected_rating,
            },
        )
        assert response.status == 200
        await check_driver_rating(web_app, driver_guid, expected_rating)


@pytest.mark.pgsql('rida', files=['pg_rida.sql', 'pg_rida_extra.sql'])
@pytest.mark.config(RIDA_RATING_SETTINGS=RIDA_RATING_SETTINGS_NO_FAKE)
@pytest.mark.now('2022-02-24T12:22:22')
@pytest.mark.parametrize(
    ['expected_passenger_rating', 'expected_driver_rating'],
    [
        pytest.param(
            5, 5, marks=experiments_utils.get_penalty_exp(), id='no_clauses',
        ),
        pytest.param(
            4,
            5,
            marks=experiments_utils.get_penalty_exp(
                passenger_rules=[experiments_utils.PenaltyRule(penalty=1)],
            ),
            id='simple_user_penalty',
        ),
        pytest.param(
            5,
            4,
            marks=experiments_utils.get_penalty_exp(
                driver_rules=[experiments_utils.PenaltyRule(penalty=1)],
            ),
            id='simple_driver_penalty',
        ),
        pytest.param(
            1,
            5,
            marks=experiments_utils.get_penalty_exp(
                passenger_rules=[experiments_utils.PenaltyRule(penalty=1000)],
            ),
            id='very_big_penalty_value',
        ),
        pytest.param(
            5,
            5,
            marks=experiments_utils.get_penalty_exp(
                passenger_rules=[experiments_utils.PenaltyRule(penalty=-9)],
            ),
            id='negative_penalty_value',
        ),
        pytest.param(
            5,
            5,
            marks=experiments_utils.get_penalty_exp(
                recent_window_size_days=1,
                passenger_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=1, min_cancelled_orders=1,
                    ),
                ],
                driver_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=2, min_cancelled_orders=1,
                    ),
                ],
            ),
            id='cancelled_offers_outside_window_size',
        ),
        pytest.param(
            4,
            3,
            marks=experiments_utils.get_penalty_exp(
                recent_window_size_days=3,
                passenger_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=1, min_cancelled_orders=1,
                    ),
                ],
                driver_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=2, min_cancelled_orders=1,
                    ),
                ],
            ),
            id='cancelled_offers_inside_window_size',
        ),
        pytest.param(
            2.4,
            3.7,
            marks=experiments_utils.get_penalty_exp(
                # user has 4 offers: 1 complete, 2 cancelled w/ driver,
                # 1 cancelled w/o driver (not counted)
                passenger_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=4, min_cancelled_ratio=1,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=2.6, min_cancelled_ratio=0.6,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=1.3, min_cancelled_ratio=0.5,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=0.5, min_cancelled_ratio=0.4,
                    ),
                ],
                # driver has 2 offers: 1 complete, 1 cancelled w/ user
                driver_rules=[
                    experiments_utils.PenaltyRule(
                        penalty=4, min_cancelled_ratio=1,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=2.6, min_cancelled_ratio=0.6,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=1.3, min_cancelled_ratio=0.5,
                    ),
                    experiments_utils.PenaltyRule(
                        penalty=0.5, min_cancelled_ratio=0.4,
                    ),
                ],
            ),
            id='multiple_rule_clauses',
        ),
    ],
)
async def test_offer_cancel_penalty(
        web_app,
        web_app_client,
        expected_passenger_rating: float,
        expected_driver_rating: float,
):
    user_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B'
    driver_guid = '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C'
    common_payload: dict = {
        'offer_guid': 'EECDF6A4-A636-4139-BD93-EE9CF6E93EF2',
        'user_guid': user_guid,
        'driver_guid': driver_guid,
        'rating': 5,
    }

    # passenger feedback about driver
    passenger_response = await web_app_client.post(
        '/v1/createReview',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'review_type': 'user_review', **common_payload},
    )
    assert passenger_response.status == 200
    await check_driver_rating(web_app, driver_guid, expected_driver_rating)

    # driver feedback about passenger
    driver_response = await web_app_client.post(
        '/v1/createReview',
        headers=helpers.get_auth_headers(user_id=1234),
        json={'review_type': 'driver_review', **common_payload},
    )
    assert driver_response.status == 200
    await check_passenger_rating(web_app, user_guid, expected_passenger_rating)
