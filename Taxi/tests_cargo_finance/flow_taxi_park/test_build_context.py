async def test_order_context(
        build_taxi_order_context,
        mock_py2_taxi_order_context,
        mock_v1_parks_retrieve,
        get_event,
        taxi_order_id,
):
    mock_py2_taxi_order_context.code = 404
    order_context = await build_taxi_order_context()

    assert mock_py2_taxi_order_context.mock.times_called == 1
    request = mock_py2_taxi_order_context.mock.next_call()['request']
    assert request.json == {'order_id': taxi_order_id}

    assert order_context == get_event('taxi_order_context')['payload']['data']


async def test_py2_products_request(
        build_taxi_order_context,
        mock_py2_taxi_order_context,
        mock_v1_parks_retrieve,
        mock_py2_products,
        taxi_order_id,
):
    mock_py2_taxi_order_context.code = 404
    order_context = await build_taxi_order_context()

    assert mock_py2_products.times_called == 1
    request = mock_py2_products.next_call()['request']
    assert request.query == {}
    assert request.json == {
        'park_clid': order_context['park_clid'],
        'timestamp': order_context['taxi_order_due'],
    }

    assert mock_py2_taxi_order_context.mock.times_called == 1
    request = mock_py2_taxi_order_context.mock.next_call()['request']
    assert request.json == {'order_id': taxi_order_id}


async def test_py2_taxi_order_context_request(
        build_taxi_order_context,
        mock_py2_taxi_order_context,
        mock_v1_parks_retrieve,
        get_event,
        taxi_order_id,
        load_json,
):
    order_context = await build_taxi_order_context()
    expected_context = load_json('order_context.json')

    assert mock_py2_taxi_order_context.mock.times_called == 1
    request = mock_py2_taxi_order_context.mock.next_call()['request']
    assert request.json == {'order_id': taxi_order_id}

    assert order_context == expected_context


async def test_waybill_context_request(
        build_waybill_billing_context,
        mock_waybill_find_ref,
        mock_waybill_info,
        taxi_order_id,
):
    await build_waybill_billing_context()

    assert mock_waybill_find_ref.times_called == 1
    assert mock_waybill_info.mock.times_called == 1

    request = mock_waybill_find_ref.next_call()['request']
    assert request.json == {'taxi_order_id': taxi_order_id}


async def test_waybill_context_dispatch_returns404(
        build_waybill_billing_context,
        mock_waybill_find_ref,
        mock_waybill_info,
):
    mock_waybill_info.code = 404
    mock_waybill_info.data = {
        'code': 'waybill not found',
        'message': 'waybill not found',
    }
    response = await build_waybill_billing_context()

    assert mock_waybill_find_ref.times_called == 1
    assert mock_waybill_info.mock.times_called == 1
    assert response.status_code == 500


async def test_waybill_context_performer_not_found(
        build_waybill_billing_context,
        mock_waybill_find_ref,
        mock_waybill_info,
):
    del mock_waybill_info.data['execution']['taxi_order_info'][
        'last_performer_found_ts'
    ]
    response = await build_waybill_billing_context()

    assert mock_waybill_find_ref.times_called == 1
    assert mock_waybill_info.mock.times_called == 1
    assert response.status_code == 404
    assert response.json() == {
        'fail_reason': {
            'code': 'performer_not_found',
            'message': (
                'No last_performer_found_ts '
                'in WaybillInfo.Execution.TaxiOrderInfo'
            ),
            'details': {},
        },
    }
