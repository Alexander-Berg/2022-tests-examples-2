import datetime
import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from bank_access_control_plugins.generated_tests import *


@pytest.fixture(autouse=True)
def init_fixture(jwks_content):
    jwks_content.set_data(
        [
            {
                'kty': 'RSA',
                'n': 'u1SU1LfVLPHCozMxH2Mo4lgOEePzNm0tRgeLezV6ffAt0gunVTLw7onLRnrq0_IzW7yWR7QkrmBL7jTKEn5u-qKhbwKfBstIs-bMY2Zkp18gnTxKLxoS2tFczGkPLPgizskuemMghRniWaoLcyehkd3qqGElvW_VDL5AaWTg0nLVkjRo9z-40RQzuVaE8AkAFmxZzow3x-VJYKdjykkJ0iT9wCS0DRTXu269V264Vf_3jvredZiKRkgwlL9xNAwxXFg0x_XFw005UWVRIkdgcKWTjpBP2dPwVZ4WWC-9aGVd-Gyn1o0CLelf4rEjGoXbAAEgAqeGUxrcIlbjXfbcmw',
                'e': 'AQAB',
                'alg': 'RS256',
            },
            {
                'kty': 'EC',
                'x': 'WcvDFh6ghcjNODTCvvXIU7oUjiyFlfIQBOEzbTtSL_c',
                'y': 'qdw-EC0OZp1gmH8Pd9yiM3lTkEbnp0p3nLj3seir0oM',
                'crv': 'P-256',
            },
            {
                'kty': 'EC',
                'x': 'HwQhJzwciQlm7DQO3eHBfRSlAEMW9QDdSWQLWJXwzF7V70ht5peFZzpMnWzGDMHQ',
                'y': 'wb6_ncKgK_PJ0-dhLWcrcqYomGlvkvO7YJDqhnRqr7LGCz5zhrk1W4mJdBH4yKLp',
                'crv': 'P-384',
            },
            {
                'kty': 'EC',
                'x': 'AHhis5Pp6SklS1F7gPMjASPQM4hHG0gmw4WMS1aao_p7rT0S4KfqqC7czp64ZAISp2kJf2eKdpDJKfvvI5gr9II9',
                'y': 'AFpQhbA-qoTS7gf0KkfgadELrQPKANteEqZU9_JRYvWAkuisDPHoKSW-X9FaO83aZfHvfM5Rm-T5bLVAtn6ZlBhr',
                'crv': 'P-521',
            },
            {'kty': 'RSA', 'n': 'AQAB', 'e': 'AQAB', 'alg': 'RS256'},
        ],
    )


def make_idm_response(*args):
    roles = []
    for idx, status in zip(range(len(args)), args):
        role = None
        if status is not None:
            role = dict(role_id=idx, rolenode_id=idx, role_status=status)
        roles.append(dict(role=role))
    return dict(roles=roles)


# Feel free to provide your custom implementation to override generated tests.
async def test_apply_policies_without_jwt(taxi_bank_access_control):
    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={'subject_attributes': {}, 'resource_attributes': {}},
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'NOT_APPLICABLE'


async def test_apply_policies_simple(taxi_bank_access_control, mockserver):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSJ9.fUBxgcAVpct2o6Xk1FjPDiKNFLtBEFIRAGBjG-6ue93F9ODA7cKyFDpUQvgOt1MSnUIJy4wS5e2ZFqftN4RmVuC19Ws-ohUDcB8uBMmlB5Nbu-2jEfqFIed9X3RGFcoI7LelYVI0IZ8lHwNjs7_0oG-emNS4U_9-fOYavvJ_4NhOyzcXfTCLWvNMdkeCIrOx5Y6L8Hl_5JBnLKvboRVlN7YJ7EiY0M3LwQD_Mhu_clRqL-LRiWyV10e-l1wMIvAxOgSadjE-5294Mm1vzGObKLwOU704uNuke0F6FGRdpfzVj_ztO6NbvWvVhweqmLbVbbg9lpoRQRBSoGHqDlqD9w',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'PERMIT'
    assert response['user_login'] == 'alice'


