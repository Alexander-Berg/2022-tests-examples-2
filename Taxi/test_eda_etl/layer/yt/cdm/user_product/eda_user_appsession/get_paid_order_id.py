from eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import get_paid_order_id, get_paid_order_id_lavka


def test_get_order_id():
    for input_dict, input_name, expected in (
        ({}, None, None),
        ({'second_purchase': {'type: applepay': {'order_id': 123}}}, None, None),
        ({'first_purchase': {'type: android': {'order_id': 'first_purchase123'}},
          'first_purchase1': {'type: android': {'order_id': 'first_purchase1234'}}}, None, 'first_purchase123'),
        ({'first_purchase': {
            'type: android': {'order_id': 'first_purchase123'},
            'type: android1': {'order_id': 'first_purchase123'},
            'type: android3': {'order_id': 'first_purchase123'}
            },
          'first_purchase1': {'type: android': {'order_id': 'first_purchase1234'}}}, None, 'first_purchase123'),
        ({'first_purchase': {'123type: applepay': {'order_id': 'first_purchase123'}},
          'first_purchase1': {'type: applepay': {'order_id': 'first_purchase1234'}}}, None, None),
        ({'first_purchase': {'type: android': None},
          'first_purchase1': {'type: android': {'order_id': 'first_purchase1234'}}}, None, None),
        ({'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}},
          'first_purchase1': {'type: applepay': {'order_id': 'first_purchase1234'}}}, None, 'repeat_purchase123'),
        ({'first_purchase': {'type: applepay': {'order_id': 'first_purchase123'}},
          'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}}}, None, 'first_purchase123'),
        ({'first_purchase': {'type: android': {'order_id': 'first_purchase123'}},
          'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}}}, 'eda.checkout.repeat_purchase', None),
        ({'not_order_id': '1234-1235','order_id': '1234-1234'}, 'eda.checkout.repeat_purchase', '1234-1234'),
        ({'not_order_id': '1234-1235', 'order_id': '1234-1234'}, 'eda.checkout.repeat_purchase1', None),
        ({'not_order_id': '1234-1235','order_id': '1234-1234'}, 'eda.lavka.checkout.purchase', None),
        ({'first_purchase': {'order_id': 'first_purchase123'},
          'first_purchase1': {'order_id': 'first_purchase1234'}}, None, 'first_purchase123'),
        ({'first_purchase': {'order_id': None},
          'first_purchase1': {'order_id': 'first_purchase1234'}}, None, None),
        ({'first_purchase': None,
          'first_purchase1': {'order_id': 'first_purchase1234'}}, None, None),
        ({'first_purchase1': None,
          'first_purchase': {'type: applepay': 'first_purchase1234'}}, None, None),
    ):
        actual = get_paid_order_id(input_dict, input_name)

        assert (expected == actual), \
            'Expected order_id is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_dict
            )


def test_get_order_id_lavka():
    for input_dict, input_name, expected in (
        ({}, None, None),
        ({'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}},
          'first_purchase1': {'type: applepay': {'order_id': 'first_purchase1234'}}}, None, None),
        ({'first_purchase': {'type: applepay': {'order_id': 'first_purchase123'}},
          'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}}}, None, None),
        ({'first_purchase': {'type: android': {'order_id': 'first_purchase123'}},
          'repeat_purchase': {'type: applepay': {'order_id': 'repeat_purchase123'}}}, 'eda.lavka.checkout.purchase', None),
        ({'not_order_id': '1234-1235','order_id': '1234-1234'}, 'eda.lavka.checkout.purchase', '1234-1234'),
        ({'not_order_id': '1234-1235', 'order_id': '1234-1234'}, 'eda.lavka.checkout.purchase1', None),
        ({'first_purchase': {'order_id': 'first_purchase123'},
          'first_purchase1': {'order_id': 'first_purchase1234'}}, None, None),
        ({'not_order_id': '1234-1235', 'order_id': '1234-1234'}, 'eda.checkout.repeat_purchase', None),
    ):
        actual = get_paid_order_id_lavka(input_dict, input_name)

        assert (expected == actual), \
            'Expected order_id is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_dict
            )
