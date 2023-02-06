from unittest import mock

import freezegun
import pytest
from sqlalchemy.exc import IntegrityError

from taxi.robowarehouse.lib.concepts import device_messages
from taxi.robowarehouse.lib.concepts import devices
from taxi.robowarehouse.lib.concepts import solomon
from taxi.robowarehouse.lib.concepts import celery
from taxi.robowarehouse.lib.concepts.adapters import tuya
from taxi.robowarehouse.lib.concepts.adapters.types import AdapterType
from taxi.robowarehouse.lib.misc import datetime_utils
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


@pytest.fixture(scope='function', name='solomon_send_coroutine_check')
def solomon_send_coroutine_mock_and_assert_called():
    with mock.patch.object(solomon.client.SolomonClient, '_send_coroutine') as mock_send_coroutine:
        mock_send_coroutine.return_value = None
        yield
        mock_send_coroutine.assert_called()


@pytest.mark.asyncio
async def test_get_all_empty():
    result = await device_messages.get_all()

    assert result == []


@pytest.mark.asyncio
async def test_get_all():
    message1 = await device_messages.factories.create()
    message2 = await device_messages.factories.create()

    result = await device_messages.get_all()

    assert_items_equal([r.to_response() for r in result], [message1.to_response(), message2.to_response()])


@pytest.mark.asyncio
async def test_get_by_message_id_not_exist():
    await device_messages.factories.create()

    result = await device_messages.get_by_message_id(generate_id())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_message_id():
    message = await device_messages.factories.create()
    await device_messages.factories.create()

    result = await device_messages.get_by_message_id(message.message_id)

    assert result.to_response() == message.to_response()


@pytest.mark.asyncio
async def test_get_by_source_message_id_not_exist():
    await device_messages.factories.create()

    result = await device_messages.get_by_source_message_id(source=AdapterType.TUYA, source_message_id=generate_id())

    assert result is None


@pytest.mark.asyncio
async def test_get_by_source_message_id():
    message = await device_messages.factories.create()
    await device_messages.factories.create()

    result = await device_messages.get_by_source_message_id(
        source=message.source,
        source_message_id=message.source_message_id,
    )

    assert result.to_response() == message.to_response()


@pytest.mark.asyncio
async def test_create():
    message1 = device_messages.factories.build()
    message2 = await device_messages.factories.create()

    result = await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1))

    assert result.to_response() == message1.to_response()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), message2.to_response()])


@pytest.mark.asyncio
async def test_create_duplicate():
    message1 = await device_messages.factories.create()
    message2 = await device_messages.factories.create()

    with pytest.raises(IntegrityError) as e:
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1))

    assert 'duplicate key value violates unique constraint' in str(e.value)

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), message2.to_response()])


@freezegun.freeze_time('1970-01-01 00:00:05', tz_offset=0)
@mock.patch.object(celery.tasks.device_messages_tasks.check_open_legality, 'delay')
@pytest.mark.asyncio
async def test_process_tuya_message_already_exists(check_open_mock):
    check_open_mock.return_value = None
    message1 = await device_messages.factories.create()
    message2 = await device_messages.factories.create()
    device = await devices.factories.create()

    tuya_message = tuya.Message(
        message_id=message1.source_message_id,
        time=datetime_utils.timestamp_to_datetime(1),
        payload={'p': 1},
        data={'devId': device.source_device_id},
    )

    result = await device_messages.process_tuya_message(tuya_message)

    assert result.to_response() == message1.to_response()

    db_messages = await device_messages.get_all()
    check_open_mock.assert_not_called()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), message2.to_response()])


