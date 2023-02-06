import pytest


@pytest.mark.parametrize(
    'json,code,expected',
    [
        (
            {
                'situation_id': 3,
                'source': 'call',
                'order_cost': 1400,
                'payment_method_type': 'card',
                'compensation_count': 0,
                'antifraud_score': 'good',
                'country': 'ru',
                'delivery_class': 'ultima',
            },
            200,
            {
                'compensation_packs': [
                    {
                        'id': 3,
                        'compensations': [
                            {
                                'id': 10,
                                'type': 'refund',
                                'is_full_refund': False,
                                'min_value': 200,
                                'notification': 'order.compensation.refund',
                            },
                            {
                                'id': 13,
                                'description': 'test',
                                'type': 'tipsRefund',
                                'rate': 10.0,
                                'is_full_refund': True,
                                'max_value': 1600,
                                'min_value': 200,
                                'notification': (
                                    'order.compensation.tips_refund'
                                ),
                            },
                            {
                                'id': 16,
                                'type': 'superRefund',
                                'is_full_refund': True,
                                'max_value': 1600,
                                'notification': 'order.compensation.refund',
                            },
                        ],
                    },
                ],
                'situation_code': 'long_delay',
                'situation_group_title': 'Долгое ожидание доставки',
                'situation_id': 3,
                'situation_title': 'более 30 минут',
            },
        ),
        (
            {
                'situation_id': 3,
                'source': 'call',
                'order_cost': 1400,
                'payment_method_type': 'card',
                'compensation_count': 0,
                'antifraud_score': 'good',
                'country': 'ru',
                'delivery_class': 'regular',
            },
            200,
            {
                'compensation_packs': [],
                'situation_code': 'long_delay',
                'situation_group_title': 'Долгое ожидание доставки',
                'situation_id': 3,
                'situation_title': 'более 30 минут',
            },
        ),
        (
            {
                'situation_id': 33,
                'source': 'call',
                'order_cost': 1400,
                'payment_method_type': 'card',
                'compensation_count': 0,
                'antifraud_score': 'good',
                'country': 'ru',
            },
            400,
            {'code': '404', 'message': 'Situation not found'},
        ),
    ],
)
async def test_submit_situation(
        taxi_eats_compensations_matrix, mockserver, json, code, expected,
):
    response = await taxi_eats_compensations_matrix.post(
        '/eats-compensations-matrix/v1/api/compensation/submit_situation',
        json=json,
    )

    assert response.status_code == code
    assert response.json() == expected
