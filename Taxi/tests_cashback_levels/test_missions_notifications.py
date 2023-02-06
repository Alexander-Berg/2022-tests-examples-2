import typing

import pytest

from . import common

UID = 123


def get_rid_of_ids(objects):
    for obj in objects:
        del obj['id']


async def post_missions_notifications(taxi_cashback_levels, path, headers):
    return await taxi_cashback_levels.post(path, headers=headers)


class MyTestCase(typing.NamedTuple):
    path: str = '/cashback-levels/v1/missions/notifications'
    headers: typing.Dict = {
        'X-Yandex-UID': str(UID),
        'X-Request-Language': 'ru',
        'X-Request-Application': common.X_REQUEST_APPLICATION_HEADER,
    }


@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(path='/cashback-levels/v1/missions/notifications'),
            id='internal_path',
        ),
        pytest.param(
            MyTestCase(path='/4.0/cashback-levels/v1/missions/notifications'),
            id='client_path',
        ),
    ],
)
async def test_missions_notifications_no_config(taxi_cashback_levels, case):
    resp = await post_missions_notifications(
        taxi_cashback_levels, case.path, case.headers,
    )
    assert resp.status == 500


@pytest.mark.experiments3(
    filename='config3_cashback_tasks_app_notifications.json',
)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(path='/cashback-levels/v1/missions/notifications'),
            id='internal_path',
        ),
        pytest.param(
            MyTestCase(path='/4.0/cashback-levels/v1/missions/notifications'),
            id='client_path',
        ),
    ],
)
async def test_missions_notifications_empty_db(taxi_cashback_levels, case):
    resp = await post_missions_notifications(
        taxi_cashback_levels, case.path, case.headers,
    )
    assert resp.status == 200

    resp_body = resp.json()
    assert resp_body == {'notifications': []}


@pytest.mark.config(
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
@pytest.mark.pgsql(
    'cashback_levels', files=['missions_notifications_test.sql'],
)
@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'case',
    [
        pytest.param(
            MyTestCase(path='/cashback-levels/v1/missions/notifications'),
            id='internal_path',
        ),
        pytest.param(
            MyTestCase(path='/4.0/cashback-levels/v1/missions/notifications'),
            id='client_path',
        ),
    ],
)
async def test_missions_notifications_basic(
        taxi_cashback_levels, load_json, case,
):
    resp = await post_missions_notifications(
        taxi_cashback_levels, case.path, case.headers,
    )
    assert resp.status == 200

    resp_body = resp.json()
    get_rid_of_ids(resp_body['notifications'])
    assert resp_body == load_json('expected_response.json')
