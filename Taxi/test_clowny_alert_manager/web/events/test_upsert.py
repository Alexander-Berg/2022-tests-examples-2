from test_clowny_alert_manager.helpers import extractors


async def test_handler(get_service, upsert_event):
    service = await get_service(1)
    event = list(extractors.Services([service]).events)[0]

    assert event['settings']['ignore_nodata']
    assert 'escalation_method' not in event['settings']
    event['settings']['ignore_nodata'] = False
    event['settings']['escalation_method'] = 'phone_escalation'

    await upsert_event(event)

    service = await get_service(1)
    event = list(extractors.Services([service]).events)[0]

    assert not event['settings']['ignore_nodata']
    assert event['settings']['escalation_method'] == 'phone_escalation'
