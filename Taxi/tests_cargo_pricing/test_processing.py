from tests_cargo_pricing import utils


def get_default_processing_events():
    return [
        {'kind': 'create'},
        {
            'kind': 'calculation',
            'calc_id': 'cargo-pricing/v1/4005d50f-d838-4ea5-9fd6-404af4d43c71',
            'price_for': 'client',
            'origin_uri': 'some/origin/uri',
            'calc_kind': 'offer',
        },
    ]


def assert_processing_event_request(event_req, calc_req, calc_id):
    expected = {
        'kind': 'calculation',
        'calc_id': calc_id,
        'price_for': calc_req['price_for'],
        'origin_uri': calc_req['origin_uri'],
        'clients': calc_req['clients'],
        'calc_kind': calc_req['calc_kind'],
        'resolution_info': calc_req['resolution_info'],
    }
    if 'performer' in calc_req:
        expected['performer'] = calc_req['performer']
    assert event_req.json == expected
    assert event_req.query['item_id'] == calc_req['entity_id']
    assert event_req.headers['X-Idempotency-Token'] == f'{calc_id}'


async def test_create_event(
        mock_put_processing_event,
        v1_add_processing_event,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    claim_id = 'some_claim_id'
    events = get_default_processing_events()
    events.pop()
    resp = await v1_add_processing_event(claim_id, events)
    assert mock_put_processing_event.mock.times_called == 1
    assert resp.status_code == 200
    assert resp.json() == {}
    assert mock_put_processing_event.requests[0].json == events[0]
    assert mock_put_processing_event.requests[0].query['item_id'] == claim_id
    assert (
        mock_put_processing_event.requests[0].headers['X-Idempotency-Token']
        == claim_id
    )


async def test_multiple_events(
        mock_put_processing_event,
        v1_add_processing_event,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    claim_id = 'some_claim_id'
    events = get_default_processing_events()
    resp = await v1_add_processing_event(claim_id, events)
    assert mock_put_processing_event.mock.times_called == 2
    assert resp.status_code == 200
    assert resp.json() == {}
    assert mock_put_processing_event.requests[0].json == events[0]
    assert mock_put_processing_event.requests[0].query['item_id'] == claim_id
    assert mock_put_processing_event.requests[1].json == events[1]
    assert mock_put_processing_event.requests[1].query['item_id'] == claim_id


async def test_entity_id_saving(
        v1_calc_creator,
        v1_add_processing_event,
        v2_retrieve_calc,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    del v1_calc_creator.payload['entity_id']
    del v1_calc_creator.payload['origin_uri']
    calc_resp = await v1_calc_creator.execute()
    assert calc_resp.status_code == 200
    calc_id = calc_resp.json()['calc_id']
    claim_id = utils.get_default_calc_request()['waypoints'][0]['claim_id']
    events = get_default_processing_events()
    events[1]['calc_id'] = calc_id
    processing_resp = await v1_add_processing_event(claim_id, events)
    assert processing_resp.status_code == 200
    retrieve_resp = await v2_retrieve_calc(calc_ids=[calc_id])
    assert retrieve_resp.status_code == 200
    assert mock_get_processing_events.mock.times_called == 1
    assert mock_get_processing_events.requests[0].query['item_id'] == claim_id


async def test_create_event_400(
        mock_put_processing_event,
        v1_add_processing_event,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    claim_id = 'some_claim_id'
    events = get_default_processing_events()
    mock_put_processing_event.status_code = 400
    mock_put_processing_event.response = {
        'code': 'no_such_item',
        'message': 'Item "some_claim_id" not exists',
    }
    resp = await v1_add_processing_event(claim_id, events)
    assert mock_put_processing_event.mock.times_called == 1
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'processing_error',
        'message': mock_put_processing_event.response['message'],
    }


async def test_add_event_on_v1_calc(
        v1_calc_creator,
        mock_put_processing_event,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    calc_id = response.json()['calc_id']
    assert mock_put_processing_event.mock.times_called == 1
    default_calc_request = utils.get_default_calc_request()
    assert_processing_event_request(
        mock_put_processing_event.requests[0], default_calc_request, calc_id,
    )


async def test_add_event_on_calc_with_create_event(
        v1_calc_creator,
        mock_put_processing_event,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    v1_calc_creator.payload['make_processing_create_event'] = True
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    calc_id = response.json()['calc_id']
    assert mock_put_processing_event.mock.times_called == 2
    default_calc_request = utils.get_default_calc_request()
    assert mock_put_processing_event.requests[0].json == {'kind': 'create'}
    assert (
        mock_put_processing_event.requests[0].query['item_id']
        == default_calc_request['entity_id']
    )
    assert (
        mock_put_processing_event.requests[0].headers['X-Idempotency-Token']
        == default_calc_request['entity_id']
    )
    assert_processing_event_request(
        mock_put_processing_event.requests[1], default_calc_request, calc_id,
    )


async def test_add_events_on_bulk_calc(
        v2_calc_creator,
        mock_put_processing_event,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    second_calc_req = utils.add_category_to_request(v2_calc_creator)
    second_calc_req['price_for'] = 'performer'
    second_calc_req['origin_uri'] = '/some/other/origin/uri'
    second_calc_req['entity_id'] = 'claim2'
    second_calc_req['performer'] = {
        'driver_id': 'uuid0',
        'park_db_id': 'dbid0',
    }
    second_calc_req['calc_kind'] = 'final'
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    assert len(response.json()['calculations']) == 2
    calc_ids = [calc['calc_id'] for calc in response.json()['calculations']]
    assert mock_put_processing_event.mock.times_called == 2
    default_calc_req = utils.get_default_calc_request()
    assert_processing_event_request(
        mock_put_processing_event.requests[0], default_calc_req, calc_ids[0],
    )
    assert_processing_event_request(
        mock_put_processing_event.requests[1], second_calc_req, calc_ids[1],
    )


def set_mock_processing_events(mock_get_processing_events, events):
    processing_resp_events = []
    for i, event in enumerate(events):
        processing_resp_events.append(
            {
                'event_id': 'event_id_{}'.format(i),
                'created': utils.from_start(minutes=0),
                'handled': True,
                'payload': event,
            },
        )
    mock_get_processing_events.response = {'events': processing_resp_events}


async def test_processing_events_in_diagnostic(
        v2_calc_creator,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    events = get_default_processing_events()
    set_mock_processing_events(mock_get_processing_events, events)
    response = await v2_calc_creator.execute()
    assert response.status_code == 200
    calcs = response.json()['calculations']
    assert calcs[0]['result']['diagnostics']['processing_events'] == events


async def test_processing_events_in_retrieve_diagnostic(
        v1_calc_creator,
        v2_retrieve_calc,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    events = get_default_processing_events()
    set_mock_processing_events(mock_get_processing_events, events)
    calc_resp = await v1_calc_creator.execute()
    assert calc_resp.status_code == 200
    calc_id = calc_resp.json()['calc_id']
    retrieve_resp = await v2_retrieve_calc(calc_ids=[calc_id])
    assert retrieve_resp.status_code == 200
    calcs = retrieve_resp.json()['calculations']
    assert calcs[0]['result']['diagnostics']['processing_events'] == events


async def test_get_previous_calc_id_from_processing(
        conf_exp3_get_calc_id_from_processing,
        v1_calc_creator,
        mock_get_processing_events,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
):
    await conf_exp3_get_calc_id_from_processing(enabled=True)
    calc_resp = await v1_calc_creator.execute()
    assert calc_resp.status_code == 200
    calc_id = calc_resp.json()['calc_id']
    event = {
        'kind': 'calculation',
        'calc_id': calc_id,
        'price_for': 'client',
        'origin_uri': '/some/origin/uri',
        'calc_kind': 'offer',
    }
    set_mock_processing_events(mock_get_processing_events, [event])
    second_calc_resp = await utils.calc_with_previous_calc_id(
        v1_calc_creator, prev_calc_id=calc_id,
    )
    assert second_calc_resp.status_code == 200


async def test_skip_event_creation_by_config_on_calc(
        v1_calc_creator,
        mock_put_processing_event,
        conf_exp3_processing_events_saving_enabled,
        experiments3,
        taxi_cargo_pricing,
):
    await utils.set_events_saving_by_calc_kind(
        experiments3,
        taxi_cargo_pricing,
        value={'offer': True, 'final': True, 'analytical': False},
    )
    v1_calc_creator.payload['calc_kind'] = 'analytical'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert mock_put_processing_event.mock.times_called == 0
    v1_calc_creator.payload['calc_kind'] = 'offer'
    response = await v1_calc_creator.execute()
    assert response.status_code == 200
    assert mock_put_processing_event.mock.times_called == 1


async def test_confirm_usage_event_with_pg(
        v1_calc_creator,
        confirm_usage,
        conf_exp3_processing_events_saving_enabled,
        mock_put_processing_event,
):
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc_id = create_resp.json()['calc_id']
    await confirm_usage(calc_id=calc_id)
    entity_id = utils.get_default_calc_request()['entity_id']
    assert mock_put_processing_event.requests[-1].query['item_id'] == entity_id
    assert (
        mock_put_processing_event.requests[-1].headers['X-Idempotency-Token']
        == f'{calc_id}_confirm-usage'
    )
    assert mock_put_processing_event.requests[-1].json == {
        'kind': 'confirm-usage',
        'calc_id': calc_id,
    }


async def test_confirm_usage_with_empty_entity_id(
        v1_calc_creator,
        confirm_usage,
        conf_exp3_processing_events_saving_enabled,
        mock_put_processing_event,
):
    v1_calc_creator.payload.pop('entity_id')
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc_id = create_resp.json()['calc_id']
    await confirm_usage(calc_id=calc_id)


async def test_confirm_usage_event_with_yt(
        conf_exp3_processing_events_saving_enabled,
        mock_put_processing_event,
        confirm_usage,
):
    calc_id = 'cargo-pricing/v1/731d5f77-8c8b-4ac9-b556-9d38357b92b2'
    await confirm_usage(calc_id=calc_id)
    assert mock_put_processing_event.requests[-1].query['item_id'] == 'claim1'
    assert (
        mock_put_processing_event.requests[-1].headers['X-Idempotency-Token']
        == f'{calc_id}_confirm-usage'
    )
    assert mock_put_processing_event.requests[-1].json == {
        'kind': 'confirm-usage',
        'calc_id': calc_id,
    }


async def test_is_usage_confirmed_calc(
        v1_calc_creator,
        conf_exp3_processing_events_saving_enabled,
        conf_exp3_events_saving_by_calc_kind_default,
        mock_put_processing_event,
):
    v1_calc_creator.payload['is_usage_confirmed'] = True
    create_resp = await v1_calc_creator.execute()
    assert create_resp.status_code == 200
    calc_id = create_resp.json()['calc_id']
    entity_id = utils.get_default_calc_request()['entity_id']
    assert mock_put_processing_event.requests[-1].query['item_id'] == entity_id
    assert (
        mock_put_processing_event.requests[-1].headers['X-Idempotency-Token']
        == f'{calc_id}_confirm-usage'
    )
    assert mock_put_processing_event.requests[-1].json == {
        'kind': 'confirm-usage',
        'calc_id': calc_id,
    }
