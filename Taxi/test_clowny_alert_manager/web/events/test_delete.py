from test_clowny_alert_manager.helpers import extractors


async def test_handler(get_service, delete_event):
    service = await get_service(1)
    events = list(extractors.Services([service]).events)
    assert len(events) == 2

    await delete_event(1)

    service = await get_service(1)
    events = list(extractors.Services([service]).events)
    assert len(events) == 1
