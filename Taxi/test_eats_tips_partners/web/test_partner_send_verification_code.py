import http

import pytest
from submodules.testsuite.testsuite.utils import http as testsuite_http

WORKING_IP = '1.2.3.4'
BAD_IP = 'cheater'


def _format_partner_send_verification_request(*, phone):
    return {'phone': phone}


def _format_headers(*, remote_ip):
    return {'X-Remote-Ip': remote_ip}


@pytest.mark.parametrize(
    ('headers', 'params', 'expected_code', 'expected_response'),
    (
        pytest.param(
            _format_headers(remote_ip=WORKING_IP),
            _format_partner_send_verification_request(phone='+79000000000'),
            http.HTTPStatus.OK,
            {'track_id': 'sms_track_id'},
            id='ok',
        ),
        pytest.param(
            _format_headers(remote_ip=BAD_IP),
            _format_partner_send_verification_request(phone='+79000000000'),
            http.HTTPStatus.BAD_REQUEST,
            {'code': 'bad_request', 'message': f'problems with partner phone'},
            id='bad-ip',
        ),
        pytest.param(
            _format_headers(remote_ip=WORKING_IP),
            _format_partner_send_verification_request(phone='+79999999999'),
            http.HTTPStatus.TOO_MANY_REQUESTS,
            {'code': 'too_many_tries', 'message': 'sms limit exceeded'},
            id='sms-limit-exceeded',
        ),
    ),
)
@pytest.mark.pgsql('eats_tips_partners', files=['pg.sql'])
async def test_partner_send_verification_code(
        taxi_eats_tips_partners_web,
        mock_tvm_rules,
        mockserver,
        headers,
        params,
        expected_code,
        expected_response,
):
    @mockserver.json_handler(
        '/passport-internal/1/bundle/phone/confirm/submit/',
    )
    async def _submit(request: testsuite_http.Request):
        if request.headers['Ya-Consumer-Client-Ip'] == BAD_IP:
            return {'status': 'error', 'errors': ['phone.blocked']}
        if request.form.get('number') == ' 79999999999':
            return {'status': 'error', 'errors': ['sms_limit.exceeded']}
        assert request.form == {
            'number': ' 79000000000',
            'display_language': 'ru',
        }
        assert request.headers['Ya-Consumer-Client-Ip'] == WORKING_IP
        return {'status': 'ok', 'track_id': 'sms_track_id'}

    @mockserver.json_handler('/territories/v1/countries/list')
    async def _mock_client_territories(request: testsuite_http.Request):
        return {
            'countries': [
                {
                    '_id': 'rus',
                    'national_access_code': '8',
                    'phone_code': '7',
                    'phone_max_length': 11,
                    'phone_min_length': 11,
                },
            ],
        }

    response = await taxi_eats_tips_partners_web.post(
        '/v1/partner/send-verification-code', json=params, headers=headers,
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
