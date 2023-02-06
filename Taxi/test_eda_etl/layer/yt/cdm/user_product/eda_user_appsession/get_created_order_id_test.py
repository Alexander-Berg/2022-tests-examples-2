from eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import get_created_order_id


def test_get_order_id():
    for input_value, input_name, expected in (
        ({}, None, None),
        ({'order_id': '1234-1234'}, 'eda.checkout.order_created', '1234-1234'),
        ({'not_order_id': '1234-1235', 'order_id': '1234-1234'}, 'eda.checkout.order_created1', None),
        ({'order_created': {'not_order_id': '1234-1235', 'order_id': '1234-1234'}}, 'checkout', '1234-1234'),
        ({'not_order_created': {'not_order_id': '1234-1235', 'order_id': '1234-1234'}}, 'checkout', None),
    ):
        actual = get_created_order_id(input_value, input_name)

        assert (expected == actual), \
            'Expected order_id is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_value
            )
