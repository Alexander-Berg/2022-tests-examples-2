import dateutil.parser
import pytest
import pytz

from crm_admin import storage


def parse_datetime(string):
    time = dateutil.parser.parse(string)
    return time.astimezone(pytz.utc).replace(tzinfo=None)


@pytest.mark.parametrize(
    'campaign_id, start_time, stop_time, state, efficiency, code',
    [
        (
            1,
            '2021-01-05T13:00:01.127000+0000',
            '2021-01-25T14:00:01.127000+0000',
            'GROUPS_FINISHED',
            {
                '1': ['2021-01-10', '2021-01-20'],
                '2': ['2021-01-12', '2021-01-18'],
            },
            200,
        ),
        (
            1,
            '2021-01-11T13:00:01.127000+0000',
            '2021-01-19T14:00:01.127000+0000',
            'GROUPS_FINISHED',
            {
                '1': ['2021-01-11', '2021-01-19'],
                '2': ['2021-01-12', '2021-01-18'],
            },
            200,
        ),
        (
            2,
            '2021-01-11T03:00:01.127000+0000',
            '2021-01-19T03:00:01.127000+0000',
            'VERIFY_FINISHED',
            {
                '3': ['2021-01-12', '2021-01-18'],
                '4': ['2021-01-11', '2021-01-19'],
            },
            200,
        ),
        (
            3,
            '2021-01-02T03:00:01.127000+0000',
            '2021-01-08T03:00:01.127000+0000',
            'CAMPAIGN_APPROVED',
            {
                '5': ['2021-01-02', '2021-01-08'],
                '6': ['2021-01-02', '2021-01-08'],
            },
            424,
        ),
        (
            3,
            '2020-01-01T03:00:01.127000+0000',
            '2021-01-03T03:00:01.127000+0000',
            'CAMPAIGN_APPROVED',
            {
                '5': ['2021-01-02', '2021-01-08'],
                '6': ['2021-01-02', '2021-01-08'],
            },
            424,
        ),
        (
            3,
            '2021-01-02T03:00:01.127000+0000',
            '2021-01-08T03:00:01.127000+0000',
            'CAMPAIGN_APPROVED',
            {
                '5': ['2021-01-02', '2021-01-08'],
                '6': ['2021-01-02', '2021-01-08'],
            },
            424,
        ),
        (
            3,
            '2021-01-30T03:00:01.127000+0000',
            '2021-01-20T03:00:01.127000+0000',
            None,
            None,
            424,
        ),
        (
            100,
            '2021-01-20T03:00:01.127000+0000',
            '2021-01-30T03:00:01.127000+0000',
            None,
            None,
            404,
        ),
    ],
)
@pytest.mark.config(
    CRM_ADMIN_EFFICIENCY_SETTINGS={
        'efficiency_resolution_sla_in_hours': {'User': 150, 'Driver': 300},
    },
)
@pytest.mark.now('2021-01-01 17:01:00')
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_update_efficiency_period(
        web_context,
        web_app_client,
        campaign_id,
        start_time,
        stop_time,
        state,
        efficiency,
        code,
):
    data = dict(
        efficiency_start_time=start_time, efficiency_stop_time=stop_time,
    )

    response = await web_app_client.put(
        '/v1/campaigns/schedule', params={'id': campaign_id}, json=data,
    )

    assert response.status == code
    if code == 200:
        campaign_storage = storage.DbCampaign(web_context)
        campaign = await campaign_storage.fetch(campaign_id)

        _start = campaign.efficiency_start_time
        assert _start == parse_datetime(start_time)

        _stop = campaign.efficiency_stop_time
        assert _stop == parse_datetime(stop_time)

        assert campaign.state == state

        group_storage = storage.DbGroup(web_context)
        groups = await group_storage.fetch_by_segment(campaign.segment_id)

        for group in groups:
            _id = str(group.group_id)
            assert group.params.efficiency_date[0] == efficiency[_id][0]
            assert group.params.efficiency_date[1] == efficiency[_id][1]


@pytest.mark.parametrize(
    'campaign_id, schedule, code',
    [
        (4, '5 * * * *', 200),
        (5, '*/10 * * * *', 200),
        (6, '2 2 * * *', 200),
        (100, '2 2 * * *', 404),
    ],
)
@pytest.mark.pgsql('crm_admin', files=['init_schedule.sql'])
async def test_update_regular_schedule(
        web_context, web_app_client, campaign_id, schedule, code,
):
    data = dict(schedule=schedule)

    response = await web_app_client.put(
        '/v1/campaigns/schedule', params={'id': campaign_id}, json=data,
    )

    assert response.status == code
    if code == 200:
        campaign_storage = storage.DbCampaign(web_context)
        campaign = await campaign_storage.fetch(campaign_id)
        assert campaign.schedule == schedule
