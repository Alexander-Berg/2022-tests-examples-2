# pylint: disable=unused-variable
import pytest

from taxi import settings


@pytest.mark.parametrize(
    ['data', 'status_code', 'order_data'],
    [
        (
            {
                'order_id': '089d368248001cbe652cadf8c93558dc',
                'compensation_sum': 1000,
                'ticket': '46957242',
                'real_ip': '127.0.0.1',
                'x_forwarded_for': 'test',
            },
            200,
            {
                'currency': 'RUB',
                'sum_to_pay': {'ride': 1049.0, 'tips': 52.45},
                'version': 28,
            },
        ),
        (
            {
                'order_id': '089d368248001cbe652cadf8c93558dc',
                'compensation_sum': 1000,
                'ticket': '46957242',
                'ticket_type': 'chatterbox',
                'reason': 'cashrunner',
                'real_ip': '127.0.0.1',
                'x_forwarded_for': 'test',
            },
            200,
            {
                'currency': 'RUB',
                'sum_to_pay': {'ride': 1049.0, 'tips': 52.45},
                'version': 28,
            },
        ),
        (
            {
                'order_id': '089d368248001cbe652cadf8c93558dc',
                'compensation_sum': 1000,
                'ticket': '46957242',
                'real_ip': '127.0.0.1',
                'x_forwarded_for': 'test',
            },
            200,
            {
                'archive_order': True,
                'currency': 'RUB',
                'sum_to_pay': {'ride': 1049.0, 'tips': 52.45},
                'version': 28,
            },
        ),
    ],
)
async def test_success(
        support_info_client,
        patch_aiohttp_session,
        response_mock,
        admin_api_url,
        mock_csrf,
        mock_get_user_info,
        data,
        status_code,
        order_data,
):
    orders_info_filter = {'test_fields': 10}
    mock_get_user_info(
        response={'filters': {'/payments/orders_info/': orders_info_filter}},
    )

    @patch_aiohttp_session(admin_api_url + '/payments/orders_info', 'POST')
    def orders_info(*args, **kwargs):
        assert kwargs['json'] == {
            **orders_info_filter,
            'order_id': data['order_id'],
        }
        assert kwargs['headers'].pop('X-YaRequestId')
        assert kwargs['headers'] == {
            'Cookie': mock_csrf['str_cookies'],
            'X-Csrf-Token': mock_csrf['csrf_token'],
            'X-Real-Ip': '127.0.0.1',
            'X-Forwarded-For': 'test',
        }
        return response_mock(json={'orders': [order_data]})

    @patch_aiohttp_session(admin_api_url + '/payments/compensate_park', 'POST')
    def compensate_park(*args, **kwargs):
        expected_args = {
            'order_id': data['order_id'],
            'sum': data['compensation_sum'],
            'version': order_data['version'],
            'zendesk_ticket': data['ticket'],
        }
        for field in ('ticket_type', 'reason'):
            if field in data:
                expected_args[field] = data[field]

        assert kwargs['json'] == expected_args
        assert kwargs['headers'].pop('X-YaRequestId')
        assert kwargs['headers'] == {
            'Cookie': mock_csrf['str_cookies'],
            'X-Csrf-Token': mock_csrf['csrf_token'],
            'X-Real-Ip': '127.0.0.1',
            'X-Forwarded-For': 'test',
        }
        return response_mock(json={})

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order/restore', 'POST',
    )
    def order_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}])

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order_proc/restore',
        'POST',
    )
    def order_proc_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}])

    response = await support_info_client.post(
        '/v1/payments/process_compensation',
        json=data,
        cookies=mock_csrf['dict_cookies'],
    )
    assert response.status == status_code

    assert len(orders_info.calls) == 1
    if order_data.get('archive_order'):
        assert len(order_restore.calls) == 1
        assert len(order_proc_restore.calls) == 1
    else:
        assert not order_restore.calls
        assert not order_proc_restore.calls
    assert len(compensate_park.calls) == 1


async def test_order_not_found(
        support_info_client,
        patch_aiohttp_session,
        response_mock,
        admin_api_url,
        mock_csrf,
        mock_get_user_info,
):
    mock_get_user_info()

    @patch_aiohttp_session(admin_api_url + '/payments/orders_info', 'POST')
    def orders_info(*args, **kwargs):
        return response_mock(json={'orders': []})

    data = {
        'order_id': '089d368248001cbe652cadf8c93558dc',
        'compensation_sum': 100,
        'ticket': '46957242',
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
    }
    response = await support_info_client.post(
        '/v1/payments/process_compensation',
        json=data,
        cookies=mock_csrf['dict_cookies'],
    )
    assert response.status == 404
    assert await response.json() == {
        'status': 'request_error',
        'error': 'Order {} not found'.format(data['order_id']),
    }


