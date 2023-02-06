import pytest


@pytest.mark.pgsql(
    'proxy_ml',
    queries=[
        """
        INSERT INTO driver_license_queue.requests
        (id, country, token, status, created, updated)
        VALUES ('123513213', 'rus', '1234567',
        'complete', current_timestamp, current_timestamp)
        """,
        """
        INSERT INTO driver_license_queue.responses
        (id, number, series, created)
        VALUES ('123513213', '813919', '1234', current_timestamp)
        """,
    ],
)
async def test_license_recognition_status(taxi_proxy_ml, pgsql):
    request_id = '123513213'
    token = '1234567'
    params = {'request_id': request_id, 'token': token}

    response = await taxi_proxy_ml.get(
        'selfreg/license_recognition_status', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'complete',
        'license': {'number': '813919', 'series': '1234'},
    }


@pytest.mark.pgsql(
    'proxy_ml',
    queries=[
        """
        INSERT INTO driver_license_queue.requests
        (id, country, token, status, created, updated, retry_count)
        VALUES ('123513213', 'rus', '1234567',
        'fail', current_timestamp, current_timestamp, 10)
        """,
    ],
)
@pytest.mark.now('2019-04-04T00:00:00+0300')
async def test_license_recognition_status_fail(taxi_proxy_ml, pgsql):
    request_id = '123513213'
    token = '1234567'
    params = {'request_id': request_id, 'token': token}

    response = await taxi_proxy_ml.get(
        'selfreg/license_recognition_status', params=params,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'fail'}
