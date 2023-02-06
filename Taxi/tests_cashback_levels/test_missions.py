import typing

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import common_pb2
from google.protobuf import timestamp_pb2
import mission_pb2
import pytest

from . import common

UID = 123

EXPECTED_GET_MISSIONS_REQUEST = dict(
    puid=UID, customer=mission_pb2.Customer.CUSTOMER_LEVELS,
)


def expected_get_missions_response(
        start_time=common.TS_BEFORE_NOW, stop_time=common.TS_AFTER_NOW,
):
    return dict(
        status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
        mission=[
            mission_pb2.UserMission(
                puid=UID,
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
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_2',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=2,
                    target=5,
                ),
                # это задание не вернется, так как не попадает в окно действия
                start_time=common.TS_AFTER_NOW,
            ),
        ],
    )


async def post_missions(taxi_cashback_levels, mission_id=None):
    path = '/4.0/cashback-levels/v1/missions'
    if mission_id:
        path += '?mission_id=' + mission_id

    return await taxi_cashback_levels.post(
        path,
        headers={
            'X-Yandex-UID': str(UID),
            'X-Request-Language': 'ru',
            'X-Request-Application': common.X_REQUEST_APPLICATION_HEADER,
        },
    )


class MyTestCase(typing.NamedTuple):
    query_mission_id: typing.Optional[str] = None
    start_time: timestamp_pb2.Timestamp = common.TS_BEFORE_NOW
    stop_time: timestamp_pb2.Timestamp = common.TS_AFTER_NOW
    expected_response_file: str = 'expected_response.json'


async def test_missions_no_task_notifications_config(taxi_cashback_levels):
    resp = await post_missions(taxi_cashback_levels)
    assert resp.status == 500


@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
    EXTENDED_TEMPLATE_STYLES_MAP={
        'cashback_levels_reward_icon': {'width': 15, 'height': 30},
        'cashback_levels_reward_text': {
            'font_size': 15,
            'font_weight': 'bold',
        },
    },
)
@pytest.mark.experiments3(
    filename='config3_cashback_tasks_app_notifications.json',
)
@pytest.mark.translations(
    client_messages=common.MISSIONS_NOTIFICATIONS_CLIENT_MESSAGES,
)
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(), id='basic'),
        pytest.param(
            MyTestCase(query_mission_id='task_id_1'),
            id='with_query_mission_id',
        ),
        pytest.param(
            MyTestCase(
                stop_time=common.TS_1_DAY_AFTER_NOW,
                expected_response_file='expected_response_1_day_left.json',
            ),
            id='with_1_day_left',
        ),
    ],
)
async def test_missions(
        taxi_cashback_levels, load_json, mock_mc_user_mission_service, case,
):
    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST],
            [expected_get_missions_response(case.start_time, case.stop_time)],
    ):
        resp = await post_missions(taxi_cashback_levels, case.query_mission_id)
        assert resp.status == 200

        resp_body = resp.json()
        assert resp_body == load_json(case.expected_response_file)
