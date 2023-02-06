# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import typing

import common_pb2
import mission_pb2
import pytest

from . import common

STAGES_DESCRIPTION = {
    'stage1': {
        'start_time': '2021-08-25T12:00:00+0000',
        'end_time': '2021-11-25T12:00:00+0000',
        'stage_id': 'stage1',
        'next_stage_id': 'stage2',
        'top_size': 4,
    },
}


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
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_3',
            status=MISSION_COMPLETED,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1', status=PROGRESS_COMPLETED, current=5, target=5,
            ),
            # это задание вернется
            start_time=common.TS_BEFORE_NOW,
            stop_time=common.TS_AFTER_NOW,
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_2',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_2',
            cyclic_progress=mission_pb2.CyclicProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=10000,
                target=20000,
                current_completed_iteration=2,
                target_completed_iteration=10,
            ),
            # это задание вернется
            start_time=common.TS_BEFORE_NOW,
            stop_time=common.TS_AFTER_NOW,
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_4',
            status=MISSION_ACHIEVED,
            template_id='task_template_id_2',
            cyclic_progress=mission_pb2.CyclicProgress(
                id='1',
                status=PROGRESS_COMPLETED,
                current=0,
                target=100,
                current_completed_iteration=15,
                target_completed_iteration=15,
            ),
            # это задание вернется
            start_time=common.TS_BEFORE_NOW,
            stop_time=common.TS_AFTER_NOW,
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_with_non_positive_left_progress',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=6,
                target=5,
            ),
            # это задание не вернется, так как у него прогресс уже перевыполнен
            start_time=common.TS_BEFORE_NOW,
            stop_time=common.TS_AFTER_NOW,
        ),
    ],
)

EXTENDED_RESPONSE_FOR_SORT = dict(
    status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
    mission=[
        *EXPECTED_RESPONSE['mission'],
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_5',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=1,
                target=10,
            ),
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_6',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=1,
                target=100,
            ),
        ),
        mission_pb2.UserMission(
            puid=123,
            customer=mission_pb2.Customer.CUSTOMER_LEVELS,
            external_id='task_id_7',
            status=common.MISSION_IN_PROGRESS,
            template_id='task_template_id_1',
            counter_progress=mission_pb2.CounterProgress(
                id='1',
                status=common.PROGRESS_IN_PROGRESS,
                current=1,
                target=100,
            ),
        ),
    ],
)


async def post_levels_info(taxi_cashback_levels, service='service'):
    return await taxi_cashback_levels.post(
        '/v1/plus-levels/info',
        params={'uid': '123', 'service': service},
        headers={'Accept-Language': 'ru'},
    )


async def insert_default_user(cursor):
    cursor.execute(
        f"""
        INSERT INTO cashback_levels.users(
            yandex_uid, current_used_level, current_earned_level, stage_id
        )
        VALUES {'123', 1, 1, 'stage1'};
    """,
    )


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
async def test_plus_levels_info_no_tasks_config(taxi_cashback_levels):
    resp = await post_levels_info(taxi_cashback_levels)
    assert resp.status == 500


@pytest.mark.experiments3(filename='exp3_return_user_info_disabled.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
async def test_plus_levels_info_404_on_exp_disabled(taxi_cashback_levels):
    resp = await post_levels_info(taxi_cashback_levels)
    assert resp.status == 404


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
async def test_plus_levels_info_no_levels_config(taxi_cashback_levels):
    resp = await post_levels_info(taxi_cashback_levels)
    assert resp.status == 500


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
@pytest.mark.now(common.MOCK_NOW)
async def test_plus_levels_info_no_mission_control_endpoints_config(
        taxi_cashback_levels, pgsql,
):
    await insert_default_user(pgsql['cashback_levels'].cursor())
    resp = await post_levels_info(taxi_cashback_levels)
    assert resp.status == 500


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:83'])
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
async def test_plus_levels_info_invalid_mission_control_endpoints(
        taxi_cashback_levels, mock_mc_user_mission_service, pgsql,
):
    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST], [EXPECTED_RESPONSE],
    ):
        await insert_default_user(pgsql['cashback_levels'].cursor())
        resp = await post_levels_info(taxi_cashback_levels)
        assert resp.status == 500


