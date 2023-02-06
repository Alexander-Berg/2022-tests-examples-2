import pytest


DEFAULT_EATER_ID = 'default-eater-id'


@pytest.fixture(name='eats_core_eater')
def mock_eats_core_eater(mockserver):
    class Context:
        def __init__(self):
            self.eats_user_id = DEFAULT_EATER_ID
            self.personal_phone_id = None
            self.personal_email_id = None
            self.check_request_flag = None

        def set_personal_email_id(self, personal_email_id):
            self.personal_email_id = personal_email_id

        def check_request(self, eats_user_id=None, personal_phone_id=None):
            self.personal_phone_id = personal_phone_id
            self.eats_user_id = eats_user_id
            self.check_request_flag = True

        def times_find_by_id_called(self):
            return mock_find_by_id.times_called

        def flush(self):
            mock_find_by_id.flush()

    context = Context()

    @mockserver.json_handler('eats-core-eater/find-by-id')
    def mock_find_by_id(request):
        if context.check_request_flag:
            assert request.json['id'] == context.eats_user_id
        return {
            'eater': {
                'id': context.eats_user_id,
                'uuid': '123546',
                'personal_phone_id': context.personal_phone_id,
                'personal_email_id': context.personal_email_id,
                'created_at': '2020-06-23T17:20:00+03:00',
                'updated_at': '2020-06-23T17:20:00+03:00',
            },
        }

    return context
