async def test_sum2pay(load_json, calc_sum2pay):
    events = load_json('flow_taxi_park_events.json')
    sum2pay = await calc_sum2pay(events)
    assert sum2pay == load_json('expected_sum2pay.json')


async def test_s2p_taxi_billing_event(load_json, calc_sum2pay):
    events = load_json('flow_taxi_park_events.json')
    extended_order_context = load_json('order_context.json')
    for event in events:
        payload = event['payload']
        if payload['kind'] == 'waybill_billing_context':
            payload['data']['has_using_cargo_pipelines_feature'] = True
        elif payload['kind'] == 'taxi_order_context':
            payload['data'] = extended_order_context
    sum2pay = await calc_sum2pay(events)
    expected_data = load_json('flow_taxi_park/s2p_batch_order_event.json')
    assert sum2pay['taxi_park']['batch_order_event'] == expected_data
