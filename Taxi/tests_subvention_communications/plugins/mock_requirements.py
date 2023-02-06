import pytest


@pytest.fixture(name='clients', autouse=True)
def mock_requirements(mockserver):
    class Context:
        def __init__(self):
            self.driver_wall_add = {}
            self.driver_bulk_push = {}
            self.client_notify = {}
            self.send_sms = {}
            self.send_sms_error_code = {}
            self.docs_by_id = {}
            self.rules_select = {}
            self.check_fraud_reason = {}
            self.docs = []
            self.rules = []

        def add_doc(self, doc):
            self.docs.append(doc)

        def add_rule(self, rule):
            self.rules.append(rule)

        def set_send_sms_error_code(self, error_code):
            self.send_sms_error_code = error_code

        @staticmethod
        def fraud_reason_tanker_info():
            return {
                'keyset': 'taximeter_messages',
                'key': 'fraud_reason_1',
                'params': {
                    'check_reason_param_name': 'check_reason_param_value',
                },
            }

    context = Context()

    @mockserver.json_handler('driver-wall/internal/driver-wall/v1/add')
    def _driver_wall_add(request):
        return {'id': request.json['id']}

    @mockserver.json_handler('/communications/driver/notification/bulk-push')
    def _driver_push(request):
        return {}

    @mockserver.json_handler('/ucommunications/driver/sms/send')
    def _send_sms(request):
        if context.send_sms_error_code:
            return mockserver.make_response(
                status=context.send_sms_error_code,
                json={
                    'message': 'An error',
                    'code': str(context.send_sms_error_code),
                    'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
                    'status': 'error',
                },
            )
        return {
            'message': 'OK',
            'code': '200',
            'message_id': 'f13bb985ce7549b181061ed3e6ad1286',
            'status': 'sent',
        }

    @mockserver.json_handler('client-notify/v2/push')
    def _client_notify_v2_push(request):
        return {'notification_id': 'mock_notification_id'}

    @mockserver.json_handler('/billing-reports/v1/docs/by_id')
    def _mock_docs_by_id(request):
        return {'docs': context.docs}

    @mockserver.json_handler('/billing_subventions/v1/rules/select')
    async def _rules_select(request):
        assert 'rule_ids' in request.json
        rules = [
            rule
            for rule in context.rules
            if rule['subvention_rule_id'] == request.json['rule_ids'][0]
        ]
        return {'subventions': rules}

    @mockserver.json_handler('/antifraud/v1/description/check_reason')
    async def _check_fraud_reason(request):
        return {'message': Context.fraud_reason_tanker_info()}

    context.send_sms = _send_sms
    context.driver_wall_add = _driver_wall_add
    context.driver_bulk_push = _driver_push
    context.client_notify = _client_notify_v2_push
    context.docs_by_id = _mock_docs_by_id
    context.rules_select = _rules_select
    context.check_fraud_reason = _check_fraud_reason

    return context
