# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from geobus_tools import geobus  # noqa: F401 C5521
from geopipeline_tools.geopipeline import (  # noqa: F401 C5521
    geopipeline_config,  # noqa: F401 C5521
)  # noqa: F401 C5521
import pytest

from internal_trackstory_plugins import *  # noqa: F403 F401


def format_universal_signal_track(track, source, driver):
    result = []
    for position in track:
        point = {
            'contractor_id': driver,
            'client_timestamp': position['timestamp'] * 1000 * 1000,
            'source': source,
            'signals': [
                {
                    'geo_position': {
                        'position': {
                            'lon': position['lon'],
                            'lat': position['lat'],
                        },
                    },
                },
            ],
        }
        for additional_field in ['direction', 'altitude', 'speed', 'accuracy']:
            if additional_field in position:
                point['signals'][0]['geo_position'][
                    additional_field
                ] = position[additional_field]

        result += [point]

    return {'payload': result}


def format_signalv2_track(track, source, driver):
    result = []
    for position in track:
        point = {
            'driver_id': driver,
            'position': [position['lon'], position['lat']],
            'unix_time': position['timestamp'] * 1000,
            'source': source,
            'speed': position['speed'],
        }

        if 'direction' in position:
            point['direction'] = position['direction']

        result += [point]

    return result


def format_position_track(track, driver):
    result = []
    for position in track:
        result += [
            {
                'driver_id': driver,
                'position': [position['lon'], position['lat']],
                'timestamp': position['timestamp'],
                'speed': position['speed'],
                'direction': position['direction'],
                'accuracy': position['accuracy'],
            },
        ]
    return result


# pylint: disable=redefined-outer-name
@pytest.fixture
async def taxi_internal_trackstory_adv(
        taxi_internal_trackstory, geopipeline_config,  # noqa: F811
):

    return await geopipeline_config(taxi_internal_trackstory)


@pytest.fixture
async def shorttrack_payload_sender(testpoint, now, redis_store):
    @testpoint('internal-trackstory-shorttrack-payload-processed')
    def payload_processed(data):
        return

    class PayloadSender:
        def __init__(self) -> None:
            pass

        async def send_signalv2_payload(self, track, source, driver, channel):
            message_data = format_signalv2_track(track, source, driver)
            message = geobus.serialize_signal_v2(message_data, now)
            redis_store.publish(channel, message)
            await payload_processed.wait_call()

        async def send_positions_payload(self, track, driver, channel):
            message_data = format_position_track(track, driver)
            message = geobus.serialize_positions_v2(message_data, now)
            redis_store.publish(channel, message)
            await payload_processed.wait_call()

        async def send_universal_signals_payload(
                self, track, source, driver, channel,
        ):
            message_data = format_universal_signal_track(track, source, driver)
            message = geobus.serialize_universal_signal(message_data, now)
            redis_store.publish(channel, message)
            await payload_processed.wait_call()

    return PayloadSender()
