import pytest


@pytest.mark.servicetest
@pytest.mark.pgsql('leaderboard_pg', files=['developers.sql'])
@pytest.mark.parametrize(
    'login, date_of_top, expected',
    [
        (
            'ydemidenko',
            '2019-01-01',
            {
                'items': [
                    {
                        'rank_place': 1,
                        'login': 'ydemidenko',
                        'rating': 4.0,
                        'additions': 4,
                        'deletions': 0,
                        'commits': 1,
                    },
                ],
            },
        ),
        (
            'ydemidenko',
            '2018-12-31',
            {
                'items': [
                    {
                        'rank_place': 1,
                        'login': 'ydemidenko',
                        'rating': 5.0,
                        'additions': 5,
                        'deletions': 0,
                        'commits': 1,
                    },
                ],
            },
        ),
        (
            'karachevda',
            '2019-01-01',
            {
                'items': [
                    {
                        'rank_place': 1,
                        'login': 'ydemidenko',
                        'rating': 4.0,
                        'additions': 4,
                        'deletions': 0,
                        'commits': 1,
                    },
                    {
                        'rank_place': 2,
                        'login': 'karachevda',
                        'rating': 0.0,
                        'additions': 0,
                        'deletions': 0,
                        'commits': 1,
                    },
                ],
            },
        ),
    ],
)
@pytest.mark.config(LEADERBOARD_TOP_SIZE=1)
async def test_leaderboard(taxi_leaderboard_web, login, date_of_top, expected):
    response = await taxi_leaderboard_web.get(
        '/v1/top/',
        params={'date_of_top': date_of_top},
        headers={'X-Yandex-Login': login},
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected
