import pytest

ORDER_ID = '8c83b49edb274ce0992f337061047375'


def setup_collection_item(collection, key, value):
    if value is not None:
        collection.update({'_id': ORDER_ID}, {'$set': {key: value}})


def setup_order_proc_current_prices(
        db,
        kind,
        user_total_price,
        user_total_display_price,
        user_ride_display_price,
        cost_breakdown=None,
):
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_price',
        user_total_price,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_total_display_price',
        user_total_display_price,
    )
    setup_collection_item(
        db.order_proc,
        'order.current_prices.user_ride_display_price',
        user_ride_display_price,
    )
    setup_collection_item(db.order_proc, 'order.current_prices.kind', kind)

    if cost_breakdown is not None:
        setup_collection_item(
            db.order_proc,
            'order.current_prices.cost_breakdown',
            cost_breakdown,
        )


@pytest.mark.config(CURRENT_PRICES_WORK_MODE='newway')
@pytest.mark.experiments3(filename='exp3_paid_by_plus_flag_enabled.json')
@pytest.mark.now('2016-12-15T11:30:00+0300')
def test_totw_driver_status(taxi_protocol, db):
    db.order_proc.update(
        {'_id': ORDER_ID},
        {
            '$set': {
                'order._type': 'soon',
                'order.status': 'pending',
                'order.taxi_status': 'assigned',
            },
        },
    )

    setup_order_proc_current_prices(
        db,
        'taximeter',
        100.0,
        0.0,
        100.0,
        [{'type': 'personal_wallet', 'amount': 100.0}],
    )

    response = taxi_protocol.post(
        '3.0/taxiontheway',
        {
            'format_currency': True,
            'id': 'b300bda7d41b4bae8d58dfa93221ef16',
            'orderid': '8c83b49edb274ce0992f337061047375',
        },
    )
    assert response.status_code == 200
    content = response.json()

    assert 'cost_message_details' in content
    cost_message_details = content['cost_message_details']

    assert 'cost_flags' in cost_message_details
    cost_flags = cost_message_details['cost_flags']

    assert cost_flags == [{'type': 'paid_by_plus'}]
