async def test_antifraud_sum(web_processing_antifraud):
    response = await web_processing_antifraud.antifraud_sum.make_request(
        'order_id',
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'sum_to_pay': {
            'ride': [
                {
                    'payment_method_id': 'card-x60e569d527cbd5e67212045e',
                    'sum': '150',
                    'type': 'card',
                },
            ],
        },
    }


async def test_not_found_order(web_processing_antifraud):
    response = await web_processing_antifraud.antifraud_sum.make_request(
        'random_order',
    )
    assert response.status == 404
