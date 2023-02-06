import datetime
import logging

import pytest


logger = logging.getLogger(__name__)

DATA = (
    '{\"NODE\":\"TAXI-MYT-QAPP1\",'
    '\"PARTITION\":\"TAXIMYT1\",'
    '\"DATE\":1566395449,'
    '\"CALLID\":\"taxi-myt-qapp1.yndx.net-1566395444.1632\",'
    '\"QUEUENAME\":\"disp_cc\",'
    '\"AGENT\":null,'
    '\"ACTION\":\"META\",'
    '\"DATA1\":\"0\",'
    '\"DATA2\":\"0002030101-0000065536-1588774110-0002446012\",'
    '\"DATA3\":\"X-CC-OriginalDN\",'
    '\"DATA4\":\"+73812955555\",'
    '\"DATA5\":\"commutation_id\",'
    '\"DATA6\":null,'
    '\"DATA7\":null,'
    '\"DATA8\":null,'
    '\"OTHER\":null}\n'
)


@pytest.mark.now('2019-09-03T11:00:00.00Z')
@pytest.mark.parametrize(
    ['events_data', 'expected_call_status'],
    (
        pytest.param(
            '1_meta.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600901',
                    'krasnodar_disp_cc',
                    'meta',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has NO abonent_phone_guid from ENTERQUEUE
                    None,
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    None,
                ),
            ],
            id='1_meta.txt',
        ),
        pytest.param(
            '2_queued.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    'krasnodar_disp_cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    None,
                ),
            ],
            id='2_queued.txt',
        ),
        pytest.param(
            '3_queued_no_meta.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600903',
                    'krasnodar_disp_cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO call_guid from META
                    None,
                    # has NO called_number from META
                    None,
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    None,
                ),
            ],
            id='3_queued_no_meta.txt',
        ),
        pytest.param(
            '4_talking.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    'krasnodar_disp_cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has agent_id from CONNECT
                    '1000001304',
                    None,
                ),
            ],
            id='4_talking.txt',
        ),
        pytest.param(
            '5_talking_no_pre_events.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600905',
                    'krasnodar_disp_cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO call_guid from META
                    None,
                    # has NO called_number from META
                    None,
                    # has abonent_phone_guid from ENTERQUEUE
                    None,
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has agent_id from CONNECT
                    '1000001304',
                    None,
                ),
            ],
            id='5_talking_no_pre_events.txt',
        ),
        pytest.param('6_abandoned.txt', [], id='6_abandoned.txt'),
        pytest.param(
            '7_completed_by_agent.txt', [], id='7_completed_by_agent.txt',
        ),
        pytest.param(
            '10_queued_dbl.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600902',
                    'krasnodar_disp_cc',
                    'queued',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has NO answered_at
                    None,
                    # has NO agent_id from CONNECT
                    None,
                    None,
                ),
            ],
            id='10_queued_dbl.txt',
        ),
        pytest.param(
            '11_talking_dbl.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    'krasnodar_disp_cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has agent_id from CONNECT
                    '1000001304',
                    None,
                ),
            ],
            id='11_talking_dbl.txt',
        ),
        pytest.param(
            '12_talking_dbl.txt',
            [
                (
                    'taxi-mar-qproc1.yndx.net-1588774115.600904',
                    'krasnodar_disp_cc',
                    'talking',
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, 0, tzinfo=datetime.timezone.utc,
                    ),
                    # has call_guid from META
                    '0002030101-0000065536-1588774110-0002446012',
                    # has called_number from META
                    '+73812955555',
                    # has abonent_phone_guid from ENTERQUEUE
                    '+79991111111_id',
                    # has queued_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 35, tzinfo=datetime.timezone.utc,
                    ),
                    # has answered_at
                    datetime.datetime(
                        2020, 5, 6, 14, 8, 55, tzinfo=datetime.timezone.utc,
                    ),
                    # has agent_id from CONNECT
                    '1000001304',
                    None,
                ),
            ],
            id='12_talking_dbl.txt',
        ),
    ),
)
async def test_call_status(
        taxi_callcenter_stats,
        testpoint,
        events_data,
        load,
        pgsql,
        expected_call_status,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(events_data)

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT * from callcenter_stats.call_status',
    )
    call_status_result = cursor.fetchall()
    cursor.close()

    assert call_status_result == expected_call_status


@pytest.mark.now('2019-09-03T11:00:00.00Z')
async def test_commutation_id(
        taxi_callcenter_stats,
        testpoint,
        load,
        pgsql,
        mock_personal,
        lb_message_sender,
):
    await taxi_callcenter_stats.invalidate_caches()
    await lb_message_sender.send(DATA, raw=True)

    cursor = pgsql['callcenter_stats'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT commutation_id from callcenter_stats.call_status',
    )
    commutation_id = cursor.fetchall()[0][0]
    cursor.close()

    assert commutation_id == 'commutation_id'
