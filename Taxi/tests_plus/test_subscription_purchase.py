import pytest


NATIVE_PLUS = 'ru.yandex.plus.1month.autorenewable.native.web.1month.trial.169'


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
async def test_purchase_not_enabled(web_plus):
    result = await web_plus.subscription_purchase.request(
        subscription_id='plus_russia', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 429


@pytest.mark.config(PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': []})
async def test_subscription_disallowed(web_plus):
    result = await web_plus.subscription_purchase.request(
        subscription_id='plus_russia', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
)
@pytest.mark.parametrize(
    'status, order_id',
    [
        ('already-purchased', 12345),
        ('already-pending', None),
        ('error', 12345),
        ('success', None),
        ('need-supply-payment-data', 12345),
    ],
)
async def test_subscription_wrong_status(
        web_plus, mock_mediabilling, status, order_id,
):
    mock_mediabilling.submit_order.status(status).order_id(order_id)

    result = await web_plus.subscription_purchase.request(
        subscription_id='plus_russia', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
)
async def test_purchase_not_mapped(web_plus, mock_mediabilling):
    result = await web_plus.subscription_purchase.request(
        subscription_id='plus_russia', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['plus_russia']},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'plus_russia': NATIVE_PLUS},
)
async def test_purchase_ok(web_plus, mock_mediabilling):
    order_id = 123456789
    mock_mediabilling.submit_order.status('success').order_id(order_id)

    result = await web_plus.subscription_purchase.request(
        subscription_id='plus_russia', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 200
    content = result.json()
    assert content['purchase_id'] == str(order_id)


@pytest.mark.config(
    PLUS_ALLOWED_SUBSCRIPTIONS_BY_COUNTRIES={'ru': ['ya_trial_sub_rus']},
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'ya_trial_sub_rus': NATIVE_PLUS},
)
async def test_purchase_trial_sub_ok(web_plus, mock_mediabilling):
    order_id = 123456789
    mock_mediabilling.submit_order.status('success').order_id(order_id)

    result = await web_plus.subscription_purchase.request(
        subscription_id='ya_trial_sub_rus', payment_method_id='card-xxxx',
    ).perform()

    assert result.status_code == 200
    content = result.json()
    assert content['purchase_id'] == str(order_id)
