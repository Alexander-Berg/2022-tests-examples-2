import pytest

from tests_eats_restapp_marketing import experiments


async def request_proxy_create_bulk_exp(taxi_eats_restapp_marketing, places):
    url = '/internal/marketing/v1/ad/create-bulk-experiment'
    body = {'places': places}
    extra = {'json': body}

    return await taxi_eats_restapp_marketing.post(url, **extra)


@pytest.mark.config(
    EATS_RESTAPP_MARKETING_ADVERT_RATING_THRESHOLD={
        'rating_threshold': 3.5,
        'is_enabled': True,
        'batch_size': 1000,
        'periodic': {'interval_seconds': 3600},
    },
)
@experiments.token_id_for_exp()
@pytest.mark.parametrize(
    'campaigns, code',
    [
        pytest.param(
            [
                {
                    'place_id': 1,
                    'averagecpc': 2,
                    'weekly_spend_limit': 5,
                    'experiment': 'foo_exp1',
                },
                {'place_id': 2, 'averagecpc': 2, 'experiment': 'foo_exp2'},
                {'place_id': 2, 'averagecpc': 3, 'experiment': 'foo_exp3'},
            ],
            201,
            id='all_exp',
            marks=pytest.mark.pgsql(
                'eats_tokens', files=['insert_tokens.sql'],
            ),
        ),
        pytest.param(
            [
                {'place_id': 1, 'averagecpc': 2, 'weekly_spend_limit': 5},
                {'place_id': 2, 'averagecpc': 2, 'experiment': 'foo_exp2'},
                {'place_id': 2, 'averagecpc': 3, 'experiment': 'foo_exp3'},
            ],
            400,
            id='at leats one no exp',
            marks=pytest.mark.pgsql(
                'eats_tokens', files=['insert_tokens.sql'],
            ),
        ),
        pytest.param(
            [
                {
                    'place_id': 1,
                    'averagecpc': 2,
                    'weekly_spend_limit': 5,
                    'experiment': 'foo_exp1',
                },
                {'place_id': 2, 'averagecpc': 2, 'experiment': 'foo_exp2'},
                {'place_id': 2, 'averagecpc': 3, 'experiment': 'foo_exp3'},
            ],
            403,
            id='no token',
        ),
    ],
)
async def test_create_bulk_exp(
        taxi_eats_restapp_marketing,
        mock_blackbox_tokeninfo,
        mock_auth_partner,
        mock_authorizer_allowed,
        mock_rating_info_ok,
        campaigns,
        code,
        pgsql,
):
    response = await request_proxy_create_bulk_exp(
        taxi_eats_restapp_marketing, campaigns,
    )
    cursor = pgsql['eats_restapp_marketing'].cursor()

    assert response.status_code == code
    if code == 201:
        cursor = pgsql['eats_restapp_marketing'].cursor()
        cursor.execute(
            """
                SELECT
                place_id, averagecpc,
                weekly_spend_limit, experiment
                FROM eats_restapp_marketing.advert
        """,
        )
        assert set(cursor) == {
            (1, 2000000, 5000000, 'foo_exp1'),
            (2, 2000000, None, 'foo_exp2'),
            (2, 3000000, None, 'foo_exp3'),
        }

        cursor.execute(
            """
                SELECT a.place_id,ac.token_id 
                FROM eats_restapp_marketing.advert_for_create as ac
                LEFT JOIN eats_restapp_marketing.advert a on a.id = ac.advert_id;
        """,
        )
        assert set(cursor) == {(1, 1), (2, 1), (2, 1)}
