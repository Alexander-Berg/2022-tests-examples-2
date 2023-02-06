import datetime

import pytest

from crm_admin.generated.service.swagger import models
from test_crm_admin.web.test_targets import utils


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_create_period(web_context, web_app_client):
    start_at = datetime.datetime.fromisoformat('2023-03-23T02:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )

    expected_result = models.api.PeriodGet(
        control=models.api.Control(
            control_percentage=5, key='phone_pd_id', salt=utils.EVERY_SALT,
        ),
        created_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        updated_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        id=1,
        owner=utils.OWNER_OF_ALL,
        start_at=start_at,
        previous_control_percentage=50,
    ).serialize()
    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_get_periods(web_context, web_app_client):
    start_at_1 = datetime.datetime.fromisoformat('2023-03-23T02:22:22+03:00')
    start_at_2 = datetime.datetime.fromisoformat('2024-04-24T02:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at_1,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200
    period_id_1 = await response.json()
    period_id_1 = period_id_1['id']

    period_body.start_at = start_at_2

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200
    period_id_2 = await response.json()
    period_id_2 = period_id_2['id']

    response = await web_app_client.get(f'/v1/targets/{target_id}/periods')
    assert response.status == 200

    period_get_body = models.api.PeriodGet(
        control=models.api.Control(
            control_percentage=period_body.control_percentage,
            key=period_body.key,
            salt=utils.EVERY_SALT,
        ),
        created_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        updated_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        id=period_id_1,
        owner=utils.OWNER_OF_ALL,
        start_at=start_at_1,
        previous_control_percentage=period_body.previous_control_percentage,
    )
    expected_result = list()
    expected_result.append(period_get_body.serialize())

    period_get_body.id = period_id_2
    period_get_body.start_at = start_at_2
    expected_result.append(period_get_body.serialize())

    assert response.status == 200
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_update_period(web_context, web_app_client):
    start_at_1 = datetime.datetime.fromisoformat('2023-03-23T02:22:22+03:00')
    start_at_2 = datetime.datetime.fromisoformat('2024-04-24T02:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at_1,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200
    period_id = await response.json()
    period_id = period_id['id']

    period_body.control_percentage = 10
    period_body.previous_control_percentage = 25
    period_body.start_at = start_at_2

    response = await web_app_client.put(
        f'/v1/targets/{target_id}/periods/{period_id}',
        json=period_body.serialize(),
    )
    assert response.status == 200

    period_get_body = models.api.PeriodGet(
        control=models.api.Control(
            control_percentage=period_body.control_percentage,
            key=period_body.key,
            salt=utils.EVERY_SALT,
        ),
        created_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        updated_at=datetime.datetime.fromisoformat(
            '2022-02-22T02:22:22+03:00',
        ),
        id=period_id,
        owner=utils.OWNER_OF_ALL,
        start_at=period_body.start_at,
        previous_control_percentage=period_body.previous_control_percentage,
    )

    expected_result = period_get_body.serialize()
    assert expected_result == await response.json()

    response = await web_app_client.get(f'/v1/targets/{target_id}/periods')
    assert response.status == 200

    expected_result = [period_get_body.serialize()]
    assert expected_result == await response.json()


@pytest.mark.now('2022-02-22T02:22:22+03:00')
async def test_delete_period(web_context, web_app_client):
    start_at = datetime.datetime.fromisoformat('2023-03-23T02:22:22+03:00')
    target_id = await utils.create_target_for_periods(web_app_client)
    period_body = models.api.PeriodUpdate(
        control_percentage=5,
        key='phone_pd_id',
        previous_control_percentage=50,
        start_at=start_at,
    )

    response = await web_app_client.post(
        f'/v1/targets/{target_id}/periods',
        json=period_body.serialize(),
        headers={'X-Yandex-Login': utils.OWNER_OF_ALL},
    )
    assert response.status == 200
    period_id = await response.json()
    period_id = period_id['id']

    response = await web_app_client.delete(
        f'/v1/targets/{target_id}/periods/{period_id}',
        json=period_body.serialize(),
    )
    assert response.status == 200

    response = await web_app_client.get(f'/v1/targets/{target_id}/periods')
    assert response.status == 200

    assert [] == await response.json()
