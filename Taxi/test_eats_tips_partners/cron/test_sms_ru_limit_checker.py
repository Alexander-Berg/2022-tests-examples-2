import pytest


def _format_sms_ru_response(
        *, used_today=500, status_code=100, status='OK', total_limit='1000',
):
    return {
        'status': status,
        'status_code': status_code,
        'total_limit': total_limit,
        'used_today': used_today,
    }


def _format_solomon_request(
        *, application='eats_tips_partners_cron', used_today=500, limit=1000,
):
    return {
        'sensors': [
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': application,
                    'sensor': 'sms_ru_limit_checker_sms_today',
                },
                'value': used_today,
            },
            {
                'kind': 'IGAUGE',
                'labels': {
                    'application': application,
                    'sensor': 'sms_ru_limit_checker_limit',
                },
                'value': limit,
            },
        ],
        'ts': 1577836800,
    }


@pytest.mark.parametrize(
    ('sms_response', 'solomon_expected_request', 'expected_exception'),
    (
        pytest.param(
            _format_sms_ru_response(),
            _format_solomon_request(used_today=500, limit=1000),
            {},
            id='ok',
        ),
        pytest.param(
            _format_sms_ru_response(status='SERVER ERROR', status_code=500),
            _format_solomon_request(used_today=500, limit=1000),
            {RuntimeError},
            id='error',
        ),
        pytest.param(
            _format_sms_ru_response(used_today=1000),
            _format_solomon_request(used_today=1000, limit=1000),
            {},
            id='max used',
        ),
        pytest.param(
            _format_sms_ru_response(used_today='1000'),
            _format_solomon_request(used_today=1000, limit=1000),
            {},
            id='string-used_today',
        ),
    ),
)
@pytest.mark.now('2020-01-01T00:00:00')
async def test_sms_ru_limit_checker(
        load_json,
        cron_runner,
        mock_limits,
        mock_solomon,
        sms_response,
        solomon_expected_request,
        expected_exception,
):
    # sms_response = load_json('sms-ru_response.json')
    limits_mock = mock_limits(sms_response)
    solomon_mock = mock_solomon()

    try:
        await cron_runner.sms_ru_limit_checker()
        assert limits_mock.has_calls
        assert solomon_mock.has_calls
        assert (
            solomon_mock.next_call()['request'].json
            == solomon_expected_request
        )
    except RuntimeError:
        if sms_response['status'] == 'OK':
            assert 0
