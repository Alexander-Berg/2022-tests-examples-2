import pytest


@pytest.fixture(name='personal', autouse=True)
def mock_personal(mockserver):
    class Context:
        def __init__(self):
            self.personal_phone_id = None
            self.phone = None
            self.error_code = None
            self.check_request_flag = None
            self.tin = None
            self.personal_tin_id = None
            self.email = None
            self.email_id = None

        def check_request(
                self,
                personal_phone_id=None,
                phone=None,
                error_code=None,
                tin=None,
                personal_tin_id=None,
                email_id=None,
                email=None,
        ):
            self.personal_phone_id = personal_phone_id
            self.phone = phone
            self.error_code = error_code
            self.check_request_flag = True
            self.tin = tin
            self.personal_tin_id = personal_tin_id
            self.email_id = email_id
            self.email = email

        def times_phones_retrieve_called(self):
            return mock_phones_retrieve.times_called

        def times_phones_store_called(self):
            return mock_phones_store.times_called

        def times_tins_store_called(self):
            return mock_tins_store.times_called

        def times_tins_retrieve_called(self):
            return mock_tins_retrieve.times_called

        def times_tins_find_called(self):
            return mock_tins_find.times_called

        def times_emails_store_called(self):
            return mock_emails_store.times_called

        def times_emails_retrieve_called(self):
            return mock_emails_retrieve.times_called

        def flush(self):
            mock_phones_retrieve.flush()

    context = Context()

    @mockserver.json_handler('personal/v1/phones/retrieve')
    def mock_phones_retrieve(request):
        if context.check_request_flag:
            assert request.json['id'] == context.personal_phone_id
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        if context.phone and context.personal_phone_id:
            return {'value': context.phone, 'id': context.personal_phone_id}
        return {'value': '+79991012345', 'id': request.json['id']}

    @mockserver.json_handler('personal/v1/phones/store')
    def mock_phones_store(request):
        if context.check_request_flag:
            assert request.json['value'] == context.phone
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        return {'value': context.phone, 'id': context.personal_phone_id}

    @mockserver.json_handler('personal/v1/tins/store')
    def mock_tins_store(request):
        if context.check_request_flag:
            assert request.json['value'] == context.tin
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        if context.tin and context.personal_tin_id:
            return {'value': context.tin, 'id': context.personal_tin_id}
        context.tin = request.json['value']
        context.personal_tin_id = 'tin_id_123'
        return {'value': context.tin, 'id': context.personal_tin_id}

    @mockserver.json_handler('personal/v1/tins/retrieve')
    def mock_tins_retrieve(request):
        if context.check_request_flag:
            assert request.json['id'] == context.personal_tin_id
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        if context.tin and context.personal_tin_id:
            return {'value': context.tin, 'id': context.personal_tin_id}
        return {'value': '7707083893', 'id': request.json['id']}

    @mockserver.json_handler('personal/v1/tins/find')
    def mock_tins_find(request):
        if context.check_request_flag:
            assert request.json['value'] == context.tin
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        if context.tin and context.personal_tin_id:
            return {'value': context.tin, 'id': context.personal_tin_id}
        return {'value': '7707083893', 'id': 'not_founded_id'}

    @mockserver.json_handler('/personal/v1/emails/store')
    def mock_emails_store(request):
        if context.check_request_flag:
            assert request.json['value'] == context.email
        if context.error_code:
            return mockserver.make_response(
                json={'code': 'error_code', 'message': 'error_message'},
                status=context.error_code,
            )
        if context.email and context.email_id:
            return {'value': context.email, 'id': context.email_id}
        context.email = request.json['value']
        context.email_id = 'personal_email_id'
        return {'value': context.email, 'id': context.email_id}

    @mockserver.json_handler('personal/v1/emails/retrieve')
    def mock_emails_retrieve(request):
        if context.check_request_flag:
            assert request.json['id'] == context.email_id
        if context.error_code:
            return mockserver.make_response('', context.error_code)
        if context.email and context.email_id:
            return {'value': context.email, 'id': context.email_id}
        return {'value': 'super_mail@yandex.ru', 'id': request.json['id']}

    return context
