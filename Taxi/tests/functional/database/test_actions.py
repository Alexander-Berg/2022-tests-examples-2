import pytest

from taxi.robowarehouse.lib.concepts import database
from taxi.robowarehouse.lib.concepts import device_messages
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal


class SomeError(Exception):
    pass


@pytest.mark.asyncio
async def test_db_session_error():
    async def _run():
        async with database.db_session() as session:
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=session)
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=session)
            raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    assert await device_messages.get_all() == []


@pytest.mark.asyncio
async def test_db_session_error_after_commit():
    async def _run():
        async with database.db_session() as session:
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=session)
            await session.commit()
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=session)
            raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response()])


@pytest.mark.asyncio
async def test_db_session_different_session():
    async def _run():
        async with database.db_session() as session:
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=session)
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2))
            raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message2.to_response()])


@pytest.mark.asyncio
async def test_db_session():
    async def _run():
        async with database.db_session() as session:
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=session)
            await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=session)

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), message2.to_response()])


@pytest.mark.asyncio
async def test_with_db_session_error():
    @database.with_db_session
    async def _run(db):
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=db)
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=db)
        raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    assert await device_messages.get_all() == []


@pytest.mark.asyncio
async def test_with_db_session_error_after_commit():
    @database.with_db_session
    async def _run(db):
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=db)
        await db.commit()
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=db)
        raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response()])


@pytest.mark.asyncio
async def test_with_db_session_different_session():
    @database.with_db_session
    async def _run(db):
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=db)
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2))
        raise SomeError('Fail')

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    with pytest.raises(SomeError):
        await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message2.to_response()])


@pytest.mark.asyncio
async def test_with_db_session():
    @database.with_db_session
    async def _run(db):
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message1), db=db)
        await device_messages.create(device_messages.CreateDeviceMessageRequest.from_orm(message2), db=db)

    message1 = device_messages.factories.build()
    message2 = device_messages.factories.build()

    await _run()

    db_messages = await device_messages.get_all()
    assert_items_equal([m.to_response() for m in db_messages], [message1.to_response(), message2.to_response()])
