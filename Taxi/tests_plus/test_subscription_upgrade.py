import pytest


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
async def test_subscription_not_enabled(web_plus):
    result = await web_plus.subscription_upgrade.request(
        has_plus=True, has_cashback_plus=False,
    ).perform()

    assert result.status_code == 429


@pytest.mark.experiments3()
@pytest.mark.parametrize(
    'has_plus, has_cashback_plus',
    [(False, False), (False, True), (True, True)],
)
async def test_upgrade_fails(web_plus, has_plus, has_cashback_plus):
    result = await web_plus.subscription_upgrade.request(
        has_plus=has_plus, has_cashback_plus=has_cashback_plus,
    ).perform()

    assert result.status_code == 409


# NOTE: no mark.experiments3()
async def test_experiment_disabled(web_plus):
    result = await web_plus.subscription_upgrade.request(
        has_plus=True, has_cashback_plus=False,
    ).perform()

    assert result.status_code == 409


@pytest.mark.experiments3()
async def test_upgrade_success(web_plus, mock_mediabilling_v2):
    result = await web_plus.subscription_upgrade.request(
        has_plus=True, has_cashback_plus=False,
    ).perform()

    assert result.status_code == 200


@pytest.mark.experiments3()
@pytest.mark.parametrize('mb_status', [400, 409, 500])
async def test_mediabilling_errors(web_plus, mock_mediabilling_v2, mb_status):
    mock_mediabilling_v2.cashback_status.http_status = mb_status

    result = await web_plus.subscription_upgrade.request(
        has_plus=True, has_cashback_plus=False,
    ).perform()

    assert result.status_code == 500
