import pytest


@pytest.mark.servicetest
@pytest.mark.pgsql('leaderboard_pg', files=['history.sql'])
@pytest.mark.now('2019-01-01T02:00:00')
@pytest.mark.parametrize(
    'month, expected_rank_history',
    [(None, [3, 2, 1]), (1, [3, 2, 1]), (12, [1]), (9, [1])],
)
async def test_leaderboard(taxi_leaderboard_web, month, expected_rank_history):
    params = {'login': 'ydemidenko'}
    if month:
        params['month'] = month
    response = await taxi_leaderboard_web.get('/v1/history/', params=params)
    assert response.status == 200
    content = await response.json()
    rank_history = [item['rank_place'] for item in content['items']]
    assert rank_history == expected_rank_history
