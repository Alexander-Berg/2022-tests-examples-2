import pytest


@pytest.fixture(name='social')
def _social(mockserver):
    class Context:
        def __init__(self):
            self.body = '{"status":"ok"}'
            self.code = 200
            self.need_to_verify = False
            self.expected_request = {}

        def verify(self, request):
            if self.need_to_verify:
                assert self.expected_request == request.args

    context = Context()

    @mockserver.handler('/social/api/unbind_phonish_by_uid')
    def _unbind_phonish_by_uid(request):
        context.verify(request)
        return mockserver.make_response(context.body, context.code)

    return context


async def test_simple(taxi_zalogin, social):
    social.need_to_verify = True
    social.expected_request = {
        'consumer': 'taxi-zalogin',
        'uid1': '1',
        'uid2': '2',
    }

    body = {'yandex_uid1': '1', 'yandex_uid2': '2'}

    response = await taxi_zalogin.post('admin/uid-unbind', body)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


async def test_errors(taxi_zalogin, social):
    body = {'yandex_uid1': '1', 'yandex_uid2': '2'}

    social.code = 500
    response = await taxi_zalogin.post('admin/uid-unbind', body)
    assert response.status_code == 500

    social.code = 400
    response = await taxi_zalogin.post('admin/uid-unbind', body)
    assert response.status_code == 500

    social.code = 200
    social.body = '{"status":"error","errors":["e1","e2"]}'
    response = await taxi_zalogin.post('admin/uid-unbind', body)
    assert response.status_code == 200
    assert response.json() == {'status': 'error', 'errors': ['e1', 'e2']}


async def test_full(taxi_zalogin, social):
    social.need_to_verify = True
    social.expected_request = {
        'consumer': 'taxi-zalogin',
        'uid1': '1',
        'uid2': '2',
        'delete_phone': '1',
        'logout_master': '1',
        'logout_phonish': '0',
    }

    body = {
        'yandex_uid1': '1',
        'yandex_uid2': '2',
        'unbind_phone_from_portal': True,
        'logout_portal': True,
        'logout_phonish': False,
    }

    response = await taxi_zalogin.post('admin/uid-unbind', body)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
