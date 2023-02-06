import pytest


def test_no_request_data(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.post('service/chat/channels')
    assert response.status_code == 200
    assert response.json() == load_json('DefaultResponse.json')


@pytest.mark.redis_store(['set', 'DriverSession:1488:qwerty', 'driver'])
def test_driver_channels(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.post(
        'service/chat/channels?db=1488&yandex=True',
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('AllChannels.json')


@pytest.mark.redis_store(['set', 'DriverSession:1488:qwerty', 'driver'])
def test_driver_channels_no_yandex(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.post(
        'service/chat/channels?db=1488', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('NoYandexChannels.json')


@pytest.mark.config(
    CHAT_SHOW_CHANNELS_BY_COUNTRY={
        '__default__': {'__default__': True},
        'Россия': {
            '__default__': True,
            'Sos': False,
            'Support': False,
            'Park': False,
        },
    },
)
@pytest.mark.redis_store(['set', 'DriverSession:1488:qwerty', 'driver'])
def test_driver_channels_hidden_channels(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.post(
        'service/chat/channels?db=1488', headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('NoYandexChannelsHiddenChannels.json')
