import aiohttp


class BaseResponse:
    inner_dict = None
    http_status = 200

    def set_http_status(self, status_code):
        self.http_status = status_code
        return self

    def update(self, **kwargs):
        for key, val in kwargs.items():
            if val is None:
                self.inner_dict.pop(key, None)
            else:
                self.inner_dict[key] = val

    def make_response(self):
        return aiohttp.web.json_response(
            self.inner_dict, status=self.http_status,
        )


class RetrieveInvoice(BaseResponse):
    def __init__(self):
        self.inner_dict = {
            'cleared': {},
            'currency': 'RUB',
            'debt': {},
            'held': {'ride': '20'},
            'id': 'order_id',
            'invoice_due': '2020-02-17T11:14:00+03:00',
            'operation_info': {},
            'payment_type': 'card',
            'status': 'held',
            'sum_to_pay': {'ride': '200', 'tips': '0'},
            'transactions': [],
            'yandex_uid': 'yandex_uid_1',
        }


class RetrieveInvoiceV2(BaseResponse):
    def __init__(self):
        self.inner_dict = {
            'id': 'order_id',
            'invoice_due': '2020-04-15T14:24:00+03:00',
            'created': '2020-04-15T14:24:00+03:00',
            'currency': 'RUB',
            'status': 'held',
            'payment_types': ['card'],
            'sum_to_pay': [
                {
                    'payment_type': 'card',
                    'items': [
                        {'item_id': 'ride', 'amount': '291'},
                        {'item_id': 'tips', 'amount': '0'},
                    ],
                },
            ],
            'held': [
                {
                    'payment_type': 'card',
                    'items': [{'item_id': 'ride', 'amount': '20'}],
                },
            ],
            'cleared': [],
            'debt': [],
            'operation_info': {},
            # Transactions aren't relevant to our particular use case,
            # but in reality they are not empty
            'transactions': [],
            'yandex_uid': 'yandex_uid_1',
            'operations': [],
            'cashback': {
                'status': 'init',
                'version': 1,
                'rewarded': [],
                'transactions': [],
                'operations': [],
                'commit_version': 1,
            },
            'user_ip': '2a02:6b8:b010:50a3::3',
        }
