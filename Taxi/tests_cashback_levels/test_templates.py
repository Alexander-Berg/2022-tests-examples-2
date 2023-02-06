# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import enum
import typing

import common_pb2
import mission_pb2
import pytest

from . import common

YANDEX_UID = 123

EXPECTED_GET_MISSIONS_REQUEST = dict(
    puid=YANDEX_UID, customer=mission_pb2.Customer.CUSTOMER_LEVELS,
)


class Flag(enum.Enum):
    HAPPY_PATH = 0
    EMPTY_MISSIONS_FROM_MC = 1
    WITHOUT_TARIFFS = 2
    WITH_ORDER_ID = 3


def expected_get_missions_response(
        flag: Flag,
        start_time=common.TS_BEFORE_NOW,
        stop_time=common.TS_AFTER_NOW,
):
    if flag == Flag.EMPTY_MISSIONS_FROM_MC:
        return dict(
            status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
            mission=[],
        )
    if flag == Flag.WITHOUT_TARIFFS:
        return dict(
            status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
            mission=[
                mission_pb2.UserMission(
                    puid=YANDEX_UID,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task_id_2',
                    status=common.MISSION_IN_PROGRESS,
                    template_id='task_template_id_2',
                    counter_progress=mission_pb2.CounterProgress(
                        id='1',
                        status=common.PROGRESS_IN_PROGRESS,
                        current=2,
                        target=12,
                    ),
                    # это задание вернется
                    start_time=start_time,
                    stop_time=stop_time,
                ),
            ],
        )
    if flag == Flag.WITH_ORDER_ID:
        return dict(
            status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
            mission=[
                mission_pb2.UserMission(
                    puid=YANDEX_UID,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task_id_3',
                    status=common.MISSION_IN_PROGRESS,
                    template_id='task_template_id_3',
                    counter_progress=mission_pb2.CounterProgress(
                        id='1',
                        status=common.PROGRESS_IN_PROGRESS,
                        current=10,
                        target=15,
                    ),
                    # это задание вернется
                    start_time=start_time,
                    stop_time=stop_time,
                ),
                mission_pb2.UserMission(
                    puid=YANDEX_UID,
                    customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                    external_id='task_id_5',
                    status=common.MISSION_IN_PROGRESS,
                    template_id='task_template_id_5',
                    counter_progress=mission_pb2.CounterProgress(
                        id='1',
                        status=common.PROGRESS_IN_PROGRESS,
                        current=10,
                        target=15,
                    ),
                    # это задание не вернется, т.к. не прошло
                    # 20 минут после просмотра нотификации
                    start_time=start_time,
                    stop_time=stop_time,
                ),
            ],
        )
    return dict(
        status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
        mission=[
            mission_pb2.UserMission(
                puid=YANDEX_UID,
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
                puid=YANDEX_UID,
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
                # это задание не вернется, так как не попадает в окно действия
                start_time=common.TS_AFTER_NOW,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_1',
                # это задание не вернется, так как оно завершено
                status=common.MISSION_COMPLETED,
                template_id='task_template_id_1',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.PROGRESS_COMPLETED,
                    current=5,
                    target=5,
                ),
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                # это задание не вернется, так как его нет в конфиге
                # cashback_available_tasks_descriptions_for_market_plaque
                external_id='task_id_4',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_3',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=2,
                    target=5,
                ),
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_id_5',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_5',
                counter_progress=mission_pb2.CounterProgress(
                    id='1',
                    status=common.PROGRESS_IN_PROGRESS,
                    current=10,
                    target=15,
                ),
                # это задание не вернется, т.к. не прошло
                # 20 минут после просмотра нотификации
                start_time=start_time,
                stop_time=stop_time,
            ),
        ],
    )


async def get_templates(taxi_cashback_levels):
    path = f'/internal/cashback-levels/v1/plaque/templates?uid={YANDEX_UID}'

    return await taxi_cashback_levels.get(
        path, headers={'X-Request-Language': 'ru'},
    )


class MyTestCase(typing.NamedTuple):
    flag: Flag = Flag.HAPPY_PATH
    expected_response_file: str = 'expected_response.json'


async def test_templates_without_configs(taxi_cashback_levels):
    resp = await get_templates(taxi_cashback_levels)
    assert resp.status == 500


@pytest.mark.config(
    CASHBACK_LEVELS_MISSION_CONTROL_ENDPOINTS=['localhost:1083'],
    CASHBACK_LEVELS_TARIFF_NAME_ORDER_MAPPING=common.CASHBACK_LEVELS_TARIFF_NAME_ORDER_MAPPING,  # noqa: E501
)
@pytest.mark.experiments3(
    filename='config3_cashback_tasks_app_notifications.json',
)
@pytest.mark.experiments3(
    filename='config3_cashback_available_tasks_descriptions_for_market_plaque.json',  # noqa: E501
)
@pytest.mark.experiments3(
    filename='config3_cashback_levels_product_time_to_enable_templates.json',
)
@pytest.mark.translations(
    client_messages=common.MISSION_TEMPLATES_CLIENT_MESSAGES,
)
@pytest.mark.pgsql(
    'cashback_levels',
    files=['template_order_id_test.sql', 'template_time_to_show_test.sql'],
)
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(flag=Flag.HAPPY_PATH), id='happy_path'),
        pytest.param(
            MyTestCase(flag=Flag.EMPTY_MISSIONS_FROM_MC),
            id='not_found_missions',
        ),
        pytest.param(
            MyTestCase(
                flag=Flag.WITHOUT_TARIFFS,
                expected_response_file='expected_response_without_selected_tariffs.json',  # noqa: E501
            ),
            id='without_selected_tariffs',
        ),
        pytest.param(
            MyTestCase(
                flag=Flag.WITH_ORDER_ID,
                expected_response_file='expected_response_with_order_id.json',
            ),
            id='with_order_id',
        ),
    ],
)
async def test_templates(
        taxi_cashback_levels,
        load_json,
        mock_mc_user_mission_service,
        case,
        mocked_time,
):
    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST],
            [expected_get_missions_response(case.flag)],
    ):
        resp = await get_templates(taxi_cashback_levels)
        expected_code = 200
        if case.flag == Flag.EMPTY_MISSIONS_FROM_MC:
            expected_code = 404
        assert resp.status == expected_code

        if expected_code == 200:
            resp_body = resp.json()
            assert resp_body == load_json(case.expected_response_file)
