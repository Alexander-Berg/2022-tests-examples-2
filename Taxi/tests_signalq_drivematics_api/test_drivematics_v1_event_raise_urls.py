ENDPOINT = '/drivematics/signalq-drivematics-api/v1/event-raise-urls/generate'


async def test_drivematics_v1_event_raise_urls(taxi_signalq_drivematics_api):
    response = await taxi_signalq_drivematics_api.post(
        ENDPOINT,
        json={
            'url_parameteres': [
                {'serial_number': 'ab1', 'unix_timestamp': 1568635200},
                {
                    'serial_number': 'ab1',
                    'unix_timestamp': 1568635300,
                    'event_type': 'fart',
                },
            ],
        },
    )
    assert response.status_code == 200, response.text
    assert 'items' in response.json().keys()
    response.json()['items'].sort(key=lambda item: item['unix_timestamp'])
    assert response.json() == {
        'items': [
            {
                'serial_number': 'ab1',
                'unix_timestamp': 1568635200,
                'url': 'https://fleet.yandex-team.ru/api/fleet/signal-device-message-api/v1/event?jwt_signature=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXJpYWxfbnVtYmVyIjoiYWIxIiwiaWF0IjoxNTY4NjM1MjAwLCJldmVudF90eXBlIjoic3VwcG9ydF90aXJlZCJ9.PEzHoydzU1Tl_RLR4CN4lk3qIWLlHjCJhjAy5SamALE',  # noqa: E501 pylint: disable=line-too-long
            },
            {
                'serial_number': 'ab1',
                'unix_timestamp': 1568635300,
                'url': 'https://fleet.yandex-team.ru/api/fleet/signal-device-message-api/v1/event?jwt_signature=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzZXJpYWxfbnVtYmVyIjoiYWIxIiwiaWF0IjoxNTY4NjM1MzAwLCJldmVudF90eXBlIjoiZmFydCJ9.JFw6s8vFbQi1BmmHKNpdCaUZkSWxVJaQxaYYjK6d7FM',  # noqa: E501 pylint: disable=line-too-long
            },
        ],
    }
