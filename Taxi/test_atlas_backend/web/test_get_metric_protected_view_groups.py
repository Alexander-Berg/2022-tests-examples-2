import pytest


@pytest.mark.config(
    ATLAS_METRICS_RESTRICTION_GROUPS={
        'view_groups': [
            {'en_name': 'CI+KD', 'id': 'ci_kd', 'ru_name': 'CI+KD'},
            {
                'en_name': 'Call center',
                'id': 'callcenter',
                'ru_name': 'Колл-центер',
            },
        ],
    },
)
async def test_get_metric_existed(web_app_client):
    response = await web_app_client.get(
        '/api/v2/metrics/protected_view_groups',
    )
    assert response.status == 200

    content = await response.json()
    assert content == [
        {'id': 'ci_kd', 'en_name': 'CI+KD', 'ru_name': 'CI+KD'},
        {
            'id': 'callcenter',
            'en_name': 'Call center',
            'ru_name': 'Колл-центер',
        },
    ]
