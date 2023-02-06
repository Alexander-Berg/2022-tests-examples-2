import json

import pytest


REGISTER_MESSAGE_ID = 'selfemployed-message-id'

FNS_RECEIPT_URL = 'fns-receipt-url.jpg'
FNS_RECEIPT_ID = 'fns-receipt-id'

SELFEMPLOYED_PROCESSING_RESPONSE = {
    'status_code': 200,
    'body': {'ProcessingStatus': 'PROCESSING'},
}

SELFEMPLOYED_DUPLICATE = {
    'status_code': 400,
    'body': {
        'Code': 'DUPLICATE',
        'Message': 'receipt already exists',
        'Args': [
            {'Key': 'RECEIPT_URL', 'Value': FNS_RECEIPT_URL},
            {'Key': 'RECEIPT_ID', 'Value': FNS_RECEIPT_ID},
        ],
    },
    'error_code': 'fns_duplicate',
}


SELFEMPLOYED_NOT_FOUND = {
    'status_code': 404,
    'body': {'Code': 'NOT_FOUND', 'Message': 'message id not found'},
}

SELFEMPLOYED_ALREADY_DELETED = {
    'status_code': 400,
    'body': {
        'Code': 'ALREADY_DELETED',
        'Message': 'receipt already deleted',
        'Args': [{'Key': 'RECEIPT_ID', 'Value': FNS_RECEIPT_ID}],
    },
    'error_code': 'fns_already_deleted',
}

SELFEMPLOYED_REQUEST_VALIDATION_ERROR = {
    'status_code': 400,
    'body': {
        'Code': 'REQUEST_VALIDATION_ERROR',
        'Message': 'request validation error',
    },
}

SELFEMPLOYED_TAXPAYER_UNBOUND = {
    'status_code': 400,
    'body': {
        'Code': 'TAXPAYER_UNBOUND',
        'Message': 'Партнер не привязан к налогоплательщику c ИНН',
    },
    'error_code': 'fns_taxpayer_unbound',
}

SELFEMPLOYED_INTERNAL_ERROR = {
    'status_code': 400,
    'body': {'Code': 'INTERNAL_ERROR', 'Message': 'internal_error'},
    'error_code': 'fns_internal_error',
}

SELFEMPLOYED_TAXPAYER_UNREGISTERED = {
    'status_code': 400,
    'body': {
        'Code': 'TAXPAYER_UNREGISTERED',
        'Message': 'taxipayer_unregistered',
    },
    'error_code': 'fns_taxpayer_unregistered',
}

SELFEMPLOYED_PARTNER_DENY = {
    'status_code': 400,
    'body': {'Code': 'PARTNER_DENY', 'Message': 'partner_deny'},
    'error_code': 'fns_partner_deny',
}

SELFEMPLOYED_PERMISSION_NOT_GRANTED = {
    'status_code': 400,
    'body': {
        'Code': 'PERMISSION_NOT_GRANTED',
        'Message': 'permission_not_granted',
    },
    'error_code': 'fns_permission_not_granted',
}

SELFEMPLOYED_RECEPT_ID_NOT_FOUND = {
    'status_code': 400,
    'body': {'Code': 'RECEPT_ID_NOT_FOUND', 'Message': 'recept_id_not_found'},
    'error_code': 'fns_recept_id_not_found',
}


class SelfemployedResponse:
    processing = SELFEMPLOYED_PROCESSING_RESPONSE
    duplicate = SELFEMPLOYED_DUPLICATE
    not_found = SELFEMPLOYED_NOT_FOUND
    already_deleted = SELFEMPLOYED_ALREADY_DELETED
    request_validation_error = SELFEMPLOYED_REQUEST_VALIDATION_ERROR
    taxpayer_unbound = SELFEMPLOYED_TAXPAYER_UNBOUND
    internal_error = SELFEMPLOYED_INTERNAL_ERROR
    taxpayer_unregistered = SELFEMPLOYED_TAXPAYER_UNREGISTERED
    partner_deny = SELFEMPLOYED_PARTNER_DENY
    permission_not_granted = SELFEMPLOYED_PERMISSION_NOT_GRANTED
    recept_id_not_found = SELFEMPLOYED_RECEPT_ID_NOT_FOUND


@pytest.fixture(name='selfemployed')
def mock_selfemployed(mockserver):
    class Context:
        def __init__(self):
            self.inn = None
            self.services = None
            self.message_id = None
            self.income_result_response = {'ProcessingStatus': 'PROCESSING'}
            self.income_result_status_code = 200
            self.response = SelfemployedResponse()

            self.default_message_id = REGISTER_MESSAGE_ID

            self.receipt_url = FNS_RECEIPT_URL
            self.receipt_id = FNS_RECEIPT_ID

            self.register_income_response = {'MessageId': REGISTER_MESSAGE_ID}
            self.revert_income_response = {'MessageId': REGISTER_MESSAGE_ID}

            self.refund_receipt_url = 'no-receipt-for-fns-refund'

        def times_register_income_called(self):
            return _mock_register_income.times_called

        def times_get_income_result_called(self):
            return _mock_get_income_result.times_called

        def times_revert_income_called(self):
            return _mock_revert_income.times_called

        def times_get_revert_result_called(self):
            return _mock_get_revert_income_result.times_called

        def check_register_income(self, inn, services):
            self.inn = inn
            self.services = services

        def set_register_income_response(self, message_id):
            self.register_income_response['MessageId'] = message_id

        def check_get_income_result(self, message_id):
            self.message_id = message_id

        def set_get_income_result_response(self, status_code=200, **kwargs):
            self.income_result_status_code = status_code
            self.income_result_response = kwargs

        def check_get_revert_income_result(self, message_id):
            self.message_id = message_id

        def set_get_revert_result_response(self, status_code=200, **kwargs):
            self.income_result_status_code = status_code
            self.income_result_response = kwargs

    context = Context()

    @mockserver.json_handler('/selfemployed/lavka/v1/send-register-income-msg')
    def _mock_register_income(request):
        if context.inn is not None:
            assert request.json['Inn'] == context.inn
        if context.services is not None:
            assert request.json['Services'] == context.services

        return context.register_income_response

    @mockserver.json_handler(
        '/selfemployed/lavka/v1/get-register-income-result',
    )
    def _mock_get_income_result(request):
        if context.message_id is not None:
            assert request.json['MessageId'] == context.message_id

        return mockserver.make_response(
            json.dumps(context.income_result_response),
            context.income_result_status_code,
        )

    @mockserver.json_handler('/selfemployed/lavka/v1/send-revert-income-msg')
    def _mock_revert_income(request):
        if context.inn is not None:
            assert request.json['Inn'] == context.inn
        if context.receipt_id is not None:
            assert request.json['ReceiptId'] == context.receipt_id

        return context.register_income_response

    @mockserver.json_handler('/selfemployed/lavka/v1/get-revert-income-result')
    def _mock_get_revert_income_result(request):
        if context.message_id is not None:
            assert request.json['MessageId'] == context.message_id

        return mockserver.make_response(
            json.dumps(context.income_result_response),
            context.income_result_status_code,
        )

    return context
