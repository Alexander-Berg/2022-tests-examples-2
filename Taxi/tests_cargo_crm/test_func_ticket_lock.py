from tests_cargo_crm import const


async def test_acquiring_idempotency(acquire_ticket_lock):
    for dummy_i in range(2):
        result = await acquire_ticket_lock(const.UID, const.TICKET_ID)
        assert result == {'is_successful': True, 'ticket_id': const.TICKET_ID}


async def test_race(acquire_ticket_lock, find_ticket_lock):
    first = await acquire_ticket_lock(const.UID, const.TICKET_ID)
    assert first['is_successful']

    second = await acquire_ticket_lock(const.UID, const.ANOTHER_TICKET_ID)
    assert not second['is_successful']
    assert second['ticket_id'] == const.TICKET_ID  # ticket locked on


async def test_successful_search(acquire_ticket_lock, find_ticket_lock):
    await acquire_ticket_lock(const.UID, const.TICKET_ID)

    result = await find_ticket_lock(const.UID)
    assert result['ticket_id'] == const.TICKET_ID


async def test_found_nothing(find_ticket_lock):
    result = await find_ticket_lock(const.UID)
    assert 'ticket_id' not in result


async def test_release(
        acquire_ticket_lock, find_ticket_lock, release_ticket_lock,
):
    await acquire_ticket_lock(const.UID, const.TICKET_ID)
    assert (await find_ticket_lock(const.UID))['ticket_id'] == const.TICKET_ID

    await release_ticket_lock(const.TICKET_ID)
    assert 'ticket_id' not in await find_ticket_lock(const.UID)


async def test_release_successful_even_on_for_nonexistent(release_ticket_lock):
    result = await release_ticket_lock(const.TICKET_ID)
    assert result == {}
