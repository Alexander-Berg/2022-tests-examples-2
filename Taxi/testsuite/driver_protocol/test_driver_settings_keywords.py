import pytest


def test_check_session(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('777', 'test_session', 'test_driver')

    response = taxi_driver_protocol.get('driver/settings/keywords')
    assert response.status_code == 401

    response = taxi_driver_protocol.get('driver/settings/keywords?db=777')
    assert response.status_code == 401

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=unknown_session',
    )
    assert response.status_code == 401

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=test_session',
    )
    assert response.status_code == 200


@pytest.mark.config(
    TAXIMETER_SOFTWARE_KEYWORDS={
        'allowed': ['test0', 'test1'],
        'forbidden': ['test2', 'test3', 'test4'],
    },
)
def test_standard_config(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('777', 'test_session', 'test_driver')

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=test_session',
    )
    assert response.status_code == 200

    data = response.json()

    expected_data = {
        'keywords': ['test2', 'test3', 'test4'],
        'permitted': ['test0', 'test1'],
    }

    assert data == expected_data


@pytest.mark.config(
    TAXIMETER_SOFTWARE_KEYWORDS={
        'allowed': ['test0', 'test1'],
        'forbidden': [],
    },
)
def test_config_with_one_empty_value(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'test_session', 'test_driver')

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=test_session',
    )
    assert response.status_code == 200

    data = response.json()

    expected_data = {'keywords': [], 'permitted': ['test0', 'test1']}

    assert data == expected_data


@pytest.mark.config(
    TAXIMETER_SOFTWARE_KEYWORDS={'forbidden': ['test2', 'test3', 'test4']},
)
def test_config_without_one_entry(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'test_session', 'test_driver')

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=test_session',
    )
    assert response.status_code == 200

    data = response.json()

    expected_data = {'keywords': ['test2', 'test3', 'test4'], 'permitted': []}

    assert data == expected_data


@pytest.mark.config(
    TAXIMETER_SOFTWARE_KEYWORDS={'allowed': [], 'forbidden': []},
)
def test_config_with_empty_values(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'test_session', 'test_driver')

    response = taxi_driver_protocol.get(
        'driver/settings/keywords?db=777&session=test_session',
    )
    assert response.status_code == 200

    data = response.json()

    expected_data = {'keywords': [], 'permitted': []}

    assert data == expected_data
