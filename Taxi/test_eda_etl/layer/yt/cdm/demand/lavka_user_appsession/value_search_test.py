from eda_etl.layer.yt.cdm.demand.lavka_user_appsession.impl import value_search


def test_get_order_id():
    for input_dict, expected in (
        ({}, None),
        ({'first_purchase':{'order':{'order_id':'first_purchase123'}},
          'first_purchase1':{'order':{'order_id':'first_purchase1234'}}}, 'first_purchase123'),
        ({'repeat_purchase':{'order':{'order_id':'repeat_purchase123'}},
          'first_purchase1':{'order':{'order_id':'first_purchase1234'}}}, 'repeat_purchase123'),
        ({'first_purchase':{'order':{'order_id':'first_purchase123'}},
          'repeat_purchase':{'order':{'order_id':'repeat_purchase123'}}}, 'first_purchase123'),
        ({'first_purchase1': {'orders': {'order': {'order_id': 'first_purchase1234'}}}}, 'first_purchase1234'),
        ({'order_id': 'first_purchase1234'}, 'first_purchase1234'),
        ({"original_timestamp":"1596363004651", "type: taxi_app":{"order_id":"200802-058519"}},"200802-058519")
    ):
        actual = value_search(input_dict, 'order_id')

        assert (expected == actual), \
            'Expected order_id is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_dict
            )


def test_get_order_id_with_converter():
    for input_dict, converter, expected in (
        ({}, int, None),
        ({'first_purchase':{'order':{'order_id':'1'}}}, int, 1),
        ({'order_id':'42'}, int, 42 ),
        ({'order_id':42}, str, '42'),
    ):
        actual = value_search(input_dict, 'order_id', converter)

        assert (expected == actual), \
            'Expected order_id is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected, actual, input_dict
            )
