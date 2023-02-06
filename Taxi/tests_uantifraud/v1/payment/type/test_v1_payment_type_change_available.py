import pytest

_CACHE_MAX_AGE = 666


@pytest.mark.parametrize(
    'order_id,found,result',
    [
        ('not_found_order', False, 'allow'),
        ('found_fraud', True, 'block'),
        ('found_not_fraud', True, 'allow'),
    ],
)
@pytest.mark.config(
    UAFS_PAYMENT_TYPE_CHANGE_AVAILABLE_RESULT_CACHE_AGE=_CACHE_MAX_AGE,
)
async def test_base(taxi_uantifraud, testpoint, order_id, found, result):
    @testpoint('change_available_result_not_found')
    def not_found_tp(_):
        pass

    resp = await taxi_uantifraud.get(
        f'/v1/payment/type/change_available?order_id={order_id}',
    )
    assert resp.status_code == 200
    assert resp.json() == {'status': result}
    assert resp.headers['Cache-Control'] == f'max-age={_CACHE_MAX_AGE}'

    if found:
        assert not not_found_tp.has_calls
    else:
        await not_found_tp.wait_call()
