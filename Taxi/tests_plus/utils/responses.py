import json


class BaseResponse:
    inner_dict = None
    http_status = 200

    def set_http_status(self, status_code):
        self.http_status = status_code
        return self

    def _to_json(self):
        return json.dumps(self.inner_dict)

    def make_response(self, mockserver):
        return mockserver.make_response(
            self._to_json(), status=self.http_status,
        )


class SubmitNativeOrderResponse(BaseResponse):
    def __init__(self):
        self.inner_dict = {'result': {}, 'invocationInfo': {}}
        self.result_dict = self.inner_dict['result']
        self.status('success')

    def status(self, status):
        self.result_dict['status'] = status
        return self

    def order_id(self, order_id):
        self.result_dict['orderId'] = order_id
        return self


class BillingOrderInfoResponse(BaseResponse):
    def __init__(self):
        self.inner_dict = {'result': {}, 'invocationInfo': {}}
        self.result_dict = self.inner_dict['result']
        self.status('ok')

    def status(self, status):
        self.result_dict['status'] = status
        return self

    def order_id(self, order_id):
        self.result_dict['orderId'] = order_id
        return self

    def sync_features(self, sync_features):
        self.result_dict['synchronizationState'] = {
            'featuresSync': sync_features,
        }
        return self


class TransferResponse(BaseResponse):
    def __init__(self):
        self.inner_dict = {'result': {}, 'invocationInfo': {}}
        self.result_dict = self.inner_dict['result']

    def error_id(self, error_id):
        self.result_dict['id'] = error_id

    def status(self, status):
        self.result_dict['status'] = status
        return self

    def order_id(self, order_id):
        self.result_dict['orderId'] = order_id
        return self


class StopSubscription(BaseResponse):
    def __init__(self):
        self.result_dict = None
        self.inner_dict = {'invocationInfo': {}}

    def _ensure_result(self):
        if 'result' not in self.inner_dict:
            self.result_dict = {}
            self.inner_dict['result'] = self.result_dict

    def success(self):
        self.inner_dict.pop('result', {})

    def error(self, error_id, description=None):
        self._ensure_result()
        self.result_dict['id'] = error_id
        if description:
            self.result_dict['description'] = description


class TransitionsResponse(BaseResponse):
    def __init__(self, load_json_func):
        self.load_json = load_json_func
        self.inner_dict = self.load_json('transitions_response.json')


class CashbackStatusResponse(BaseResponse):
    def __init__(self):
        self.inner_dict = {'result': {}, 'invocationInfo': {}}
        self.result_dict = self.inner_dict['result']
        self.status('OK')

    def status(self, status):
        self.result_dict['status'] = status
        return self


class OrderFields(BaseResponse):
    def __init__(self):
        self.inner_dict = {
            'order_id': '12345abcd',
            'fields': {'order': {'pricing_data': {'user': {'data': {}}}}},
            'replica': 'master',
            'version': '15',
        }

    def balance(self, balance):
        if balance is not None:
            self.inner_dict['fields']['order']['pricing_data']['user'][
                'data'
            ] = {'complements': {'personal_wallet': {'balance': balance}}}
        return self