@freezegun.freeze_time('1970-01-01 00:00:05', tz_offset=0)
@mock.patch.object(celery.tasks.device_messages_tasks.check_open_legality, 'delay')
@pytest.mark.asyncio
async def test_process_tuya_message_device_not_exists(check_open_mock, solomon_send_coroutine_check):
    check_open_mock.return_value = None
    message1 = await device_messages.factories.create()
    await devices.factories.create()

    tuya_message = tuya.Message(
        message_id='id123',
        time=datetime_utils.timestamp_to_datetime(1),
        payload={'p': 1},
        data={'devId': '1'},
    )

    result = await device_messages.process_tuya_message(tuya_message)

    expected = device_messages.factories.build(
        message_id=result.message_id,
        device_id='',
        published_at=datetime_utils.timestamp_to_datetime(1),
        source=AdapterType.TUYA,
        source_message_id='id123',
        received_at=datetime_utils.timestamp_to_datetime(5),
        payload={'p': 1},
        data={'devId': '1'},
    )

    db_messages = await device_messages.get_all()
    check_open_mock.assert_not_called()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), expected.to_response()])


@freezegun.freeze_time('1970-01-01 00:00:05', tz_offset=0)
@mock.patch.object(celery.tasks.device_messages_tasks.check_open_legality, 'delay')
@pytest.mark.asyncio
async def test_process_tuya_message_no_device_id(check_open_mock, solomon_send_coroutine_check):
    check_open_mock.return_value = None
    message1 = await device_messages.factories.create()
    tuya_message = tuya.Message(
        message_id='id123',
        time=datetime_utils.timestamp_to_datetime(1),
        payload={'p': 1},
        data={'a': 1},
    )

    result = await device_messages.process_tuya_message(tuya_message)

    expected = device_messages.factories.build(
        message_id=result.message_id,
        device_id='',
        published_at=datetime_utils.timestamp_to_datetime(1),
        source=AdapterType.TUYA,
        source_message_id='id123',
        received_at=datetime_utils.timestamp_to_datetime(5),
        payload={'p': 1},
        data={'a': 1},
    )

    db_messages = await device_messages.get_all()
    check_open_mock.assert_not_called()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), expected.to_response()])


@freezegun.freeze_time('1970-01-01 00:00:05', tz_offset=0)
@mock.patch.object(celery.tasks.device_messages_tasks.check_open_legality, 'delay')
@pytest.mark.asyncio
async def test_process_tuya_messages(check_open_mock, solomon_send_coroutine_check):
    check_open_mock.return_value = None
    message1 = await device_messages.factories.create()
    device = await devices.factories.create()
    await devices.factories.create()

    tuya_message = tuya.Message(
        message_id='id123',
        time=datetime_utils.timestamp_to_datetime(1),
        payload={'p': 1},
        data={'devId': device.source_device_id},
    )

    result = await device_messages.process_tuya_message(tuya_message)

    expected = device_messages.factories.build(
        message_id=result.message_id,
        device_id=device.device_id,
        published_at=datetime_utils.timestamp_to_datetime(1),
        source=AdapterType.TUYA,
        source_message_id='id123',
        received_at=datetime_utils.timestamp_to_datetime(5),
        payload={'p': 1},
        data={'devId': device.source_device_id},
    )

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), expected.to_response()])
    check_open_mock.assert_not_called()


@freezegun.freeze_time('1970-01-01 00:00:05', tz_offset=0)
@mock.patch.object(celery.tasks.device_messages_tasks.check_open_legality, 'delay')
@pytest.mark.asyncio
async def test_process_tuya_messages_with_unlock_remote(check_open_mock, solomon_send_coroutine_check):
    check_open_mock.return_value = None
    await device_messages.factories.create()
    device = await devices.factories.create()
    await devices.factories.create()

    tuya_message = tuya.Message(
        message_id='id123',
        time=datetime_utils.timestamp_to_datetime(1),
        payload={'p': 1},
        data={'devId': device.source_device_id, 'status': [{'code': 'unlock_remote', 'value': 999}]},
    )

    await device_messages.process_tuya_message(tuya_message)

    check_open_mock.assert_called_once_with(device_id=device.device_id, timestamp=1)
