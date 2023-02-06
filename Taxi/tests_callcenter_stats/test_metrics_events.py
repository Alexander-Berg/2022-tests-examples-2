import pytest

MESSAGE = (
    '{\"NODE\":\"TAXI-MYT-QAPP1\",'
    '\"PARTITION\":\"TAXIMYT1\",'
    '\"DATE\":1566395449,'
    '\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\",'
    '\"QUEUENAME\":\"disp_cc\",'
    '\"AGENT\":null,'
    '\"ACTION\":\"ENTERQUEUE\",'
    '\"DATA1\":\"\",'
    '\"DATA2\":\"79872676410\",'
    '\"DATA3\":\"1\",'
    '\"DATA4\":null,'
    '\"DATA5\":null,'
    '\"DATA6\":null,'
    '\"DATA7\":null,'
    '\"DATA8\":null,'
    '\"OTHER\":null}\n'
)


@pytest.mark.config(
    TVM_ENABLED=False,
    TVM_RULES=[{'src': 'callcenter_stats', 'dst': 'personal'}],
)
@pytest.mark.parametrize(
    ['data', 'expected_queue', 'expected_action'],
    (pytest.param(MESSAGE, 'disp_cc', 'enterqueue', id='message_1'),),
)
async def test_message(
        taxi_callcenter_stats,
        taxi_callcenter_stats_monitor,
        mock_personal,
        testpoint,
        data,
        expected_queue,
        expected_action,
        lb_message_sender,
):
    # Enable testpoints and clear metrics with help of cache invalidator
    await taxi_callcenter_stats.enable_testpoints()

    # Put message to logbroker consumer as if logbroker does
    await lb_message_sender.send(data, raw=True)

    # Check monitor answer
    response = await taxi_callcenter_stats_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['qapp-event-consumer']['qapp_event']
    assert metrics['ok']['1min'] == 1
    tel_events = metrics['action']['1min']
    assert tel_events[expected_queue][expected_action] == 1

    node_events = metrics['node']['1min']
    assert node_events['taxi-myt-qapp1'] == 1
