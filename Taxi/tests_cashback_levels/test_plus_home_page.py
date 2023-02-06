# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing

import common_pb2
import mission_pb2
import pytest

from . import common

MISSION_ACHIEVED = mission_pb2.MissionStatus.MISSION_STATUS_ACHIEVED
MISSION_COMPLETED = mission_pb2.MissionStatus.MISSION_STATUS_COMPLETED
MISSION_NOT_ACCEPTED = mission_pb2.MissionStatus.MISSION_STATUS_NOT_ACCEPTED

PROGRESS_COMPLETED = mission_pb2.ProgressStatus.PROGRESS_STATUS_COMPLETED
RESPONSE_STATUS_SUCCESS = common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS

EXPECTED_GET_MISSIONS_REQUEST = dict(
    puid=123, customer=mission_pb2.Customer.CUSTOMER_LEVELS,
)

EXPECTED_RESPONSE = dict(
    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
    mission=[
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_1',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=2,
                target=5,
            ),
            # это задание вернется
            start_time=common.TS_BEFORE_NOW,
            stop_time=common.TS_AFTER_NOW,
        ),
    ],
)


async def post_plushome_page(taxi_cashback_levels, service='service'):
    return await taxi_cashback_levels.get(
        '/cashback-levels/v2/plus/home/page',
        params={'passportUid': '123', 'service': service},
        headers={'Accept-Language': 'ru'},
    )


class MyTestCase(typing.NamedTuple):
    EXPECTED_GET_MISSIONS_REQUESTs: list = [EXPECTED_GET_MISSIONS_REQUEST]
    expected_responses: list = [EXPECTED_RESPONSE]
    service: str = 'market'
    expected_response_file: str = 'expected_plus_home_page.json'
    resp_code: int = 200
    resp_err_msg: str = ''


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(
    filename='config_cashback_levels_plushome_show_params.json',
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_shortcuts.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize('case', [pytest.param(MyTestCase(), id='happy_path')])
async def test_happy_path(
        case, taxi_cashback_levels, load_json, mock_mc_user_mission_service,
):
    async with mock_mc_user_mission_service(
            case.EXPECTED_GET_MISSIONS_REQUESTs, case.expected_responses,
    ):
        resp = await post_plushome_page(
            taxi_cashback_levels, service=case.service,
        )
        assert resp.status == case.resp_code

        resp_body = resp.json()
        if case.resp_err_msg:
            assert resp_body['code'] == str(case.resp_code)
            assert resp_body['message'] == case.resp_err_msg
        else:
            assert resp_body == load_json(case.expected_response_file)
