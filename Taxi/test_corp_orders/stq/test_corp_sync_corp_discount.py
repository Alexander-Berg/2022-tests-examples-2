import decimal

import pytest

from corp_orders.stq import corp_sync_corp_discount
from test_corp_orders.stq import stq_test_util as util

ORDER_ID = '191015-243801'
NO_ORDER_ERRORS = {
    corp_sync_corp_discount.OrderNotFound,
    corp_sync_corp_discount.ServiceNotSupported,
}


@pytest.mark.parametrize(
    ['case_params'],
    [
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                stq_error=corp_sync_corp_discount.ApplyNotFound,
            ),
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_1.sql'],
            ),
            id='no corp discount',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                corp_discount='10',
                corp_discount_reverted=False,
                corp_discount_version=1,
                stq_error=corp_sync_corp_discount.OrderNotFound,
            ),
            id='no order yet found',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                corp_discount='10',
                corp_discount_reverted=False,
                corp_discount_version=1,
            ),
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_1.sql'],
            ),
            id='with corp discount',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                corp_discount='10',
                corp_discount_reverted=True,
                corp_discount_version=2,
            ),
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_1.sql'],
            ),
            id='with corp discount reverted',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='drive',
                stq_error=corp_sync_corp_discount.ServiceNotSupported,
            ),
            id='service not supported yet',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                corp_discount='10',
                corp_discount_reverted=False,
                corp_discount_version=1,
                order_discount='100',
                order_discount_reverted=True,
                order_discount_version=2,
            ),
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_version_2.sql'],
            ),
            id='too old version from api',
        ),
        pytest.param(
            dict(
                order_id=ORDER_ID,
                service='eats2',
                corp_discount='100',
                corp_discount_reverted=True,
                corp_discount_version=2,
            ),
            marks=pytest.mark.pgsql(
                'corp_orders', files=['insert_eda_order_version_2.sql'],
            ),
            id='same version from api',
        ),
    ],
)
async def test_sync_corp_discount_eda(stq3_context, mockserver, case_params):
    order_id = case_params['order_id']
    order_service = case_params['service']
    stq_error = case_params.get('stq_error')
    # values for API
    corp_discount = case_params.get('corp_discount')
    corp_discount_reverted = case_params.get('corp_discount_reverted')
    corp_discount_version = case_params.get('corp_discount_version')
    # expected values in db
    order_discount = case_params.get('order_discount', corp_discount)
    order_discount_reverted = case_params.get(
        'order_discount_reverted', corp_discount_reverted,
    )
    order_discount_version = case_params.get(
        'order_discount_version', corp_discount_version,
    )

    @mockserver.json_handler('/corp-discounts/v1/applies/get')
    async def _corp_discounts_applies_get(request):
        if case_params.get('corp_discount') is None:
            return mockserver.make_response(
                json={'message': 'no discount'}, status=404,
            )
        discount_value = decimal.Decimal(corp_discount)
        vat_value = discount_value * decimal.Decimal('0.2')
        return {
            'client_id': 'client_1',
            'discount_amount': {
                'sum': corp_discount,
                'vat': str(vat_value),
                'with_vat': str(discount_value + vat_value),
            },
            'is_reverted': corp_discount_reverted,
            'order_created': '2021-09-24T00:00:00+00:00',
            'apply_timestamp': '2021-09-24T01:00:00+00:00',
            'order_version': corp_discount_version,
            'order_id': order_id,
            'order_price': '1024',
            'service': order_service,
            'user_id': 'user_1',
        }

    try:
        await corp_sync_corp_discount.task(
            stq3_context, order_id, order_service, corp_discount_version,
        )
    except corp_sync_corp_discount.BaseError as exc:
        assert exc.__class__ == stq_error
        if stq_error == corp_sync_corp_discount.ServiceNotSupported:
            return
    else:
        assert stq_error is None, 'should have raised %r' % stq_error

    order_json_value = await util.fetch_eda_order(stq3_context, order_id)
    if stq_error in NO_ORDER_ERRORS:
        assert order_json_value is None
    else:
        assert order_json_value is not None
        assert 'corp_discount' in order_json_value
        if order_discount is not None:
            order_discount = util.get_sum_with_vat(order_discount)
        assert order_json_value.pop('corp_discount') == order_discount
        _is_reverted = order_json_value.pop('corp_discount_reverted')
        assert _is_reverted == order_discount_reverted
        discount_version = order_json_value.pop('corp_discount_version')
        assert discount_version == order_discount_version
