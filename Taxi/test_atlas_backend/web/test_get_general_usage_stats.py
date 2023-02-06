async def test_get_general_usage_stats_requests(web_app_client):
    response = await web_app_client.post(
        '/api/usage_stat/general',
        json={
            'ts_from': 1602288000,
            'ts_to': 1602374400,
            'granularity': 5,
            'count_users': False,
            'api_names': [
                'api_metrics_plot',
                'api_metrics_map',
                'api_drivers_map',
                'api_metrics_leaderboard',
            ],
        },
    )
    # 1601856000
    assert response.status == 200
    data = await response.json()
    expected = [[1602288000, 3]]
    assert data == expected


async def test_get_general_usage_stats_users(web_app_client):
    response = await web_app_client.post(
        '/api/usage_stat/general',
        json={
            'ts_from': 1602288000,
            'ts_to': 1609372800,
            'granularity': 6,
            'count_users': True,
            'api_names': [
                'api_metrics_plot',
                'api_metrics_map',
                'api_drivers_map',
                'api_metrics_leaderboard',
            ],
        },
    )
    assert response.status == 200
    data = await response.json()
    expected = [[1601856000, 2], [1609113600, 1]]
    assert data == expected
