# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import enum
import typing

import common_pb2
import mission_pb2
import pytest

from . import common

YANDEX_UID = 123
MARKET_SERVICE_NAME = 'market'

EXPECTED_GET_MISSIONS_REQUEST = dict(
    puid=YANDEX_UID, customer=mission_pb2.Customer.CUSTOMER_LEVELS,
)

MISSION_TEMPLATES_CLIENT_MESSAGES = {
    'several_tasks_description_completed': {
        'ru': [
            '%(value)s завершенная задача',
            '%(value)s завершенные задачи',
            '%(value)s завершенных задач',
        ],
    },
    'several_tasks_description_new': {
        'ru': ['%(value)s новые задачи', '%(value)s новых задач'],
    },
    'several_tasks_description_in_progress': {
        'ru': ['%(value)s законченные задачи', '%(value)s законченных задач'],
    },
    'first_task_description_completed': {
        'ru': ['описание первой законченной задачки'],
    },
    'second_task_description_completed': {
        'ru': ['описание второй законченной задачки'],
    },
    'task_description_new': {'ru': ['описание новой задачки']},
    'task_description_in_progress': {'ru': ['описание задачки в прогрессе']},
}


class Flag(enum.Enum):
    HAPPY_PATH = 0
    WITHOUT_SERVICE = 1


def get_mс_response(
        start_time=common.TS_BEFORE_NOW, stop_time=common.TS_AFTER_NOW,
):
    return dict(
        status=common_pb2.ResponseStatus.RESPONSE_STATUS_SUCCESS,
        mission=[
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='new_task_id',
                status=common.NEW_MISSION,
                template_id='task_template_id_1',
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='task_in_progress',
                status=common.MISSION_IN_PROGRESS,
                template_id='task_template_id_1',
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='completed_task_1',
                status=common.MISSION_COMPLETED,
                template_id='task_template_id_1',
                start_time=start_time,
                stop_time=stop_time,
            ),
            mission_pb2.UserMission(
                puid=YANDEX_UID,
                customer=mission_pb2.Customer.CUSTOMER_LEVELS,
                external_id='completed_task_2',
                status=common.MISSION_COMPLETED,
                template_id='task_template_id_1',
                start_time=start_time,
                stop_time=stop_time,
            ),
        ],
    )


async def get_templates(taxi_cashback_levels):
    path = f'/internal/cashback-levels/v2/plaque/templates?uid={YANDEX_UID}&ya_service={MARKET_SERVICE_NAME}'

    return await taxi_cashback_levels.get(
        path, headers={'X-Request-Language': 'ru'},
    )


async def get_templates_without_service(taxi_cashback_levels):
    path = f'/internal/cashback-levels/v2/plaque/templates?uid={YANDEX_UID}'

    return await taxi_cashback_levels.get(
        path, headers={'X-Request-Language': 'ru'},
    )


async def get_templates_without_service(taxi_cashback_levels):
    path = f'/internal/cashback-levels/v2/plaque/templates?uid={YANDEX_UID}'

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
    filename='config3_cashback_levels_cross_service_tasks_priorities.json',
)
@pytest.mark.experiments3(
    filename='config3_cashback_levels_cross_service_tasks_descriptions.json',
)
@pytest.mark.experiments3(
    filename='config3_cashback_levels_cross_service_several_tasks_descriptions.json',
)
@pytest.mark.translations(client_messages=MISSION_TEMPLATES_CLIENT_MESSAGES)
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(MyTestCase(flag=Flag.HAPPY_PATH), id='happy_path'),
        pytest.param(
            MyTestCase(flag=Flag.WITHOUT_SERVICE), id='without_service',
        ),
    ],
)
async def test_cross_service_templates(
        taxi_cashback_levels,
        load_json,
        mock_mc_user_mission_service,
        case,
        mocked_time,
):
    async with mock_mc_user_mission_service(
            [EXPECTED_GET_MISSIONS_REQUEST], [get_mс_response()],
    ):
        if case.flag == Flag.HAPPY_PATH:
            resp = await get_templates(taxi_cashback_levels)
            assert resp.status == 200
            resp_body = resp.json()
            assert resp_body == load_json(case.expected_response_file)
        elif case.flag == Flag.WITHOUT_SERVICE:
            resp = await get_templates_without_service(taxi_cashback_levels)
            assert resp.status == 400
