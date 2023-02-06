import pytest

DEFAULT_ERROR_CONTENT_TYPE = 'application/json; charset=utf-8'

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq'
    '_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXD'
    'iiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848PW-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkHR3s'
)


async def test_existing_session(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.get(
        'autogen/driver',
        headers={'X-Driver-Session': 'driver_session1'},
        params={'park_id': 'driver_db_id1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }


async def test_bad_session(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.get(
        'autogen/driver',
        headers={'X-Driver-Session': 'bad session'},
        params={'park_id': 'driver_db_id1'},
    )
    assert response.status_code == 401
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_other_client_id(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_client_session(
        'uberdriver', 'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.get(
        'autogen/driver',
        headers={
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter-uber 9.05 (1234)',
        },
        params={'park_id': 'driver_db_id1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }


async def test_unauthorized_client_id(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_client_session(
        'taximeter', 'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.get(
        'autogen/driver',
        headers={
            'X-Driver-Session': 'driver_session1',
            'User-Agent': 'Taximeter-uber 9.05 (1234)',
        },
        params={'park_id': 'driver_db_id1'},
    )
    assert response.status_code == 401
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_legacy_park_id(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.post(
        'autogen/driver',
        params={'park_id': 'driver_db_id1', 'session': 'driver_session1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }


async def test_legacy_db(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.post(
        'autogen/driver',
        params={'db': 'driver_db_id1', 'session': 'driver_session1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }


async def test_legacy_bad_session(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.post(
        'autogen/driver',
        params={'park_id': 'driver_db_id1', 'session': 'bad_session'},
    )
    assert response.status_code == 401
    assert response.headers['Content-Type'] == DEFAULT_ERROR_CONTENT_TYPE


async def test_legacy_other_client_id(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_client_session(
        'uberdriver', 'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.post(
        'autogen/driver',
        headers={'User-Agent': 'Taximeter-Uber 9.1 (1234) ios'},
        params={'park_id': 'driver_db_id1', 'session': 'driver_session1'},
    )
    assert response.status_code == 200


async def test_legacy_new_params(taxi_userver_sample, driver_authorizer):
    driver_authorizer.set_session(
        'driver_db_id1', 'driver_session1', 'driver_uuid1',
    )
    response = await taxi_userver_sample.post(
        'autogen/driver',
        headers={'X-Driver-Session': 'driver_session1'},
        params={'park_id': 'driver_db_id1'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'mock', 'dst': 'userver-sample'}],
    TVM_SERVICES={'userver-sample': 2001716, 'mock': 111},
)
@pytest.mark.tvm2_ticket({111: MOCK_SERVICE_TICKET})
async def test_legacy_with_api_v1(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/driver',
        headers={
            'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': 'driver_uuid1',
            'X-Request-Application-Version': '1.2 (3)',
            'X-Request-Version-Type': 'vezet',
            'X-Request-Platform': 'ios',
            'X-Request-Application': 'vezet',
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'park-id': 'driver_db_id1',
        'driver-profile-id': 'driver_uuid1',
    }
