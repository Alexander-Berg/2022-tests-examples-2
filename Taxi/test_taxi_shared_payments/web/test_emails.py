import pytest


from taxi_shared_payments.controllers import emails

SLUG = 'some_slug'
WELCOME_EMAILS_LIST = [
    'WelcomeEmail',
    'Onboarding1stEmail',
    'Onboarding2ndEmail',
    'Onboarding3rdEmail',
]
FULL_CONFIG_LIST = WELCOME_EMAILS_LIST + [emails.DEFAULT_KEY]


@pytest.mark.parametrize(
    ['account_id', 'locale', 'brand', 'user_ip'],
    [pytest.param('1', 'ru', 'yataxi', 'some_ip', id='regular')],
)
@pytest.mark.config(
    COOP_ACCOUNT_REPORTS_SENDER_SLUGS={
        email_type: {'ru': SLUG} for email_type in WELCOME_EMAILS_LIST
    },
    COOP_ACCOUNT_SEND_EMAIL_SWITCHES={emails.DEFAULT_KEY: True},
    COOP_ACCOUNT_USE_BRAND_IN_EMAILS=True,
    COOP_ACCOUNT_WELCOME_EMAILS_LIST=WELCOME_EMAILS_LIST,
)
async def test_welcome_emails(
        mockserver, web_context, account_id, locale, brand, user_ip,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {
            'items': [
                {'name': emails.EXPERIMENT_NAME, 'value': {'enabled': True}},
            ],
        }

    @mockserver.json_handler(
        r'/stq-agent/queues/api/add/(?P<queue_name>\w+)', regex=True,
    )
    async def _queue(request, queue_name):
        kwargs = request.json['kwargs']
        assert kwargs['account_id'] == account_id
        assert kwargs['locale'] == locale
        assert kwargs['user_ip'] == user_ip
        assert kwargs['email_type'] in WELCOME_EMAILS_LIST
        assert kwargs['brand'] == brand

    await emails.send_welcome_emails(
        web_context, account_id, locale, brand, user_ip,
    )
    assert _queue.times_called == len(WELCOME_EMAILS_LIST)


@pytest.mark.parametrize(
    ['account_id', 'experiments_response', 'expected_result'],
    [
        pytest.param(
            'business-account1',
            [{'name': emails.EXPERIMENT_NAME, 'value': {'enabled': False}}],
            False,
            id='test group',
        ),
        pytest.param('business-account1', [], True, id='control group'),
    ],
)
async def test_set_ab_test_group(
        web_context,
        mockserver,
        account_id,
        experiments_response,
        expected_result,
):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _handler(request):
        return {'items': experiments_response}

    result = await emails.is_onboarding_sending_enabled(
        web_context, account_id,
    )
    assert result == expected_result
