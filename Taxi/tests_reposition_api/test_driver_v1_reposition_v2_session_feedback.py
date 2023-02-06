import pytest


def get_headers(dbid, uuid):
    return {
        'Accept-Language': 'en-EN',
        'X-YaTaxi-Park-Id': dbid,
        'X-YaTaxi-Driver-Profile-Id': uuid,
        'X-Request-Application': 'taximeter',
        'X-Request-Application-Version': '9.07 (1234)',
        'X-Request-Version-Type': '',
        'X-Request-Platform': 'android',
        'User-Agent': 'Taximeter 9.07 (1234)',
    }


@pytest.mark.parametrize(
    'request_body',
    [{'score': 1, 'choices': ['no_orders'], 'comment': 'test'}, {}],
)
@pytest.mark.pgsql(
    'reposition', files=['drivers.sql', 'mode_home.sql', 'feedback_data.sql'],
)
@pytest.mark.now('2019-10-14T18:18:46')
async def test_feedback(taxi_reposition_api, pgsql, mockserver, request_body):
    response = await taxi_reposition_api.put(
        '/driver/v1/reposition/v2/session/feedback'
        '?session_id=LkQWjnegglewZ1p0',
        json=request_body,
        headers=get_headers('1488', 'driverSS'),
    )

    assert response.status_code == 200
    assert response.json() == {
        'state': {
            'state': {'status': 'no_state'},
            'usages': {
                'home': {
                    'start_screen_usages': {'subtitle': '', 'title': ''},
                    'usage_allowed': True,
                    'usage_limit_dialog': {'body': '', 'title': ''},
                },
            },
        },
        'state_etag': '"2Q5xmbmQijboKM7W"',
    }
