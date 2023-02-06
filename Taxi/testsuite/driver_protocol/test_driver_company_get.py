# coding=utf-8
import pytest


def test_driver_company_get_description(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'test_session', 'test_uuid')

    response = taxi_driver_protocol.get(
        'driver/company/get',
        params=dict({'db': '1488', 'session': 'test_session'}),
    )

    assert response.status_code == 200
    assert response.json() == {'contact': 'Moscow_1488'}


def test_driver_company_get_no_description(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('777', 'test_session', 'test_uuid')

    response = taxi_driver_protocol.get(
        'driver/company/get',
        params=dict({'db': '777', 'session': 'test_session'}),
    )

    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_CONTACTS={
        'countries': {'rus': 'RUS contacts'},
        'cities': {'Москва': 'Moscow contacts'},
    },
)
def test_driver_company_get_self_employed_fns_city(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1369', 'test_session', 'test_uuid')

    response = taxi_driver_protocol.get(
        'driver/company/get',
        params=dict({'db': '1369', 'session': 'test_session'}),
    )

    assert response.status_code == 200
    assert response.json() == {'contact': 'Moscow contacts'}


@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_CONTACTS={
        'countries': {'rus': 'RUS contacts'},
        'cities': {'Санкт-Петербург': 'Spb contacts'},
    },
)
def test_driver_company_get_self_employed_fns_country(
        taxi_driver_protocol, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1369', 'test_session', 'test_uuid')

    response = taxi_driver_protocol.get(
        'driver/company/get',
        params=dict({'db': '1369', 'session': 'test_session'}),
    )

    assert response.status_code == 200
    assert response.json() == {'contact': 'RUS contacts'}
