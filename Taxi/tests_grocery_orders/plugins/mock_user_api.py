import pytest


@pytest.fixture(name='user_api', autouse=True)
def mock_user_api(mockserver):
    class Context:
        def __init__(self):
            self.personal_phone_id = None
            self.number_type = None
            self.phone_id = None
            self.error_code = None
            self.check_request_flag = False

        def set_error_code(self, code):
            self.error_code = code

        def set_phone_id(self, phone_id):
            self.phone_id = phone_id

        def set_check_request(self, check_request):
            self.check_request_flag = check_request

        def check_request(
                self,
                *,
                number_type='yandex',
                personal_phone_id=None,
                check_request_flag=False,
        ):
            self.number_type = number_type
            self.personal_phone_id = personal_phone_id
            self.check_request_flag = check_request_flag

        def mock_retrieve_times_called(self):
            return mock_user_api_retrieve.times_called

        def flush(self):
            mock_user_api.flush()

    context = Context()

    @mockserver.json_handler('/user-api/user_phones/by_personal/retrieve')
    def mock_user_api_retrieve(request):
        if context.check_request_flag:
            assert context.number_type == context.number_type
            assert context.personal_phone_id == context.personal_phone_id

        if context.error_code:
            return mockserver.make_response(
                json={'message': '', 'code': str(context.error_code)},
                status=context.error_code,
            )

        return {
            'id': context.phone_id,
            'type': context.number_type,
            'is_loyal': False,
            'is_yandex_staff': True,
            'is_taxi_staff': True,
            'phone': '88005553535',
            'stat': {
                'big_first_discounts': 1,
                'complete': 1,
                'complete_card': 1,
                'complete_apple': 0,
                'complete_google': 1,
                'fake': 0,
                'total': 12,
            },
        }

    return context
