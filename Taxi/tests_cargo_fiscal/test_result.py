import pytest


@pytest.mark.parametrize(
    'topic_id, expected_response',
    (
        (
            'topic_id',
            {
                'receipts': [
                    {
                        'is_ready': True,
                        'transaction_id': 'transaction_id',
                        'url': 'url',
                        'context': {
                            'is_refund': False,
                            'payment_method': 'card',
                            'transaction_id': 'transaction_id',
                        },
                    },
                ],
                'context': {
                    'title': 'Услуги курьерской доставки',
                    'country': 'RUS',
                    'provider_inn': '381805387129',
                    'service_rendered_at': '2022-03-03T14:25:49.233+00:00',
                },
            },
        ),
        (
            'unready_topic_id',
            {
                'receipts': [
                    {
                        'is_ready': False,
                        'transaction_id': 'transaction_id',
                        'context': {
                            'is_refund': False,
                            'payment_method': 'card',
                            'transaction_id': 'transaction_id',
                        },
                    },
                ],
                'context': {
                    'title': 'Услуги курьерской доставки',
                    'country': 'RUS',
                    'provider_inn': '381805387129',
                    'service_rendered_at': '2022-03-03T14:25:49.233+00:00',
                },
            },
        ),
        ('wrong_topic_id', {'receipts': []}),
    ),
)
async def test_result(taxi_cargo_fiscal, topic_id, expected_response):
    response = await taxi_cargo_fiscal.post(
        f'/internal/cargo-fiscal/receipts/delivery/'
        f'orders/result?topic_id={topic_id}',
    )

    assert response.status_code == 200
    assert response.json() == expected_response
