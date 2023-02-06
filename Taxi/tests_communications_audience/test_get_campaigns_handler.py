import pytest


@pytest.mark.parametrize(
    'json_body,expected',
    [
        pytest.param(
            {
                'user': {
                    'yandex_uid': 'id-1',
                    'phone_ids': ['id-1'],
                    'personal_phone_ids': ['id-1'],
                    'device_ids': ['iphone'],
                },
            },
            {'campaigns': ['name-1']},
            id='simple',
        ),
        pytest.param({'user': {}}, {'campaigns': []}, id='empty'),
        pytest.param(
            {
                'user': {
                    'yandex_uid': 'id-1',
                    'phone_ids': ['8926', '8495'],
                    'personal_phone_ids': ['7896', '7657'],
                    'device_ids': ['iphone', 'android'],
                },
            },
            {'campaigns': ['name-1', 'name-2', 'name-3', 'name-4', 'name-5']},
            id='match_all',
        ),
        pytest.param(
            {
                'user': {
                    'yandex_uid': 'id-1',
                    'phone_ids': ['8926', '8495'],
                    'personal_phone_ids': ['7896436', '765724'],
                    'device_ids': ['iphone5', 'android6'],
                },
            },
            {'campaigns': ['name-1', 'name-2', 'name-3']},
            id='three_matches',
        ),
        pytest.param(
            {
                'user': {
                    'yandex_uid': '',
                    'phone_ids': [],
                    'personal_phone_ids': [],
                    'device_ids': [],
                },
            },
            {'campaigns': []},
            id='default',
        ),
    ],
)
@pytest.mark.ydb(files=['fill_audience.sql'])
async def test_get_campaigns(
        json_body, expected, taxi_communications_audience,
):
    response = await taxi_communications_audience.post(
        'communications-audience/v1/get_campaigns', json=json_body,
    )
    assert response.status_code == 200
    assert response.json() == expected
