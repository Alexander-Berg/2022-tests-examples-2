import pytest

from taxi.clients import passport

from taxi_shared_payments.stq import send_trigger_email

SLUG = 'some_slug'
WELCOME_EMAIL_TYPE = 'WelcomeEmail'
YATAXI_BRAND = 'yataxi'


@pytest.mark.config(
    COOP_ACCOUNT_REPORTS_SENDER_SLUGS={WELCOME_EMAIL_TYPE: {'ru': SLUG}},
    COOP_ACCOUNT_USE_BRAND_IN_EMAILS=True,
    COOP_ACCOUNT_EMAILS_BRAND_PARAMS={
        YATAXI_BRAND: {'from_email': 'a@a.com', 'from_name': 'name'},
    },
)
@pytest.mark.parametrize(
    ['send_email', 'locale', 'brand', 'expected_calls'],
    [
        pytest.param(
            'account1_email', 'ru', YATAXI_BRAND, 1, id='regural send',
        ),
        pytest.param(
            '', 'ru', YATAXI_BRAND, 0, id='could not find email, do not send',
        ),
    ],
)
async def test_send_trigger_email_task(
        stq3_context, patch, send_email, locale, brand, expected_calls,
):
    @patch('taxi.clients.sender.SenderClient.send_transactional_email')
    async def _send(slug, email, **kwargs):
        assert slug == SLUG
        assert email == send_email
        assert kwargs['template_vars'] == {
            'brand': YATAXI_BRAND,
            'email_source': send_trigger_email.USER_EMAIL_SOURCE,
        }
        assert kwargs['from_email'] == 'a@a.com'
        assert kwargs['from_name'] == 'name'

    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        return {'email': send_email}

    await send_trigger_email.task(
        stq3_context, 'account1', WELCOME_EMAIL_TYPE, 'some_ip', locale, brand,
    )

    assert len(_send.calls) == expected_calls


@pytest.mark.parametrize(
    ['account_id', 'user_ip', 'expected_email', 'expected_source'],
    [
        pytest.param(
            'account1',
            'some_ip',
            'account1_email',
            send_trigger_email.USER_EMAIL_SOURCE,
            id='get email from account',
        ),
        pytest.param(
            'account2',
            'some_ip',
            'account2_email_from_passport',
            send_trigger_email.PASSPORT_EMAIL_SOURCE,
            id='get email from passport',
        ),
        pytest.param(
            'account3', '', None, None, id='Get not existed account email',
        ),
    ],
)
async def test_get_account_email(
        stq3_context,
        patch,
        account_id,
        user_ip,
        expected_email,
        expected_source,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(data_type, request_id, *args, **kwargs):
        return {'email': request_id}

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info(*args, **kwargs):
        return {'address-list': [{'address': 'account2_email_from_passport'}]}

    email_obj = await send_trigger_email.get_account_email(
        stq3_context, account_id, user_ip,
    )
    if email_obj:
        assert email_obj['email'] == expected_email
        assert email_obj['source'] == expected_source


@pytest.mark.parametrize(
    ['account_id', 'user_ip', 'passport_error'],
    [
        pytest.param('account2', '', None, id='pass no ip to passport'),
        pytest.param(
            'account2',
            'some_ip',
            passport.InvalidRequestError,
            id='pass no ip to passport',
        ),
    ],
)
async def test_get_account_email_fail(
        stq3_context, patch, account_id, user_ip, passport_error,
):
    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info(*args, **kwargs):
        raise passport_error

    email = await send_trigger_email.get_account_email(
        stq3_context, account_id, user_ip,
    )
    assert email is None