@pytest.mark.parametrize(
    'jwt',
    [
        'eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSJ9.'
        'A-pNZh3NbP46jHfPVHcTOYOYiL6TEzHhz0d8o6mPrzswTpIqN6olN0ysZ5FfsYtds0002T2hcTbLcd'
        'bifDTXPg',  # ES256
        'eyJhbGciOiJFUzM4NCIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSJ9.'
        '2rXzBQEz38qqz0RxN-5KgJUjv_isWMhWp3oFzHAjEs8E5oIs08PwuaOqZ5n79om56RlLQDbvSYU-eM'
        'bJmH5ZZLv5A-8iBPMexaQ3DvVAamlREgFiHltWHlLdjfZvg6vY',  # ES384
        'eyJhbGciOiJFUzUxMiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSJ9.'
        'ALGIqMmdHtlEEA5tZqqe0iyVsLzoeuTLFnh26QVFGF9SrZJsgYSQ_PAvylgbfmcgvx9Yv2J82WCeG8'
        'HRoX1-EcSAAVs8Cjq6wkqz_p7VFfW1z6cq24jgaOzUko0aBmw0NTZE4rrCNCARCYQQRbY8TSTtVSSQ'
        'rekKwjBHO_hjyYZhDNNJ',  # ES512
    ],
)
async def test_apply_policies_ecdsa(
        taxi_bank_access_control, bank_audit, mockserver, jwt,
):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {'jwt': jwt},
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'PERMIT'
    assert response['user_login'] == 'alice@yandex-team.ru'


# Its 2022-04-01 14:35:10 in JWT's exp
@pytest.mark.parametrize(
    'now, expected_decision',
    [
        (
            datetime.datetime.strptime(
                '2022-04-01 14:35:09', '%Y-%m-%d %H:%M:%S',
            ),
            'PERMIT',
        ),
        (
            datetime.datetime.strptime(
                '2022-04-01 14:35:11', '%Y-%m-%d %H:%M:%S',
            ),
            'DENY',
        ),
    ],
)
async def test_apply_policies_simple_expired(
        taxi_bank_access_control,
        bank_audit,
        mockserver,
        mocked_time,
        now,
        expected_decision,
):
    mocked_time.set(now)
    await taxi_bank_access_control.invalidate_caches()

    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSIsImV4cCI6MTY0ODgyMzcxMH0.BTcCyngelZB_IwxM_d0jAT191zkTYzJeaYGY6vGn4WS8GwKNv-oh6rT9I0oevexnStkqLkxgoaPOFJrIT1SzM9sdCntpZfZJ6ecIniLQYJGeLmOycWTPA_Gi3vSm0B5_4FK_6nkQmvcuG7PTjaqOYJ8et_688fOp_ChyaneOPHIugBTy0ymqDKsUUyxmy4SHN_m0wIEj0TYQ5t-dUZECygqRBgBU8Yiw9uJ6hrhjzsnEw3VzY2732SxOdNrAxn6Ar4TAVWlNCj0Cu5emaEGTS7PDvA_ev38aPzq4-_vB4I8eZdHtVi1cVMU7hpxsQjXZXnoAkDZBex6BxZ2PUQvfgw',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == expected_decision
    if expected_decision == 'PERMIT':
        assert response['user_login'] == 'alice@yandex-team.ru'


# Its 2022-04-01 14:35:10 in JWT's exp
@pytest.mark.parametrize(
    'now, expected_decision',
    [
        (
            datetime.datetime.strptime(
                '2022-04-01 14:35:09', '%Y-%m-%d %H:%M:%S',
            ),
            'DENY',
        ),
        (
            datetime.datetime.strptime(
                '2022-04-01 14:35:11', '%Y-%m-%d %H:%M:%S',
            ),
            'PERMIT',
        ),
    ],
)
async def test_apply_policies_simple_nbf(
        taxi_bank_access_control,
        bank_audit,
        mockserver,
        mocked_time,
        now,
        expected_decision,
):
    mocked_time.set(now)
    await taxi_bank_access_control.invalidate_caches()

    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSIsIm5iZiI6MTY0ODgyMzcxMH0.SiflDu1fzB8EU7PejlCH0ifAMgoAhte_JvtPh_CkKEvnGScoFA1OEjoAvgJVKRY5eIbSmKmEkirsGW_P272m-bSgHKH_y-_lXb8ey6sqh_Y9289S1jIq20NXLzaxaR80AVonJRK4eD-lj63viXmGiWtbJOWRlPTQQL2-xzt8-jhIkpUQbWZthH91HPwx79hgt_FV-WphT0PoJ0Z4goC9Oes7FIRKLb_MYIVosy1aOnYYgueTe5TKgQy8kEvicXZ2vyDo-P856ExIDguQEoyiUpvrXXPmV9xOps27vMSXXeOEXls1Ej49XpTKdbJf1h_QowQM2cyYBZsiSTDw06AbGA',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == expected_decision
    if expected_decision == 'PERMIT':
        assert response['user_login'] == 'alice@yandex-team.ru'


