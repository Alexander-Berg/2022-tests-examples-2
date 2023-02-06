import typing

import pytest

from taxi_sm_monitor import settings as sm_settings


@pytest.mark.config(
    YOUSCAN_PROFILES={
        'support-taxi': {
            'st-profile': 'support-taxi',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'yandex_taxi': 'taxi'},
        },
        'support-zen': {
            'st-profile': 'support-zen',
            'queue': 'YOUSCAN',
            'enabled': True,
            'topic-group-to-ml': {'yandex_taxi': 'taxi'},
        },
    },
    YOUSCAN_TO_STARTRACK_ENABLED=True,
    YOUSCAN_TOPIC_GROUPS=['yandex_taxi', 'yandex_eats', 'uber'],
)
@pytest.mark.parametrize('topic_group', ('yandex_taxi', 'yandex_eats', 'uber'))
@pytest.mark.parametrize('profile', (None, 'support-taxi', 'support-zen'))
async def test_youscan_webhook(
        taxi_sm_monitor_client,
        patch,
        topic_group: str,
        profile: typing.Optional[str],
):
    data = {
        'mentionId': 42095240,
        'postType': 'post',
        'published': '2019-10-14T20:57:19Z',
        'resourceType': 'social',
        'spam': False,
        'topicId': 83499,
        'topicName': 'Yandex.Taxi Водители',
        'url': 'https://vk.com/wall-185605318_50',
    }
    params = {'profile': profile} if profile else None

    @patch('taxi.stq.client.put')
    async def _put(queue, eta=None, task_id=None, args=None, kwargs=None):
        assert queue == sm_settings.STQ_TAXI_SM_MONITOR_YOUSCAN_QUEUE
        assert args[0] == {**data, 'topicGroup': topic_group}
        assert kwargs.get('profile') == profile

    response = await taxi_sm_monitor_client.post(
        '/webhook/youscan/{}'.format(topic_group), json=data, params=params,
    )
    assert response.status == 200
    assert _put.calls


@pytest.mark.config(YOUSCAN_TO_STARTRACK_ENABLED=True, YOUSCAN_TOPIC_GROUPS=[])
@pytest.mark.parametrize('topic_group', ('yandex_taxi', 'yandex_eats', 'uber'))
async def test_youscan_webhook_validation(
        taxi_sm_monitor_client, topic_group: str,
):

    response = await taxi_sm_monitor_client.post(
        '/webhook/youscan/{}'.format(topic_group), json={},
    )
    assert response.status == 400