class MyTestCase(typing.NamedTuple):
    EXPECTED_GET_MISSIONS_REQUESTs: list = [EXPECTED_GET_MISSIONS_REQUEST]
    expected_responses: list = [EXPECTED_RESPONSE]
    service: str = 'service'
    users_setup_params: typing.List = []
    sort: typing.Optional[str] = None
    expected_response_file: str = 'expected_plus_levels_info.json'
    resp_code: int = 200
    resp_err_msg: str = ''


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(
                resp_code=404,
                resp_err_msg='Missions not found for uid=123',
                expected_responses=[
                    {'status': RESPONSE_STATUS_SUCCESS, 'mission': []},
                ],
            ),
            id='no_missions_for_user',
        ),
        pytest.param(
            MyTestCase(users_setup_params=['(\'123\', 1, 1, \'stage1\')']),
            id='user_has_next_level',
        ),
        pytest.param(
            MyTestCase(
                users_setup_params=['(\'123\', 2, 2, \'stage1\')'],
                expected_response_file='expected_plus_levels_info_no_next_level.json',  # noqa: E501
            ),
            id='user_does_not_have_next_level',
        ),
        pytest.param(
            MyTestCase(
                service='go',
                users_setup_params=['(\'123\', 2, 2, \'stage1\')'],
                expected_response_file='expected_plus_levels_info_go_button_url.json',  # noqa: E501
            ),
            id='user_has_task_with_go_button_url',
        ),
    ],
)
async def test_plus_levels_info_basic_flow(
        case,
        taxi_cashback_levels,
        pgsql,
        load_json,
        mock_mc_user_mission_service,
):
    async with mock_mc_user_mission_service(
            case.EXPECTED_GET_MISSIONS_REQUESTs, case.expected_responses,
    ):
        cursor = pgsql['cashback_levels'].cursor()
        for params in case.users_setup_params:
            cursor.execute(
                f"""
                INSERT INTO cashback_levels.users(
                    yandex_uid, current_used_level,
                    current_earned_level, stage_id
                )
                VALUES {params};
            """,
            )

        resp = await post_levels_info(
            taxi_cashback_levels, service=case.service,
        )
        assert resp.status == case.resp_code

        resp_body = resp.json()
        if case.resp_err_msg:
            assert resp_body['code'] == str(case.resp_code)
            assert resp_body['message'] == case.resp_err_msg
        else:
            assert resp_body['payload'] == load_json(
                case.expected_response_file,
            )


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
@pytest.mark.parametrize(
    'expected_response_file',
    [
        pytest.param(
            'expected_plus_levels_info_test_do_not_return_missions.json',
            id='missions_that_havent_started_yet',
        ),
    ],
)
async def test_plus_levels_info_do_not_return_missions(
        expected_response_file,
        taxi_cashback_levels,
        load_json,
        mock_mc_user_mission_service,
):
    mock_response = dict(
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
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_2',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_2',
                cyclic_progress=mission_pb2.CyclicProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=10000,
                    target=20000,
                    current_completed_iteration=2,
                    target_completed_iteration=10,
                ),
                # целиком в прошлом, это задание не вернется
                start_time=common.TS_BEFORE_NOW,
                stop_time=common.TS_BEFORE_NOW,
            ),
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_3',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=4,
                    target=5,
                ),
                # если stop_time не указан, то задание не имеет срока окончания
                # и должно возвращаться
                start_time=common.TS_BEFORE_NOW,
            ),
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_4',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_2',
                cyclic_progress=mission_pb2.CyclicProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=0,
                    target=100,
                    current_completed_iteration=15,
                    target_completed_iteration=15,
                ),
                # целиком в будущем, это задание не вернется
                start_time=common.TS_AFTER_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
        ],
    )

    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST], [mock_response],
    ):
        resp = await post_levels_info(taxi_cashback_levels)
        assert resp.status == 200
        assert resp.json()['payload'] == load_json(expected_response_file)


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
@pytest.mark.parametrize(
    'expected_response_file',
    [
        pytest.param(
            'expected_plus_levels_info_missions_from_multiple_stages.json',
            id='missions_from_multiple_stages',
        ),
    ],
)
async def test_plus_levels_info_missions_from_multiple_stages(
        expected_response_file,
        taxi_cashback_levels,
        load_json,
        mock_mc_user_mission_service,
):
    mock_response = dict(
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
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_with_stage2',
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

    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST], [mock_response],
    ):
        resp = await post_levels_info(taxi_cashback_levels)
        assert resp.status == 200
        assert resp.json()['payload'] == load_json(expected_response_file)


@pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
)
@pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
@pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
@pytest.mark.parametrize(
    'expected_response_file',
    [
        pytest.param(
            'expected_plus_levels_info_missions_from_multiple_stages.json',
            id='missions_from_multiple_stages',
        ),
    ],
)
async def test_plus_levels_info_accept(
        expected_response_file,
        taxi_cashback_levels,
        load_json,
        mock_mc_user_mission_service,
):
    mock_get_missions_response = dict(
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
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_with_stage2',
                status=MISSION_NOT_ACCEPTED,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1', status=MISSION_NOT_ACCEPTED, current=2, target=5,
                ),
                # это задание вернется
                start_time=common.TS_BEFORE_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_with_stage2_no_accept_by_view',
                status=MISSION_NOT_ACCEPTED,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1', status=MISSION_NOT_ACCEPTED, current=2, target=5,
                ),
                # для него выключен акцепт по просмотру в домике
                # и мы его не запросим его акцепт и не вернем его в ответе
                start_time=common.TS_BEFORE_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_2',
                status=MISSION_NOT_ACCEPTED,
                template_id='endless-Х-spend-money',
                counter_progress=mission_pb2.CounterProgress(
                    id='1', status=MISSION_NOT_ACCEPTED, current=2, target=5,
                ),
                # предположим, что в ручке accept что-то пойдет не так
                # она не обработает это задание, не вернет его в своем ответе
                # и мы его не вернем в своем
                start_time=common.TS_BEFORE_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_5',
                status=MISSION_NOT_ACCEPTED,
                template_id='make-X-eda-orders',
                counter_progress=mission_pb2.CounterProgress(
                    id='1', status=MISSION_NOT_ACCEPTED, current=2, target=5,
                ),
                # это задание еще не действует и мы не запросим его акцепт
                start_time=common.TS_AFTER_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
        ],
    )
    mock_accept_response = dict(
        status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
        mission=[
            mission_pb2.UserMission(
                puid=123,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_with_stage2',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.MISSION_IN_PROGRESS,
                    current=2,
                    target=5,
                ),
                # это задание вернется
                start_time=common.TS_BEFORE_NOW,
                stop_time=common.TS_AFTER_NOW,
            ),
        ],
    )
    expected_accept_request = dict(
        puid=123,
        customer=mission_pb2.Customer.CUSTOMER_LEVELS,
        external_id=['task_with_stage2', 'task_id_2'],
    )
    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST, expected_accept_request],
            [mock_get_missions_response, mock_accept_response],
    ) as service:
        resp = await post_levels_info(taxi_cashback_levels)
        assert resp.status == 200
        assert resp.json()['payload'] == load_json(expected_response_file)

        assert service.servicer.accept_missions_called == 1


# Sorting is currently disabled.
# @pytest.mark.experiments3(filename='exp3_return_user_info_enabled.json')
# @pytest.mark.config(
#     CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
# )
# @pytest.mark.experiments3(filename='config3_cashback_levels_description.json')
# @pytest.mark.experiments3(filename='config3_cashback_tasks_description.json')
# @pytest.mark.experiments3(filename='config3_cashback_tasks_offers.json')
# @pytest.mark.now('2021-09-25T12:00:00+0000')
# @pytest.mark.config(CASHBACK_LEVELS_STAGES_DESCRIPTION=STAGES_DESCRIPTION)
# @pytest.mark.parametrize(
#     'case',
#     [
#         pytest.param(
#             MyTestCase(
#                 users_setup_params=['(\'123\', 1, 1, \'stage1\')'],
#                 sort=None,
#                 expected_response_file='expected_plus_levels_info_no_sort.json',  # noqa: E501
#             ),
#             id='no_sort',
#         ),
#         pytest.param(
#             MyTestCase(
#                 users_setup_params=['(\'123\', 1, 1, \'stage1\')'],
#                 sort='as-is',
#                 expected_response_file='expected_plus_levels_info_no_sort.json',  # noqa: E501
#             ),
#             id='as-is',
#         ),
#         pytest.param(
#             MyTestCase(
#                 users_setup_params=['(\'123\', 1, 1, \'stage1\')'],
#                 sort='random',
#                 expected_response_file='expected_plus_levels_info_sort_random.json',  # noqa: E501
#             ),
#             id='random',
#         ),
#         pytest.param(
#             MyTestCase(
#                 users_setup_params=['(\'123\', 1, 1, \'stage1\')'],
#                 sort='random_with_top',
#                 expected_response_file='expected_plus_levels_info_sort_random_with_top.json',  # noqa: E501
#             ),
#             id='random_with_top',
#         ),
#     ],
# )
# async def test_plus_levels_info_sort(
#         case,
#         taxi_cashback_levels,
#         pgsql,
#         load_json,
#         mock_mc_user_mission_service,
#         taxi_config,
# ):
#     async with mock_mc_user_mission_service(
#             [EXPECTED_GET_MISSIONS_REQUEST], [EXTENDED_RESPONSE_FOR_SORT],
#     ):
#         if case.sort is not None:
#             stages_config = copy.deepcopy(STAGES_DESCRIPTION)
#             stages_config['stage1']['sort'] = case.sort
#             taxi_config.set(CASHBACK_LEVELS_STAGES_DESCRIPTION=stages_config)
#
#         cursor = pgsql['cashback_levels'].cursor()
#         for params in case.users_setup_params:
#             cursor.execute(
#                 f"""
#                 INSERT INTO cashback_levels.users(
#                     yandex_uid, current_used_level,
#                     current_earned_level, stage_id
#                 )
#                 VALUES {params};
#             """,
#             )
#
#         resp = await post_levels_info(taxi_cashback_levels)
#         assert resp.status == case.resp_code
#
#         resp_body = resp.json()
#         if case.resp_err_msg:
#             assert resp_body['code'] == str(case.resp_code)
#             assert resp_body['message'] == case.resp_err_msg
#         else:
#             assert resp_body['payload'] == load_json(
#                 case.expected_response_file,
#             )
