import pytest


@pytest.mark.now('2020-01-01T12:02:00+0000')
async def test_translates(taxi_eta_autoreorder):

    headers = {'X-Request-Language': 'ru'}
    response = await taxi_eta_autoreorder.get(
        '/internal/translates/autoreorder', headers=headers,
    )

    assert response.json() == {
        'status_info': {
            'translations': {
                'card': {
                    'title_template': (
                        'Водитель задерживается, уже ищем нового'
                    ),
                },
            },
        },
    }