async def test_order_info_error(
        support_info_client,
        patch_aiohttp_session,
        response_mock,
        admin_api_url,
        mock_csrf,
        mock_get_user_info,
):
    mock_get_user_info()

    @patch_aiohttp_session(admin_api_url + '/payments/orders_info', 'POST')
    def orders_info(*args, **kwargs):
        return response_mock(
            json={
                'message': 'Failed to perform request',
                'code': 'request_error',
                'status': 400,
            },
            status=400,
        )

    data = {
        'order_id': '089d368248001cbe652cadf8c93558dc',
        'compensation_sum': 100,
        'ticket': '46957242',
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
    }
    response = await support_info_client.post(
        '/v1/payments/process_compensation',
        json=data,
        cookies=mock_csrf['dict_cookies'],
    )
    assert response.status == 400


async def test_order_restore_error(
        support_info_client,
        patch_aiohttp_session,
        response_mock,
        admin_api_url,
        mock_csrf,
        mock_get_user_info,
):
    mock_get_user_info()
    data = {
        'order_id': '089d368248001cbe652cadf8c93558dc',
        'compensation_sum': 100,
        'ticket': '46957242',
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
    }

    @patch_aiohttp_session(admin_api_url + '/payments/orders_info', 'POST')
    def orders_info(*args, **kwargs):
        return response_mock(
            json={
                'orders': [
                    {
                        'archive_order': True,
                        'currency': 'RUB',
                        'sum_to_pay': {'ride': 1049.0, 'tips': 52.45},
                        'version': 28,
                    },
                ],
            },
        )

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order/restore', 'POST',
    )
    def order_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}])

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order_proc/restore',
        'POST',
    )
    def order_proc_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}], status=500)

    response = await support_info_client.post(
        '/v1/payments/process_compensation',
        json=data,
        cookies=mock_csrf['dict_cookies'],
    )
    assert response.status == 400


@pytest.mark.parametrize(
    ['message', 'status'],
    [
        ('failed to perform request', 400),
        ('permissions required', 403),
        ('race condition', 409),
    ],
)
@pytest.mark.config(SUPPORT_INFO_PAYMENTS_RETRY_NUMBER=3)
async def test_sum_process_error(
        support_info_client,
        patch_aiohttp_session,
        response_mock,
        admin_api_url,
        mock_csrf,
        message,
        status,
        mock_get_user_info,
):
    mock_get_user_info()
    data = {
        'order_id': '089d368248001cbe652cadf8c93558dc',
        'compensation_sum': 100,
        'ticket': '46957242',
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
    }

    @patch_aiohttp_session(admin_api_url + '/payments/orders_info', 'POST')
    def orders_info(*args, **kwargs):
        return response_mock(
            json={
                'orders': [
                    {
                        'archive_order': True,
                        'currency': 'RUB',
                        'sum_to_pay': {'ride': 1049.0, 'tips': 52.45},
                        'version': 28,
                    },
                ],
            },
        )

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order/restore', 'POST',
    )
    def order_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}])

    @patch_aiohttp_session(
        settings.Settings.ARCHIVE_API_URL + '/archive/order_proc/restore',
        'POST',
    )
    def order_proc_restore(*args, **kwargs):
        assert kwargs['json'] == {'id': '089d368248001cbe652cadf8c93558dc'}
        return response_mock(json=[{}])

    @patch_aiohttp_session(admin_api_url + '/payments/compensate_park', 'POST')
    def compensate_park(*args, **kwargs):
        return response_mock(
            json={'message': message, 'code': 'request_error'}, status=status,
        )

    response = await support_info_client.post(
        '/v1/payments/process_compensation',
        json=data,
        cookies=mock_csrf['dict_cookies'],
    )
    assert response.status == status

    if status == 409:
        calls_number = 3
    else:
        calls_number = 1
    assert len(orders_info.calls) == calls_number
    assert len(order_restore.calls) == calls_number
    assert len(order_proc_restore.calls) == calls_number
    assert len(compensate_park.calls) == calls_number
