import uuid

TOPIC_ID = uuid.uuid4().hex
TRANSACTION_ID = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_2 = uuid.uuid4().hex
TRANSACTION_ID_2 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_01 = uuid.uuid4().hex
TRANSACTION_ID_01 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_21 = uuid.uuid4().hex
TRANSACTION_ID_21 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_3 = uuid.uuid4().hex
TRANSACTION_ID_3 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_4 = uuid.uuid4().hex
TRANSACTION_ID_4 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_5 = uuid.uuid4().hex
TRANSACTION_ID_5 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_6 = uuid.uuid4().hex
TRANSACTION_ID_6 = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_3_TC = uuid.uuid4().hex
TRANSACTION_ID_3_TC = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_4_TC = uuid.uuid4().hex
TRANSACTION_ID_4_TC = uuid.uuid4().hex + '_maybe_random_text'
TOPIC_ID_5_TC = uuid.uuid4().hex
TRANSACTION_ID_5_TC = uuid.uuid4().hex + '_maybe_random_text'


TOPIC_CONTEXT = {
    'provider_inn': '123456789',
    'service_rendered_at': '2021-03-26T09:00:00+00:00',
    'title': 'Услуга доставки',
    'country': 'RUS',
}

REQUEST = {
    'transactions': [
        {
            'transaction_id': 'transaction_id',
            'is_refund': False,
            'payment_method': 'card',
            'price_details': {
                'without_vat': '12.5',
                'vat': '.5',
                'total': '13.0',
            },
        },
    ],
}
