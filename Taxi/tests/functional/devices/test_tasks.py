import datetime
from unittest import mock

import pytest
import freezegun

from taxi.robowarehouse.lib.clients import http
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import solomon
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.concepts.adapters import tuya
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(tuya.TuyaApiClient, 'get_device_status')
@mock.patch.object(tuya.TuyaApiClient, 'get_device')
@pytest.mark.asyncio
async def test_device_status_to_solomon(get_device_mock, get_status_mock, solomon_client):
    device1: devices.Device = await devices.factories.create(name=r'name|1*2?3"4\5')
    device2: devices.Device = await devices.factories.create()
    await devices.factories.create(state=devices.types.DeviceState.INACTIVE)

    ts = datetime_utils.get_now_timestamp()

    fake_kwargs = {
        'id': generate_id(), 'name': '1', 'asset_id': 'str', 'category': 'str', 'category_name': 'str',
        'gateway_id': 'gateway_id', 'product_id': 'str', 'product_name': 'str', 'sub': True, 'icon': 'str',
        'ip': 'str', 'lat': 'str', 'lon': 'str', 'local_key': 'str', 'model': 'str', 'time_zone': 'str',
        'uuid': 'str', 'create_time': datetime.datetime.now(), 'active_time': datetime.datetime.now(),
        'update_time': datetime.datetime.now()
    }

    expected_device = {
        device1.source_device_id: tuya.models.Device(online=True, **fake_kwargs),
        device2.source_device_id: tuya.models.Device(online=False, **fake_kwargs),
        'gateway_id': tuya.models.Device(online=True, **fake_kwargs),
    }

    expected_status = {
        device1.source_device_id: [tuya.models.DeviceStatus(code='residual_electricity', value=60)],
        device2.source_device_id: [tuya.models.DeviceStatus(code='residual_electricity', value=40)],
    }
    get_device_mock.side_effect = lambda device_id: expected_device.get(device_id)
    get_status_mock.side_effect = lambda device_id: expected_status.get(device_id)

    await devices.tasks.device_status_to_solomon()

    expected_metrics = [
        {
            'labels': {
                'sensor': 'status',
                'device_id': device1.source_device_id,
                'type': 'online',
                'name': 'name 1 2 3 4 5'
            },
            'value': 1,
            'ts': ts,
        },
        {
            'labels': {
                'sensor': 'status',
                'device_id': device1.source_device_id,
                'type': 'residual_electricity',
                'name': 'name 1 2 3 4 5'
            },
            'value': 60,
            'ts': ts,
        },
        {
            'labels': {
                'sensor': 'status',
                'device_id': device2.source_device_id,
                'type': 'online',
                'name': device2.name
            },
            'value': 0,
            'ts': ts,
        },
    ]

    assert len(solomon_client.sensors[solomon.types.Service.DEVICES]) == 3

    assert_items_equal(solomon_client.sensors[solomon.types.Service.DEVICES], expected_metrics)

    await solomon_client._clear_sensors()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(tuya.TuyaApiClient, 'get_device_status')
@mock.patch.object(tuya.TuyaApiClient, 'get_device')
@mock.patch.object(solomon.client.SolomonClient, 'send')
@pytest.mark.asyncio
async def test_device_status_to_solomon_gateway_offline(solomon_send_mock, get_device_mock, get_status_mock):
    ts = datetime_utils.get_now_timestamp()

    device: devices.Device = await devices.factories.create()

    fake_kwargs = {
        'id': generate_id(), 'name': '1', 'asset_id': 'str', 'category': 'str', 'category_name': 'str',
        'gateway_id': 'gateway_id', 'product_id': 'str', 'product_name': 'str', 'sub': True, 'icon': 'str',
        'ip': 'str', 'lat': 'str', 'lon': 'str', 'local_key': 'str', 'model': 'str', 'time_zone': 'str',
        'uuid': 'str', 'create_time': datetime.datetime.now(), 'active_time': datetime.datetime.now(),
        'update_time': datetime.datetime.now()
    }

    expected_device = {
        device.source_device_id: tuya.models.Device(online=True, **fake_kwargs),
        'gateway_id': tuya.models.Device(online=False, **fake_kwargs),
    }

    expected_status = {
        device.source_device_id: [tuya.models.DeviceStatus(code='residual_electricity', value=60)],
    }
    solomon_send_mock.return_value = None
    get_device_mock.side_effect = lambda device_id: expected_device.get(device_id)
    get_status_mock.side_effect = lambda device_id: expected_status.get(device_id)

    await devices.tasks.device_status_to_solomon()

    expected_metrics = [
        {
            'labels': {
                'sensor': 'status',
                'device_id': device.source_device_id,
                'type': 'online',
                'name': device.name
            },
            'value': 0,
            'ts': ts,
        }
    ]

    solomon_client = await solomon.get_solomon_client()

    assert len(solomon_client.sensors[solomon.types.Service.DEVICES]) == 1

    assert_items_equal(solomon_client.sensors[solomon.types.Service.DEVICES], expected_metrics)

    await solomon_client._clear_sensors()


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(http.AsyncHttpClient, 'get')
@pytest.mark.asyncio
async def test_monitoring_external_api_success_way(get_mock, solomon_client):
    ts = datetime_utils.get_now_timestamp()

    fake_kwargs = {
        'id': generate_id(), 'name': '1', 'asset_id': 'str', 'category': 'str', 'category_name': 'str',
        'gateway_id': 'gateway_id', 'product_id': 'str', 'product_name': 'str', 'sub': True, 'icon': 'str',
        'ip': 'str', 'lat': 'str', 'lon': 'str', 'local_key': 'str', 'model': 'str', 'time_zone': 'str',
        'uuid': 'str', 'create_time': datetime.datetime.now(), 'active_time': datetime.datetime.now(),
        'update_time': datetime.datetime.now(), 'online': True
    }

    get_mock.return_value = {'success': True, 'result': fake_kwargs}
    tuya_client = await tuya.TuyaApiClient.instance(configuration=dict(endpoint='http://test'))
    await tuya_client.get_device('12345')

    expected_metrics = [
        {
            'labels': {
                'sensor': 'external_api_state',
                'method': 'get_device',
                'client': 'TuyaApiClient',
                'success': True,
            },
            'value': 0.0,
            'ts': ts
        }
    ]

    assert_items_equal(solomon_client.sensors[solomon.types.Service.API], expected_metrics)


@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@mock.patch.object(http.AsyncHttpClient, 'get')
@pytest.mark.asyncio
async def test_monitoring_external_api_error(get_mock, solomon_client):
    def exc_(*args, **kwargs):
        raise Exception('test')

    ts = datetime_utils.get_now_timestamp()

    get_mock.side_effect = exc_
    tuya_client = await tuya.TuyaApiClient.instance(configuration=dict(endpoint='http://test'))
    with pytest.raises(Exception):
        await tuya_client.get_device('12345')

    expected = {
        'alerts': [{
            'labels': {
                'sensor': 'external_api_errors',
                'client': 'TuyaApiClient',
                'method': 'get_device',
                'message': 'Exception( test )'
            },
            'value': 0.0,
            'ts': ts
        }],
        'api': [{
            'labels': {
                'sensor': 'external_api_state',
                'method': 'get_device',
                'client': 'TuyaApiClient',
                'success': False
            },
            'value': 0.0,
            'ts': ts
        }]
    }
    assert_items_equal(solomon_client.sensors[solomon.types.Service.API], expected['api'])
    assert_items_equal(solomon_client.sensors[solomon.types.Service.ALERTS], expected['alerts'])
