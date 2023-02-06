# import datetime


import pytest

from tests_cargo_corp import utils


MOCK_NOW = '2021-05-31T19:00:00+00:00'
MOCK_NOW_PLUS_MINUTE = '2021-05-31T19:01:00+00:00'
CONFIRMATION_CODE = 'confirmation_code'
CONTACT_PD_ID = 'contact_pd_id'

# hash for utils.CORP_CLIENT_ID & CONTACT_PD_ID
HASH = '87ea5dfc8b8e384d848979496e706390b497e547'

INVITATION_LINK_LONG = (
    'https://dostavka.yandex.ru/account2?join_staff=%257B%2522'
    f'confirmation_code%2522%253A%2522{CONFIRMATION_CODE}%2522%252C%2522'
    f'corp_client_id%2522%253A%2522{utils.CORP_CLIENT_ID}%2522%257D'
)
INVITATION_LINK_SHORT = 'https://ya.cc/123'


@pytest.fixture(name='ucomm_ctx')
def _ucomm_ctx(mockserver):
    class Context:
        def __init__(self):
            self.send_sms_expected_request = None
            self.send_sms_response = None

        def set_send_sms_expected_request(self, short_link_expected):
            self.send_sms_expected_request = {
                'intent': 'cargo_corp_employee_invitation',
                'locale': 'ru',
                'meta': {
                    'confirmation_code': CONFIRMATION_CODE,
                    'contact_pd_id': CONTACT_PD_ID,
                },
                'phone_id': CONTACT_PD_ID,
                'text': {
                    'key': 'cargo_corp.notification.sms.employee_invitation',
                    'keyset': 'cargo',
                    'params': {
                        'invitation_url': (
                            INVITATION_LINK_SHORT
                            if short_link_expected
                            else INVITATION_LINK_LONG
                        ),
                    },
                },
            }

        def send_sms_response_by_code(self, code):
            respbody = {'code': str(code), 'message': str(code)}
            self.send_sms_response = mockserver.make_response(
                status=code, json=respbody,
            )

        def get_send_sms_response(self):
            if self.send_sms_response is not None:
                return self.send_sms_response

            return {'code': '200', 'message': '200'}

    return Context()


@pytest.fixture(name='mock_ucommunications_sms')
def _personal_handler_retrieve(mockserver, ucomm_ctx):
    @mockserver.json_handler('/ucommunications/user/sms/send')
    def _sms(request):
        assert request.headers['X-Idempotency-Token'] == HASH
        if ucomm_ctx.send_sms_expected_request:
            assert request.json == ucomm_ctx.send_sms_expected_request
        return ucomm_ctx.get_send_sms_response()

    return _sms


def get_task_kwargs(started_at=MOCK_NOW, kind='sms', host=None, country=None):
    args = {
        'invitation_kind': kind,
        'corp_client_id': utils.CORP_CLIENT_ID,
        'confirmation_code': CONFIRMATION_CODE,
        'contact_pd_id': CONTACT_PD_ID,
        'locale': 'ru',
        'started_at': started_at,
    }
    if host:
        args['host'] = host
    if country:
        args['country'] = country
    return args


# TODO (dipterix): group tests by classes?
@pytest.mark.now(MOCK_NOW)
async def test_stq_run_nothing_happens_no_country(
        stq_runner, stq, mock_ucommunications_sms,
):
    """Stq is enabled, but no country provided in args, so nothing happens"""
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(),
    )

    assert not mock_ucommunications_sms.has_calls
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_stq_run_nothing_happens_no_config(
        stq_runner, stq, mock_ucommunications_sms,
):
    """Stq is enabled, but no availabitity exp, so nothing happens"""
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert not mock_ucommunications_sms.has_calls
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.experiments3(filename='experiment.json')
async def test_stq_run_sending_sms_long_link(
        stq_runner, stq, mock_ucommunications_sms, ucomm_ctx,
):
    """Stq is enabled, availabitity exp is ok, sending sms with long link"""
    ucomm_ctx.set_send_sms_expected_request(short_link_expected=False)
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert mock_ucommunications_sms.times_called == 1
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(CARGO_CORP_ENABLE_SHORT_URL_IN_SMS=True)
async def test_stq_run_sending_sms_short_link(
        stq_runner, stq, mock_ucommunications_sms, mockserver, ucomm_ctx,
):
    """Stq is enabled, availabitity exp is ok, sending sms with short link"""

    @mockserver.json_handler('/clck/--')
    def _mock_clck(request):
        return [INVITATION_LINK_SHORT]

    ucomm_ctx.set_send_sms_expected_request(short_link_expected=True)
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert mock_ucommunications_sms.times_called == 1
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.experiments3(filename='experiment.json')
async def test_stq_run_ucomm_429(
        stq_runner, stq, mock_ucommunications_sms, ucomm_ctx,
):
    """Stq is enabled, exp is ok, ucomm 429, stq will be rescheduled"""
    ucomm_ctx.send_sms_response_by_code(code=429)
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert mock_ucommunications_sms.times_called == 1
    assert stq.cargo_corp_send_employee_invitation.times_called == 1


@pytest.mark.now(MOCK_NOW_PLUS_MINUTE)
@pytest.mark.experiments3(filename='experiment.json')
async def test_stq_late_run(
        stq_runner, stq, mock_ucommunications_sms, ucomm_ctx,
):
    """Stq is enabled, availabitity exp is ok, ucomm 429,
        but it is late - stq will not be rescheduled"""
    ucomm_ctx.send_sms_response_by_code(code=429)
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert mock_ucommunications_sms.times_called == 1
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.config(
    CARGO_CORP_SEND_EMPLOYEE_INVITATION_SETTINGS={'enabled': False},
)
@pytest.mark.experiments3(filename='experiment.json')
async def test_stq_disabled(stq_runner, stq, mock_ucommunications_sms):
    """Stq is disabled, availabitity exp is ok, nothing happens"""
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert not mock_ucommunications_sms.has_calls
    assert stq.cargo_corp_send_employee_invitation.times_called == 0


@pytest.mark.experiments3(filename='experiment.json')
@pytest.mark.config(
    CARGO_CORP_SEND_EMPLOYEE_INVITATION_SETTINGS={
        'enabled': True,
        'reschedule_immediately': True,
    },
)
async def test_stq_delayed(stq_runner, stq, mock_ucommunications_sms):
    """Stq reschedules itself immediately"""
    await stq_runner.cargo_corp_send_employee_invitation.call(
        task_id='id', kwargs=get_task_kwargs(country='rus'),
    )

    assert not mock_ucommunications_sms.has_calls
    assert stq.cargo_corp_send_employee_invitation.times_called == 1
