import pytest

from tests_corp_discounts import consts


def mock_stq(mockserver):
    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    def _mock_stq_schedule(request, queue_name):
        return {}

    class MockContext:
        @property
        def times_called(self):
            return _mock_stq_schedule.times_called

        @property
        def next_call_value(self):
            return _mock_stq_schedule.next_call()

    return MockContext()


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_apply_new_order(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('client_1_order_1.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    response_dict = response.json()
    assert response_dict['discount'] == {
        'sum': '200',
        'vat': '40',
        'with_vat': '240',
    }
    assert response_dict['status'] == 'created'

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'drive'
    assert stq_kwargs['order_version'] == 1


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_order_limit_exceeded(
        taxi_corp_discounts, mockserver, load_json,
):
    mock_context = mock_stq(mockserver)

    body = load_json('client_1_order_1.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    response_dict = response.json()
    assert response_dict['discount'] == {
        'sum': '200',
        'vat': '40',
        'with_vat': '240',
    }
    assert response_dict['status'] == 'created'

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'drive'
    assert stq_kwargs['order_version'] == 1

    body = load_json('client_1_order_2.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    # because we exceeded discount uses limit (of 1 order)
    assert response.status == 200
    assert response.json()['status'] == 'rejected'
    assert mock_context.times_called == 0


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_update_revert(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('client_1_order_1.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    response_dict = response.json()
    assert response_dict['discount'] == {
        'sum': '200',
        'vat': '40',
        'with_vat': '240',
    }
    assert response_dict['status'] == 'created'

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'drive'
    assert stq_kwargs['order_version'] == 1

    body['order_price'] = '100'
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    # test that discount cannot be applied to new cost
    assert response.status == 200
    assert response.json()['status'] == 'reverted'

    body['order_price'] = '200'
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    # test that discount cannot be applied after revert even if now qualifies
    # for discount
    assert response.status == 200
    assert response.json()['status'] == 'reverted'

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'drive'
    assert stq_kwargs['order_version'] == 2

    # max orders in discount is 1, so we test that previous order use
    # was rolled back and we can use it for another order
    body = load_json('client_1_order_2.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    response_dict = response.json()
    assert response_dict['status'] == 'created'
    assert response_dict['discount'] == {
        'sum': '200',
        'vat': '40',
        'with_vat': '240',
    }

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_2'
    assert stq_kwargs['service'] == 'drive'
    assert stq_kwargs['order_version'] == 1


@pytest.mark.config(CORP_COUNTRIES_SUPPORTED=consts.CORP_COUNTRIES_SUPPORTED)
@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_order_update_ok(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('client_2_order_1.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    previous_response_dict = response.json()
    assert previous_response_dict['discount'] == {
        'sum': '100',
        'vat': '20',
        'with_vat': '120',
    }

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'eats2'
    assert stq_kwargs['order_version'] == 1

    body['order_price'] = str(int(body['order_price']) * 2)
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    response_dict = response.json()
    assert response_dict['discount'] == {
        'sum': '200',
        'vat': '40',
        'with_vat': '240',
    }
    assert response.json()['status'] == 'updated'

    assert mock_context.times_called == 1
    stq_next_call = (
        mock_context.next_call_value
    )  # it consumes next_call(), so we have to store it
    assert stq_next_call['queue_name'] == 'corp_sync_corp_discount'
    stq_params = stq_next_call['request'].json
    stq_kwargs = stq_params['kwargs']
    assert stq_kwargs['order_id'] == 'order_id_1'
    assert stq_kwargs['service'] == 'eats2'
    assert stq_kwargs['order_version'] == 2


@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_wrong_currency(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('order_with_wrong_currency.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    assert response.status == 200
    assert response.json()['status'] == 'rejected'
    assert mock_context.times_called == 0


@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_timezone_specific(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('client_1_order_3.json')
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    # order was created before activation (if we convert timezones)
    assert response.status == 200
    assert response.json()['status'] == 'rejected'
    assert mock_context.times_called == 0


@pytest.mark.pgsql(
    'corp_discounts',
    files=['insert_discounts.sql', 'insert_discount_link.sql'],
)
async def test_reject_zero_cost(taxi_corp_discounts, mockserver, load_json):
    mock_context = mock_stq(mockserver)

    body = load_json('client_2_order_1.json')
    body['order_price'] = '0'
    response = await taxi_corp_discounts.post('/v1/discounts/apply', json=body)
    # order price is 0, so order did not pass checks
    assert response.status == 200
    assert response.json()['status'] == 'rejected'
    assert mock_context.times_called == 0