async def test_apply_policies_simple_with_yandex_team_email(
        taxi_bank_access_control, mockserver,
):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        assert '@yandex-team.ru' not in request.json['user_login']
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSJ9.tOPK_kqng6pAmrYdCCmIxrvS2iOnbii1DlN-69m676n0QeoBte0ekCo0WP66iZ02xg2dvnvYVk1S-q4JQrnO9M6FF5e3MC2OMiD6tI4RV54vpMKfiXn99Dibf1GxdEZ3ldS2H8h4rCl9ZOxtpRlWsnSQB08tpow6iVU64V9nTUQBnR7_Cqxhoq-1Buclg1UIvXDUdmM9MNfY1kdUHO3ZkqzqYZhJBCT5bPLwkWU0BVWWNA3BV3ZExWVdGEf96MBJWCSHJqK0paGPH1uNFLJ9NgnL4wm-pT9Lw6y2ETuxMHTrDIwLuEnIDlKipaf6d-yMmnt1YDcU3eSmVHYFIV0KfA',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'PERMIT'
    assert response['user_login'] == 'alice@yandex-team.ru'


async def test_apply_policies_simple_with_other_email(
        taxi_bank_access_control, mockserver,
):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        if '@' in request.json['user_login']:
            return mockserver.make_response(status=500)
        return mockserver.make_response(json=make_idm_response('granted'))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUBxd2UucnUifQ.QXaYfMAbIo7J6T9Fi_ZsfVnJoPVTaOu8oAjzW2ZrxKBavSyaHFZjs6Geo4evB9krqU-rbZ_zxaBCR9HEN05IZQAFW7BEn5W-SCCWcBb07bupgOdgnoecRGIk3PvETAHioS3HPXmFVCjfir02FEjnM_INNgWOskssplbRFwX3BOj0Fcm4-IlXBt9v5l7cCN0eyHqwhHGdTtsNoTWUlRGsHX5Ie87BuhXwIwqTkm-XoYT0MzM28SqxLJGgq8J89mrtnvspIDt9PicsJWS04lYGIE15rHhpF_dz2jCuWuuX-hz7cOanDDZXndvcxrI7QDHtrm3dC-JDBu-0j03mkXtXBg',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 500


async def test_apply_policies_simple_deny(
        taxi_bank_access_control, mockserver,
):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(json=make_idm_response(None))

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZSJ9.fUBxgcAVpct2o6Xk1FjPDiKNFLtBEFIRAGBjG-6ue93F9ODA7cKyFDpUQvgOt1MSnUIJy4wS5e2ZFqftN4RmVuC19Ws-ohUDcB8uBMmlB5Nbu-2jEfqFIed9X3RGFcoI7LelYVI0IZ8lHwNjs7_0oG-emNS4U_9-fOYavvJ_4NhOyzcXfTCLWvNMdkeCIrOx5Y6L8Hl_5JBnLKvboRVlN7YJ7EiY0M3LwQD_Mhu_clRqL-LRiWyV10e-l1wMIvAxOgSadjE-5294Mm1vzGObKLwOU704uNuke0F6FGRdpfzVj_ztO6NbvWvVhweqmLbVbbg9lpoRQRBSoGHqDlqD9w',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'DENY'


async def test_apply_policies_idm_404(taxi_bank_access_control, mockserver):
    @mockserver.json_handler('/bank-idm/v1/get-user-roles')
    def _handler(request):
        return mockserver.make_response(
            status=404,
            json={'code': 'NotFound', 'message': 'user_id not found'},
        )

    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {
                'jwt': 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhbGljZUB5YW5kZXgtdGVhbS5ydSJ9.tOPK_kqng6pAmrYdCCmIxrvS2iOnbii1DlN-69m676n0QeoBte0ekCo0WP66iZ02xg2dvnvYVk1S-q4JQrnO9M6FF5e3MC2OMiD6tI4RV54vpMKfiXn99Dibf1GxdEZ3ldS2H8h4rCl9ZOxtpRlWsnSQB08tpow6iVU64V9nTUQBnR7_Cqxhoq-1Buclg1UIvXDUdmM9MNfY1kdUHO3ZkqzqYZhJBCT5bPLwkWU0BVWWNA3BV3ZExWVdGEf96MBJWCSHJqK0paGPH1uNFLJ9NgnL4wm-pT9Lw6y2ETuxMHTrDIwLuEnIDlKipaf6d-yMmnt1YDcU3eSmVHYFIV0KfA',
            },
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'NOT_APPLICABLE'


@pytest.mark.parametrize('token', ['', '..', 'e30.e30.e30'])
async def test_jwt_parse_error(taxi_bank_access_control, mockserver, token):
    response = await taxi_bank_access_control.post(
        '/access-control-internal/v1/apply-policies',
        json={
            'subject_attributes': {'jwt': token},
            'resource_attributes': {
                'handler_path': '/v1/support/manager-role',
            },
        },
    )
    assert response.status_code == 200
    response = response.json()
    assert response['decision'] == 'NOT_APPLICABLE'
