def update_dict(data, **kwargs):
    for key, val in kwargs.items():
        if val is None:
            data.pop(key, None)
        else:
            data[key] = val


class RegisterCashbackRequest:
    def __init__(self, taxi_cashback_web):
        self.client = taxi_cashback_web

    async def make_request(self, *, override_params=None, override_data=None):
        params = {'service': 'yataxi'}
        if override_params:
            update_dict(params, **override_params)

        data = {
            'clear_sum': '100',
            'currency': 'RUB',
            'version': 0,
            'yandex_uid': 'yandex_uid_1',
            'payload': {},
            'cashback_by_source': [],
        }
        if override_data:
            update_dict(data, **override_data)

        return await self.client.post(
            '/v2/internal/cashback/register', params=params, json=data,
        )


class CalcCashbackRequest:
    def __init__(self, taxi_cashback_web):
        self.client = taxi_cashback_web

    async def make_request(self, *, override_params=None, override_data=None):
        params = {'order_id': 'order_id_default'}

        data = {'held': '0', 'cleared': '100', 'currency': 'RUB'}
        if override_data:
            update_dict(data, **override_data)

        return await self.client.post(
            '/v1/cashback/calc', params=override_params or params, json=data,
        )


class V2CalcCashbackRequest:
    def __init__(self, taxi_cashback_web):
        self.client = taxi_cashback_web

    async def make_request(self, *, override_data=None):
        data = {
            'held': [],
            'cleared': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '100'}],
                },
            ],
            'currency': 'RUB',
        }
        if override_data:
            update_dict(data, **override_data)

        return await self.client.post('/v2/cashback/calc', json=data)


class RestoreCashbackRequest:
    def __init__(self, taxi_cashback_web):
        self.client = taxi_cashback_web

    async def make_request(self, *, override_params=None):
        params = {'order_id': 'order_id_4'}
        return await self.client.post(
            '/v2/internal/cashback/restore', params=override_params or params,
        )


class PaymentSplitRequest:
    def __init__(self, taxi_cashback_web):
        self.client = taxi_cashback_web

    async def make_request(self, **override_data):
        data = {
            'sum_to_pay': {'ride': '100', 'tips': '20'},
            'payment': {
                'type': 'card',
                'payment_method_id': 'card_method_id',
                'complements': [
                    {
                        'type': 'personal_wallet',
                        'payment_method_id': 'wallet_id/1234567',
                    },
                ],
            },
            'yandex_uid': 'yandex_uid',
            'currency': 'RUB',
            'brand': 'yataxi',
            'taxi_status': 'completed',
            'status': 'finished',
            'fixed_price': True,
        }
        data.update(override_data)
        return await self.client.post('/v1/internal/payment/split', json=data)
