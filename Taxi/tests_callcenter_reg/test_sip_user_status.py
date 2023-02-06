import datetime

import pytest
import pytz


@pytest.mark.now('2018-06-21T19:00:00+00:00')
@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
async def test_sip_user_status(taxi_callcenter_reg, pgsql):
    response = await taxi_callcenter_reg.post(
        '/v1/sip_user/status',
        {
            'project': 'disp',
            'yandex_uid': '1000000000000000',
            'status': {
                'status': 'disconnected',
                'sub_status': 'cool_sub_status',
            },
        },
    )
    # check ok scenario
    assert response.status_code == 200
    cursor = pgsql['callcenter_reg'].cursor()

    query = 'SELECT * FROM callcenter_reg.sip_user_status;'

    cursor.execute(query)

    res = cursor.fetchone()
    #  1000000000
    assert res == (
        '1000000000',
        'disconnected',
        'cool_sub_status',
        'disp',
        datetime.datetime(
            2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
        ),
        datetime.datetime(
            2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
        ),
        1,
    )


@pytest.mark.now('2018-06-21T19:00:00+00:00')
@pytest.mark.pgsql('callcenter_reg', files=['agent.sql'])
async def test_sip_user_status_404(taxi_callcenter_reg, pgsql):
    response = await taxi_callcenter_reg.post(
        '/v1/sip_user/status',
        {
            'project': 'disp',
            'yandex_uid': '1000000000000001',
            'status': {
                'status': 'disconnected',
                'sub_status': 'cool_sub_status',
            },
        },
    )
    # check not found scenario
    assert response.status_code == 404


@pytest.mark.now('2018-06-21T19:00:00+00:00')
async def test_sip_user_status_not_404(taxi_callcenter_reg, pgsql):
    response = await taxi_callcenter_reg.post(
        '/v1/sip_user/status',
        {
            'project': 'disp',
            'yandex_uid': '1000000000000001',
            'sip_username': 'sip_1',
            'status': {
                'status': 'disconnected',
                'sub_status': 'cool_sub_status',
            },
        },
    )
    # check ok scenario
    assert response.status_code == 200
    cursor = pgsql['callcenter_reg'].cursor()

    query = 'SELECT * FROM callcenter_reg.sip_user_status;'

    cursor.execute(query)

    res = cursor.fetchone()
    #  1000000000
    assert res == (
        'sip_1',
        'disconnected',
        'cool_sub_status',
        'disp',
        datetime.datetime(
            2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
        ),
        datetime.datetime(
            2018, 6, 21, 22, 0, tzinfo=pytz.FixedOffset(offset=180),
        ),
        1,
    )
