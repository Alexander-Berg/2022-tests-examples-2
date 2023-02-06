import copy

import pytest

EATER_ID = 12345
DEVICE_ID = 'test_device'
DEFAULT_HEADERS = {'x-app-version': '5.4.0', 'x-platform': 'eda_ios_app'}


@pytest.mark.parametrize(
    ['feed_type', 'service'],
    [
        ('banner', 'eats-promotions-banner'),
        ('story', 'eats-promotions-story'),
        ('informer', 'eats-promotions-informer'),
    ],
)
@pytest.mark.parametrize(
    ['user_id', 'device_id', 'channels'],
    [
        (EATER_ID, None, [f'user_id:{EATER_ID}']),
        (
            EATER_ID,
            DEVICE_ID,
            [f'user_id:{EATER_ID}', f'device_id:{DEVICE_ID}'],
        ),
        (None, DEVICE_ID, [f'device_id:{DEVICE_ID}']),
    ],
)
async def test_viewed(
        taxi_eats_communications,
        mockserver,
        testpoint,
        feed_type,
        service,
        user_id,
        device_id,
        channels,
):
    """
    Проверяем, что ручка для пометки баннеров как просмотренные
    проксирует переданные фиды в ручку feeds
    Канал составляется из eater_id и device_id при их наличии
    """

    feed_id = 'my_feed_id'

    @mockserver.json_handler('/feeds/v1/batch/log_status')
    def feeds(request):
        items = request.json['items']
        assert len(items) == 1
        assert items[0]['service'] == service
        assert items[0]['feed_ids'] == [feed_id]
        assert items[0]['status'] == 'viewed'
        assert items[0]['channel'] in channels

        return {'items': [{feed_id: 200}]}

    @testpoint('feeds-viewed-queue-task-finished')
    def task_finished(data):
        pass

    headers = copy.deepcopy(DEFAULT_HEADERS)
    if device_id is not None:
        headers['x-device-id'] = 'test_device'
    if user_id is not None:
        headers['x-eats-user'] = f'user_id={user_id}'
    response = await taxi_eats_communications.post(
        '/eats/v1/eats-communications/v1/viewed',
        headers=headers,
        json={'communications': [{'feed_id': feed_id, 'type': feed_type}]},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'OK'}

    await task_finished.wait_call()
    assert feeds.times_called == (2 if device_id and user_id else 1)


@pytest.mark.parametrize('feed_type', ['banner', 'story', 'informer'])
async def test_viewed_unauthorized(taxi_eats_communications, feed_type):
    """
    Проверяем, что ручка для пометки баннеров как просмотренные
    не отдает ошибку для неавторизованного пользователя без device_id
    """

    feed_id = 'my_feed_id'

    response = await taxi_eats_communications.post(
        '/eats/v1/eats-communications/v1/viewed',
        headers=DEFAULT_HEADERS,
        json={'communications': [{'feed_id': feed_id, 'type': feed_type}]},
    )

    assert response.status_code == 200
    assert response.json() == {'status': 'UNKNOWN_USER'}
