import pytest


NATIVE_PLUS = 'ru.yandex.plus.1month.autorenewable.native.web.1month.trial.169'


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
async def test_subscription_not_enabled(web_plus):
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus',
    ).perform()

    assert result.status_code == 429


async def test_subscription_not_mapped(web_plus):
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus',
    ).perform()

    assert result.status_code == 409


@pytest.mark.config(
    PLUS_SUBSCRIPTION_STOP_ENABLED=False,
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'ya_plus': NATIVE_PLUS},
)
async def test_stopping_stop_disable(web_plus, mock_mediabilling):
    mock_mediabilling.stop_subscription.success()
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus',
    ).perform()

    assert result.status_code == 429


@pytest.mark.config(
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'ya_plus': NATIVE_PLUS},
)
async def test_stopping_ok(web_plus, mock_mediabilling):
    mock_mediabilling.stop_subscription.success()
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus',
    ).perform()

    assert result.status_code == 200


@pytest.mark.config(
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'ya_plus_trial': NATIVE_PLUS},
)
async def test_stopping_trial_sub_ok(web_plus, mock_mediabilling):
    mock_mediabilling.stop_subscription.success()
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus_trial',
    ).perform()

    assert result.status_code == 200


@pytest.mark.parametrize('http_status', [400, 404])
@pytest.mark.config(
    PLUS_SUBSCRIPTIONS_TO_PRODUCT_MAPPING={'ya_plus': NATIVE_PLUS},
)
async def test_stopping_mediabilling_error(
        web_plus, mock_mediabilling, http_status,
):
    mock_mediabilling.stop_subscription.set_http_status(http_status).error(
        error_id=345,
    )
    result = await web_plus.subscription_stop.request(
        subscription_id='ya_plus',
    ).perform()

    assert result.status_code == 409
