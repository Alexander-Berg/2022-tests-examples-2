import operator

import pytest


def test_strings(taxi_driver_protocol, mockserver, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/strings?db=1488&session=qwerty&version=1',
        headers={'Accept-Language': 'ru', 'User-Agent': 'Taximeter 9.88'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['is_key_set_full']
    assert data['version'] == 'a5036d64f8a6daadf4dfe16aa6e4968a'
    assert len(data['updated_strings']) == 2
    data['updated_strings'].sort(key=operator.itemgetter('name'))
    assert data['updated_strings'][0]['name'] == 'head_on_to_taxi_center_hint'
    assert (
        data['updated_strings'][0]['value']
        == 'Приезжайте в Центр Яндекс.Такси'
    )
    assert data['updated_strings'][1]['name'] == 'video_childseat_setup'
    assert (
        data['updated_strings'][1]['value']
        == 'www.youtube.com/watch?v=jHst7krrDdo'
    )


def test_strings_last_version(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/strings?db=1488&session=qwerty&'
        'version=a5036d64f8a6daadf4dfe16aa6e4968a',
        headers={'Accept-Language': 'ru', 'User-Agent': 'Taximeter 9.88'},
    )
    assert response.status_code == 200
    data = response.json()
    assert 'is_key_set_full' not in data
    assert 'updated_strings' not in data
    assert data['version'] == 'a5036d64f8a6daadf4dfe16aa6e4968a'


def test_strings_gzip(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/strings?db=1488&session=qwerty&version=1',
        headers={
            'Accept-Language': 'ru',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Taximeter 9.88',
        },
    )
    assert response.status_code == 200
    assert response.headers['Content-Encoding'] == 'gzip'


@pytest.mark.config(
    LOCALES_APPLICATION_TYPE_OVERRIDES={
        'aze': {
            'override_keysets': {
                'taximeter_driver_messages': 'taximeter_driver_messages_az',
            },
        },
    },
)
def test_strings_az(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('888', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/strings?db=888&session=qwerty',
        headers={'Accept-Language': 'ru', 'User-Agent': 'Taximeter-az 9.88'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['is_key_set_full']
    assert data['version'] == '17c75c41ddb26278a8ed1e06e3076b3e'
    assert len(data['updated_strings']) == 2
    data['updated_strings'].sort(key=operator.itemgetter('name'))
    assert data['updated_strings'][0]['name'] == 'head_on_to_taxi_center_hint'
    assert data['updated_strings'][0]['value'] == 'Приезжайте в Центр Uber'
    assert data['updated_strings'][1]['name'] == 'video_childseat_setup'
    assert (
        data['updated_strings'][1]['value']
        == 'www.youtube.com/watch?v=jHst7krrDdo'
    )


@pytest.mark.config(USE_ALL_FALLBACKS_FOR_DRIVERSTRINGS=True)
@pytest.mark.filldb(localization_taximeter_driver_messages='cascade')
def test_string_fallback_locales_cascade(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('888', 'qwerty', 'driver')

    response = taxi_driver_protocol.get(
        'driver/strings?db=888&session=qwerty',
        headers={'Accept-Language': 'az', 'User-Agent': 'Taximeter-az 9.88'},
    )

    data = response.json()
    assert response.status_code == 200
    for item in data['updated_strings']:
        if item['name'] == 'key_fallback_cascade_1':
            assert item['value'] == 'fallback_cascade_1_lv'
        elif item['name'] == 'key_fallback_cascade_2':
            assert item['value'] == 'fallback_cascade_2_lt'
        elif item['name'] == 'key_fallback_cascade_3':
            assert item['value'] == 'fallback_cascade_3'
        else:
            # driver/strings doesn't response keys that are empty
            # it allows a taximeter use thier version of a translation
            # so, the key 'key_fallback_cascade_4' mustn't be here
            assert False
