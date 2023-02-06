import itertools
import json
import urllib

import pytest


@pytest.fixture(name='user_api')
def _user_api(mockserver):
    class Context:
        def __init__(self):
            self.body = {
                'stat': {
                    'big_first_discounts': 0,
                    'complete': 0,
                    'complete_card': 0,
                    'complete_apple': 0,
                    'complete_google': 0,
                    'fake': 0,
                    'total': 0,
                },
                'is_loyal': True,
                'is_yandex_staff': True,
                'is_taxi_staff': True,
                'phone': '+1111111',
                'type': 'yandex',
            }

    context = Context()

    @mockserver.handler('/user-api/user_phones/get')
    def _get_user_phones(request):
        body = context.body.copy()
        body['personal_phone_id'] = 'personal_' + request.json['id']
        body['id'] = request.json['id']

        return mockserver.make_response(json.dumps(body), 200)

    return context


@pytest.fixture(name='blackbox')
def _blackbox_api(mockserver):
    class Context:
        def __init__(self):
            self.body = {
                'users': [
                    {
                        'id': '1130000002997135',
                        'uid': {
                            'value': '1130000002997135',
                            'lite': False,
                            'hosted': True,
                            'domid': '1088883',
                            'domain': 'test-pdd-domain-1.ru',
                            'mx': '0',
                            'domain_ena': '1',
                            'catch_all': False,
                        },
                        'login': 'yndx-02376184@test-pdd-domain-1.ru',
                        'have_password': True,
                        'have_hint': True,
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'attributes': {},
                    },
                ],
            }

    context = Context()

    @mockserver.handler('/blackbox')
    def _mock_blackbox(request):
        query_params = dict(
            itertools.chain(
                urllib.parse.parse_qsl(request.query_string.decode()),
                request.form.items(),
            ),
        )
        body = context.body.copy()
        body['users'][0]['id'] = query_params['uid']
        body['users'][0]['uid']['value'] = query_params['uid']
        return mockserver.make_response(json.dumps(body), 200)

    return context


async def request_and_check(taxi_zalogin, uid, code=200):
    params = {'yandex_uid': uid}
    response = await taxi_zalogin.get('admin/uid-info', params=params)
    assert response.status_code == code
    return response.json()


async def test_errors(taxi_zalogin, user_api, mockserver):
    await request_and_check(taxi_zalogin, 'not_found', code=409)
    await request_and_check(taxi_zalogin, '1113', 500)

    @mockserver.handler('/blackbox')
    def _mock_blackbox(request):
        return mockserver.make_response(json.dumps({}), 200)

    await request_and_check(taxi_zalogin, '1111', code=409)


async def test_simple(taxi_zalogin, user_api, blackbox):
    body = await request_and_check(taxi_zalogin, '1111')

    assert body['type'] == 'phonish'
    assert body['yandex_uid'] == '1111'
    assert body['allow_reset_password'] is False
    assert body['has_2fa_on'] is False
    bound_ids = body['bound_phone_ids']
    assert len(bound_ids) == 1
    assert bound_ids[0]['phone_id'] == '594baaba0000070000040001'
    assert (
        bound_ids[0]['personal_phone_id']
        == 'personal_594baaba0000070000040001'
    )


async def test_phonish_bound_to(taxi_zalogin, user_api, blackbox):
    body = await request_and_check(taxi_zalogin, '1112')

    assert body['type'] == 'phonish'
    assert body['bound_to'] == '1000'


async def test_portal_simple(taxi_zalogin, user_api, blackbox):
    body = await request_and_check(taxi_zalogin, '1114')

    assert body['type'] == 'portal'


async def test_portal_complicated(taxi_zalogin, user_api, blackbox):
    body = await request_and_check(taxi_zalogin, '1115')

    assert body['type'] == 'portal'
    assert len(body['bound_phonishes']) == 4
    assert len(body['bound_phone_ids']) == 2


@pytest.mark.parametrize(
    'uid, portal_type',
    [
        (1114, 'portal'),
        (1120, 'lite'),
        (7777, 'social'),
        (1177, 'pdd'),
        (1115, 'neophonish'),
        (1111, None),
    ],
)
async def test_portal_types(
        taxi_zalogin, user_api, blackbox, uid, portal_type,
):
    body = await request_and_check(taxi_zalogin, uid)

    if portal_type is None:
        assert 'portal_type' not in body
    else:
        assert body['portal_type'] == portal_type


@pytest.mark.parametrize('have_password', [True, False])
@pytest.mark.parametrize('has_2fa', [True, False])
async def test_allow_password_reset(
        taxi_zalogin, user_api, blackbox, have_password, has_2fa,
):
    if have_password:
        blackbox.body['users'][0]['attributes']['1005'] = '1'
    if has_2fa:
        blackbox.body['users'][0]['attributes']['1003'] = '1'
    body = await request_and_check(taxi_zalogin, '1111')
    assert body['allow_reset_password'] == (
        (have_password is True) and (has_2fa is False)
    )


@pytest.mark.parametrize('has_sms_2fa', [True, False])
async def test_has_sms_2fa(taxi_zalogin, user_api, blackbox, has_sms_2fa):
    if has_sms_2fa:
        blackbox.body['users'][0]['attributes']['200'] = '1'
    body = await request_and_check(taxi_zalogin, '1111')
    assert body['sms_2fa_status'] == has_sms_2fa
