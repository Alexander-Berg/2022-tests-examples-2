async def test_sum2pay(load_json, calc_sum2pay):
    events = load_json('flow_ndd_corp_client_events.json')
    sum2pay = await calc_sum2pay(events)
    assert sum2pay == load_json('expected_sum2pay.json')
