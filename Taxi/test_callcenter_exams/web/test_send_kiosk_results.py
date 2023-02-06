import ast

import aiohttp
import pytest

from test_callcenter_exams import conftest

HANDLE_URL = '/cc/v1/callcenter-exams/flow/v1/send_kiosk_results'


@pytest.mark.now('2021-05-16T05:05:57.253Z')
@conftest.main_configuration
@pytest.mark.parametrize(
    ['session_id', 'user_name', 'ticket_id', 'expected_result'],
    [
        ('ec5b2c7b-a57f-4765-a633-f12939ed7a1a', None, 'EXAM-123', 'success'),
        ('774dd8d4-3196-4384-9ad2-f5726b0e3ab4', None, 'EXAM-123', 'fail'),
        ('1d6c4bf8-95ad-4886-a50d-5594a84c31df', 'Uasya', 'EXAM-123', None),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_send_kiosk_results(
        web_app_client,
        patch,
        mock_startrack,
        mock_kiosk,
        session_id,
        user_name,
        ticket_id,
        expected_result,
        load,
        pgsql,
        mock_startrack_update_ticket,
):
    email_sent = False

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(body, **kwargs):
        nonlocal email_sent
        email_sent = True
        no_fio_suffix = '_no_fio' if not user_name else ''
        expected_body = (
            load(f'mail_{expected_result}{no_fio_suffix}.html')
            .strip('\n')
            .replace('$session_id$', session_id)
        )
        assert body.body == expected_body

    response = await web_app_client.post(
        HANDLE_URL,
        json={
            'user_name': user_name,
            'external_id': ticket_id,
            'session_id': session_id,
        },
        headers=conftest.pasport_headers('user_1'),
    )

    assert mock_kiosk.programs.times_called == 1
    startrack_calls = mock_startrack.calls

    if expected_result:
        assert response.status == 200
        assert email_sent
        if ticket_id:
            no_fio_suffix = '_no_fio' if not user_name else ''
            expected_text = (
                load(f'startrack_comment_{expected_result}{no_fio_suffix}')
                .strip('\n')
                .replace('$session_id$', session_id)
            )
            calls = mock_startrack_update_ticket.calls
            assert len(calls) == 1
            assert calls[0]['kwargs']['json']['comment'] == expected_text
        else:
            assert not startrack_calls
            assert not mock_startrack_update_ticket.calls
    else:
        assert response.status == 500
        assert not startrack_calls
        assert not email_sent


@pytest.mark.now('2021-05-16T05:05:57.253Z')
@conftest.main_configuration
@pytest.mark.parametrize(
    ['ticket_id', 'group', 'expected_status'],
    [
        ('EXAM-123', 'v', 200),
        ('exam-123', 'v', 400),
        ('EXAM', 'v', 400),
        ('EXAM-123 ', 'v', 400),
        ('blablabla', 'v', 400),
        ('EXAM-123', '1234aaAA._-', 200),
        ('EXAM-123', 'группа', 400),
        ('EXAM-123', 'v vezet', 400),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_validation(
        web_app_client,
        mock_kiosk,
        mock_startrack,
        mock_sticker_send,
        ticket_id,
        group,
        expected_status,
        mock_startrack_update_ticket,
):
    body = {
        'group': group,
        'external_id': 'EXAM-123',
        'session_id': 'b3a2427d-ce78-4bd4-b62e-1b1500b14cc5',
    }
    if ticket_id:
        body['external_id'] = ticket_id
    response = await web_app_client.post(
        HANDLE_URL, json=body, headers=conftest.pasport_headers('user_1'),
    )

    assert response.status == expected_status


@pytest.mark.now('2021-05-16T05:05:57.253Z')
@conftest.main_configuration
@pytest.mark.parametrize(
    ['session_id', 'user_name', 'ticket_id', 'expected_result'],
    [('ec5b2c7b-a57f-4765-a633-f12939ed7a1a', None, 'EXAM-123', 'success')],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_send_kiosk_results_bad_sessions(
        web_app_client,
        patch,
        mock_startrack,
        mock_kiosk,
        mockserver,
        session_id,
        user_name,
        ticket_id,
        expected_result,
        load,
        pgsql,
        mock_startrack_update_ticket,
):
    email_sent = False

    @mockserver.json_handler(
        '/kiosk/api/v1/sessions/ec5b2c7b-a57f-4765-a633-f12939ed7a1a',
    )
    async def _handle_sessions(request):
        return aiohttp.web.Response(status=500)

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(body, **kwargs):
        nonlocal email_sent
        email_sent = True
        no_fio_suffix = '_no_fio' if not user_name else ''
        expected_body = (
            load(f'mail_{expected_result}{no_fio_suffix}.html')
            .strip('\n')
            .replace('$session_id$', session_id)
        )
        assert body.body == expected_body

    response = await web_app_client.post(
        HANDLE_URL,
        json={
            'user_name': user_name,
            'external_id': ticket_id,
            'session_id': session_id,
        },
        headers=conftest.pasport_headers('user_1'),
    )

    assert mock_kiosk.programs.times_called == 1
    startrack_calls = mock_startrack.calls

    if expected_result:
        assert response.status == 200
        assert email_sent
        if ticket_id:
            assert not mock_startrack_update_ticket.calls
            no_fio_suffix = '_no_fio' if not user_name else ''
            expected_text = (
                load(
                    f'startrack_comment_{expected_result}{no_fio_suffix}_bad_sessions',  # noqa: E501
                )
                .strip('\n')
                .replace('$session_id$', session_id)
            )
            assert len(startrack_calls) == 1
            assert (
                startrack_calls[0]['kwargs']['json']['text'] == expected_text
            )
        else:
            assert not startrack_calls
            assert not mock_startrack_update_ticket.calls
    else:
        assert response.status == 500
        assert not startrack_calls
        assert not email_sent


@pytest.mark.now('2021-05-16T05:05:57.253Z')
@conftest.main_configuration
@pytest.mark.parametrize(
    ['session_id', 'ticket_id', 'expected_result', 'kios_result'],
    [
        (
            '774dd8d4-3196-4384-9ad2-f5726b0e3ab4',
            'EXAM-123',
            'not_passed',
            {'passed': False, 'completed': True},
        ),
        (
            '774dd8d4-3196-4384-9ad2-f5726b0e3ab4',
            'EXAM-123',
            'passed',
            {'passed': None, 'completed': True},
        ),
    ],
)
@pytest.mark.pgsql('callcenter_exams', files=['callcenter_exams.sql'])
async def test_fix_session_passed(
        web_app_client,
        patch,
        mock_startrack,
        mock_kiosk,
        session_id,
        ticket_id,
        expected_result,
        kios_result,
        load,
        mockserver,
        pgsql,
        mock_startrack_update_ticket,
):
    email_sent = False

    @mockserver.json_handler('/kiosk/api/v1/programs.json')
    async def _handle_sessions_another(request):
        assert request.query['external_id'] == 'EXAM-123'
        assert request.headers['KIOSK-API-KEY'] == 'kiosk_api_key'
        return {
            'programs': [
                {
                    'uuid': 'd985c6b4-136a-413a-8f5a-d0d0fd22e48f',
                    'name': 'Test',
                    'url': (
                        'https://instructor-dev.vmb.co/?programUuid='
                        'd985c6b4-136a413a-8f5a-d0d0fd22e48f&externalId=EXAM-123'  # noqa: E501
                    ),
                    'started': True,
                    'completed': kios_result['completed'],
                    'sessions': [
                        {'uuid': '774dd8d4-3196-4384-9ad2-f5726b0e3ab4'},
                    ],
                },
            ],
        }

    @mockserver.json_handler(
        '/kiosk/api/v1/sessions/774dd8d4-3196-4384-9ad2-f5726b0e3ab4',
    )
    async def _handle_sessions(request):
        result = ast.literal_eval(load('json_for_fix_session_passed'))
        result['session']['passed'] = kios_result['passed']
        return result

    @patch('generated.clients.sticker.StickerClient.queue_send_mail_request')
    async def _send_mail(body, **kwargs):
        nonlocal email_sent
        email_sent = True
        expected_body = (
            load('mail_success_no_fio.html')
            .strip('\n')
            .replace('$session_id$', session_id)
        )
        assert body.body == expected_body

    response = await web_app_client.post(
        HANDLE_URL,
        json={
            'user_name': None,
            'external_id': ticket_id,
            'session_id': session_id,
        },
        headers=conftest.pasport_headers('user_1'),
    )

    assert _handle_sessions_another.times_called == 1

    assert response.status == 200
    assert email_sent
    expected_text = (
        load(f'startrack_comment_{expected_result}_no_fio')
        .strip('\n')
        .replace('$session_id$', session_id)
    )
    startrack_calls = mock_startrack_update_ticket.calls
    assert len(startrack_calls) == 1
    assert startrack_calls[0]['kwargs']['json']['comment'] == expected_text
