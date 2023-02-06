import pytest


async def test_status_updated_event(
        mock_procaas_create,
        procaas_extract_token,
        assert_correct_scope_queue,
        notify_status_updated,
):
    claim_id = '123'
    data = {'revision': 4, 'status': 'accepted', 'has_resolution': False}
    expected_token = 'status_updated_{}'.format(data['revision'])

    await notify_status_updated(claim_id, data)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert_correct_scope_queue(request)
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'status_updated', 'data': data}


async def test_price_recalculated_event(
        mock_procaas_create,
        procaas_extract_token,
        assert_correct_scope_queue,
        notify_price_recalculated,
):
    claim_id = '123'
    data = {'claim_revision': 4, 'price': '300.0000', 'calc_id': '678'}
    expected_token = 'price_recalculated_{}'.format(data['calc_id'])

    await notify_price_recalculated(claim_id, data)

    data['price'] = '300'  # because was converted to money

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert_correct_scope_queue(request)
    assert request.query == {'item_id': claim_id}
    assert procaas_extract_token(request) == expected_token
    assert request.json == {'kind': 'price_recalculated', 'data': data}


@pytest.mark.parametrize(
    ['pricing_sum', 'procaas_sum'],
    [
        ('300.0', '300'),
        ('300.', '300'),
        ('0.10', '0.1'),
        ('0.', '0'),
        ('-0.', '0'),
        ('.0', '0'),
        ('.', '0'),
        ('', '0'),
    ],
)
async def test_accepted_money_format(
        mock_procaas_create,
        notify_price_recalculated,
        pricing_sum,
        procaas_sum,
):
    claim_id = '123'
    data = {'claim_revision': 4, 'price': pricing_sum, 'calc_id': '678'}

    await notify_price_recalculated(claim_id, data)

    assert mock_procaas_create.times_called == 1
    request = mock_procaas_create.next_call()['request']
    assert request.json['data']['price'] == procaas_sum


@pytest.fixture(name='notify_status_updated')
def _notify_status_updated(notify_func_factory):
    url = '/internal/cargo-finance/flow/claims/events/status-updated'
    return notify_func_factory(url)


@pytest.fixture(name='notify_price_recalculated')
def _notify_price_recalculated(notify_func_factory):
    url = '/internal/cargo-finance/flow/claims/events/price-recalculated'
    return notify_func_factory(url)


@pytest.fixture(name='notify_func_factory')
def _notify_func_factory(taxi_cargo_finance):
    def wrapper(url):
        async def func(claim_id, data, expected_code=200):
            response = await taxi_cargo_finance.post(
                url, params={'claim_id': claim_id}, json=data,
            )
            assert response.status_code == expected_code
            return response

        return func

    return wrapper
