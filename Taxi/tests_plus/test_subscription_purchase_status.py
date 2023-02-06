import pytest


@pytest.mark.config(PLUS_SERVICE_ENABLED=False)
async def test_subscription_not_enabled(web_plus):
    result = await web_plus.subscription_status.request(
        purchase_id='123456789',
    ).perform()

    assert result.status_code == 429


@pytest.mark.parametrize(
    'status,result_status,sync_feactures',
    [
        ('refund', 'success', True),
        ('refund', 'pending', False),
        ('refund', 'success', None),
        ('cancelled', 'failure', True),
        ('ok', 'success', True),
        ('ok', 'pending', False),
        ('ok', 'success', None),
        ('pending', 'pending', True),
        ('error', 'failure', True),
        ('fail-3ds', 'failure', True),
    ],
)
async def test_purchase_status_billing_resp(
        web_plus, mock_mediabilling, status, result_status, sync_feactures,
):
    mock_mediabilling.order_info.status(status).order_id(123456).sync_features(
        sync_feactures,
    )
    result = await web_plus.subscription_status.request(
        purchase_id='123456789',
    ).perform()

    assert result.status_code == 200
    content = result.json()
    assert content['status'] == result_status


async def test_purchase_status_ok(web_plus, mock_mediabilling):
    mock_mediabilling.order_info.status('ok').order_id(125748)

    result = await web_plus.subscription_status.request(
        purchase_id='123456789',
    ).perform()

    assert result.status_code == 200
    content = result.json()
    assert content['status'] == 'success'


async def test_mediabillling_404_ok(web_plus, mock_mediabilling):
    mock_mediabilling.order_info.set_http_status(404)

    result = await web_plus.subscription_status.request(
        purchase_id='123456789',
    ).perform()

    assert result.status_code == 200
    content = result.json()
    assert content['status'] == 'failure'
