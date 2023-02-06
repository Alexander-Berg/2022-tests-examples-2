from aiohttp import web
import pytest

from taxi.util import dates

import crm_hub.generated.service.swagger.models.api as models


USER_ID = 'userid1'
UUID = 'uuuuuu'
DBID = 'dddddd'
DRIVER_ID = DBID + '_' + UUID
EVENT_ID = 'eventid1'


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment10',
    args=[{'name': 'entity_id', 'type': 'string', 'value': USER_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-11-20 10:00:00')
async def test_user_delayed_sending(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/user/notification/push')
    async def handler(request):
        return web.json_response({})

    event_ts = dates.utcnow()

    comm_body = models.NewCommunication(
        '00000000000000000000000000000010', USER_ID, EVENT_ID, event_ts,
    )
    await stq_runner.crm_hub_delayed_sendings.call(
        task_id='taskid1', args=(comm_body.serialize(),),
    )

    assert handler.times_called == 1


@pytest.mark.client_experiments3(
    consumer='crm_hub/communications',
    experiment_name='experiment11',
    args=[{'name': 'entity_id', 'type': 'string', 'value': DRIVER_ID}],
    value={'group_id': '1_testing'},
)
@pytest.mark.config(CRM_HUB_EXPERIMENT_CONSUMER='crm_hub/communications')
@pytest.mark.now('2019-12-20 10:00:00')
async def test_driver_delayed_sending(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/crm-policy/v1/check_update_send_message')
    async def _(request):
        return mockserver.make_response(status=200, json={'allowed': True})

    @mockserver.json_handler('/crm-admin/v1/trigger-campaigns/list')
    async def _(request):
        campaigns_list = load_json('trigger_campaigns_list.json')
        return mockserver.make_response(status=200, json=campaigns_list)

    @mockserver.json_handler('/ucommunications/driver/sms/send')
    async def handler(request):
        return web.json_response({'code': 'code', 'message': 'message'})

    event_ts = dates.utcnow()

    comm_body = models.NewCommunication(
        '00000000000000000000000000000011', DRIVER_ID, EVENT_ID, event_ts,
    )
    await stq_runner.crm_hub_delayed_sendings.call(
        task_id='taskid2', args=(comm_body.serialize(),),
    )

    assert handler.times_called == 1
