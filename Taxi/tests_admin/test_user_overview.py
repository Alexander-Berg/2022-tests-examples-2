# pylint: disable=import-error
import datetime

import common_pb2
from google.protobuf import timestamp_pb2
import mission_pb2
import pytest

MOCK_NOW = '2021-09-25T12:00:00+0000'
TS_AFTER_NOW = timestamp_pb2.Timestamp()
# pylint: disable=no-member
TS_AFTER_NOW.FromDatetime(
    datetime.datetime.fromisoformat('2021-09-25T13:00:00+00:00'),
)

TS_BEFORE_NOW = timestamp_pb2.Timestamp()
# pylint: disable=no-member
TS_BEFORE_NOW.FromDatetime(
    datetime.datetime.fromisoformat('2021-09-25T11:00:00+00:00'),
)
MISSION_IN_PROGRESS = mission_pb2.MissionStatus.MISSION_STATUS_IN_PROGRESS
PROGRESS_IN_PROGRESS = mission_pb2.ProgressStatus.PROGRESS_STATUS_IN_PROGRESS

EXPECTED_MC_REQUEST = dict(
    puid=123, customer=mission_pb2.Customer.CUSTOMER_LEVELS,
)
EXPECTED_MC_RESPONSE = dict(
    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
    mission=[
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_1',
            status=MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1', status=PROGRESS_IN_PROGRESS, current=2, target=5,
            ),
            # это задание вернется
            start_time=TS_BEFORE_NOW,
            stop_time=TS_AFTER_NOW,
            parameters={'some_param': 'some_val'},
            version=2,
            template_version=3,
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_only_mc',
            status=MISSION_IN_PROGRESS,
            template_id='task_template_id_2',
            counter_progress=mission_pb2.CounterProgress(
                id='1', status=PROGRESS_IN_PROGRESS, current=2, target=5,
            ),
            # это задание вернется
            start_time=TS_BEFORE_NOW,
            stop_time=TS_AFTER_NOW,
            parameters={'some_param': 'some_val'},
            version=2,
            template_version=3,
        ),
    ],
)


@pytest.mark.xfail(reason='broken test, will be fixed in TAXIBACKEND-39851')
@pytest.mark.parametrize(
    'yandex_uid, stage_id, response_file',
    [
        ('123', 'stage_1', 'expected_response_with_stage.json'),
        ('123', None, 'expected_response_without_stage.json'),
    ],
)
@pytest.mark.pgsql('cashback_levels', files=['user_overview.sql'])
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
async def test_user_overview_with_mock_response(
        taxi_cashback_levels,
        mock_mc_user_mission_service,
        load_json,
        yandex_uid,
        stage_id,
        response_file,
):
    grpc_mock = mock_mc_user_mission_service(
        [EXPECTED_MC_REQUEST], [EXPECTED_MC_RESPONSE],
    )
    url = f'admin/user/overview?yandex_uid={yandex_uid}' + (
        f'&stage_id={stage_id}' if stage_id else ''
    )
    async with grpc_mock:
        response = await taxi_cashback_levels.get(url)
        assert response.status == 200
        assert response.json() == load_json(response_file)
