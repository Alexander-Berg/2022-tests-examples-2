import pytest

from duty_product_planning.api import startrack_handle


def _mock_ticket(
        key='TAXIDUTY-1', components=None, tags=None, importance=None,
):
    return {
        'key': key,
        'message': 'Message',
        'importance': importance,
        'components': components,
        'tags': tags,
    }


async def test_empty_config(taxi_duty_product_planning_web):
    body = _mock_ticket()
    headers = {'X-YaTaxi-Telegram-Token': 'token'}
    response = await taxi_duty_product_planning_web.post(
        '/internal/v1/startrack/handle', json=body, headers=headers,
    )
    assert response.status == 200


@pytest.mark.config(
    DUTY_NOTIFICATIONS_SETTINGS_2=[
        {'chat_id': 'chat_id_1'},
        {'chat_id': 'chat_id_2', 'components': [['backend']]},
        {'chat_id': 'chat_id_2', 'tags': [['backend']]},
        {'chat_id': 'chat_id_3', 'importance': 60},
    ],
)
async def test_notify(taxi_duty_product_planning_web):
    body = _mock_ticket(importance=100)
    headers = {'X-YaTaxi-Telegram-Token': 'token'}
    response = await taxi_duty_product_planning_web.post(
        '/internal/v1/startrack/handle', json=body, headers=headers,
    )
    assert response.status == 200


@pytest.mark.parametrize(
    'c_importance,t_importance,should_notify',
    [
        (None, 80, True),
        (0, 80, True),
        (80, 80, True),
        (100, 80, False),
        (100, None, False),
    ],
)
async def test_filter_importance(c_importance, t_importance, should_notify):
    consumer = startrack_handle.Consumer(
        chat_id='chat', importance=c_importance, components=[], tags=[],
    )
    ticket = startrack_handle.models.api.StartrackTask(
        key='key', message='msg', importance=t_importance,
    )
    # pylint: disable=protected-access
    notify = startrack_handle._check_importance(ticket, consumer)
    assert notify == should_notify


@pytest.mark.parametrize(
    'c_tags,t_tags,should_notify',
    [
        ([], None, True),
        ([], 't1', True),
        ([['t1']], 't2', False),
        ([['t1', 't2']], 't1', False),
        ([['t1', 't2']], 't2, t1', True),
        ([['t1', 't2'], ['t2', 't3']], 't2, t3', True),
    ],
)
async def test_filter_tags(c_tags, t_tags, should_notify):
    consumer = startrack_handle.Consumer(
        chat_id='chat', components=[], tags=c_tags, importance=None,
    )
    ticket = startrack_handle.models.api.StartrackTask(
        key='key', message='msg', tags=t_tags,
    )
    # pylint: disable=protected-access
    notify = startrack_handle._check_tags(ticket, consumer)
    assert notify == should_notify


@pytest.mark.parametrize(
    'c_comps,t_comps,should_notify',
    [
        ([], None, True),
        ([], 'c1', True),
        ([['c1']], 'c2', False),
        ([['c1', 'c2']], 'c1', False),
        ([['c1', 'c2']], 'c2, c1', True),
        ([['c1', 'c2'], ['c2', 'c3']], 'c3, c2', True),
    ],
)
async def test_filter_components(c_comps, t_comps, should_notify):
    consumer = startrack_handle.Consumer(
        chat_id='chat', components=c_comps, tags=[], importance=None,
    )
    ticket = startrack_handle.models.api.StartrackTask(
        key='key', message='msg', components=t_comps,
    )
    # pylint: disable=protected-access
    notify = startrack_handle._check_components(ticket, consumer)
    assert notify == should_notify
