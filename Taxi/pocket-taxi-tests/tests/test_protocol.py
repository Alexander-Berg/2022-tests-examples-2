import utils


PROTOCOL_BASE_URL = 'http://localhost/'


def test_protocol_launch():
    response = utils.retry_request(
        'post',
        PROTOCOL_BASE_URL + '3.0/launch',
        headers={
            'Content-Type': 'application/json',
        },
        json={},
    )
    assert response.status_code == 200
