import datetime

import pytest

from . import consts
from . import models


@pytest.fixture(name='grocery_takeout_status')
def _grocery_takeout_status(taxi_grocery_takeout):
    async def _inner(
            yandex_uids=None,
            date_request_at: datetime.datetime = None,
            status_code=200,
    ):
        if yandex_uids is None:
            yandex_uids = [consts.YANDEX_UID]
        if date_request_at is None:
            date_request_at = datetime.datetime.now().astimezone()
        yandex_uids_request = [
            dict(uid=uid, is_portal=True) for uid in yandex_uids
        ]

        response = await taxi_grocery_takeout.post(
            '/takeout/v2/status',
            json={
                'request_id': consts.JOB_ID,
                'date_request_at': date_request_at.isoformat(),
                'yandex_uids': yandex_uids_request,
            },
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


# Проверяем запрос status для entity.
@pytest.mark.parametrize('entity_status', ['empty', 'ready_to_delete'])
async def test_entity_status(
        grocery_takeout_status,
        grocery_takeout_configs,
        mock_entities,
        entity_status,
):
    yandex_uids = [consts.YANDEX_UID]
    date_request_at = consts.NOW_DT

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type='yandex_uid',
            children=[models.EntityNode(entity_type='orders')],
        ),
    )

    mock_entities.orders.mock_status(entity_status)

    mock_entities.orders.status.check(
        yandex_uids=yandex_uids,
        till_dt=date_request_at.isoformat(),
        headers={'Content-Type': 'application/json'},
    )

    grocery_takeout_configs.entity_graph(entity_graph)

    response = await grocery_takeout_status(
        yandex_uids=yandex_uids, date_request_at=date_request_at,
    )
    assert response == dict(data_state=entity_status)

    assert mock_entities.orders.status.times_called == 1


# Проверяем, что если хоть одна entity ответит ready_to_delete,
# то ручка ответит ready_to_delete.
@pytest.mark.parametrize(
    'entity_to_status',
    [
        dict(orders='empty', carts='empty'),
        dict(orders='ready_to_delete', carts='empty'),
        dict(orders='empty', carts='ready_to_delete'),
        dict(orders='ready_to_delete', carts='ready_to_delete'),
    ],
)
async def test_multiple_entities(
        grocery_takeout_status,
        grocery_takeout_configs,
        mock_entities,
        entity_to_status,
):
    entities = entity_to_status.keys()

    entity_graph = models.EntityGraph(
        models.EntityNode(
            entity_type='yandex_uid',
            children=[
                models.EntityNode(entity_type=entity_type)
                for entity_type in entities
            ],
        ),
    )

    for entity_type, status in entity_to_status.items():
        mock_entities[entity_type].mock_status(status)

    grocery_takeout_configs.entity_graph(entity_graph)

    response = await grocery_takeout_status()

    expected_state = 'empty'
    if 'ready_to_delete' in entity_to_status.values():
        expected_state = 'ready_to_delete'

    assert response == dict(data_state=expected_state)


# Проверяем, что если есть таска на удаление,
# то ручка ответит delete_in_progress.
@pytest.mark.parametrize('delete_status', models.DeleteStatus.values)
async def test_job_in_progress(
        grocery_takeout_status,
        grocery_takeout_configs,
        grocery_takeout_db,
        delete_status,
):
    yandex_uid = consts.YANDEX_UID

    grocery_takeout_db.upsert(
        models.DeleteRequest(
            job_id='0', status='done', yandex_uids=[yandex_uid],
        ),
        models.DeleteRequest(
            job_id='1', status='done', yandex_uids=['uid1', 'uid2'],
        ),
        models.DeleteRequest(
            job_id='2', status=delete_status, yandex_uids=['uid3', yandex_uid],
        ),
    )

    entity_graph = models.EntityGraph(
        models.EntityNode(entity_type='yandex_uid'),
    )

    grocery_takeout_configs.entity_graph(entity_graph)

    response = await grocery_takeout_status(yandex_uids=[yandex_uid])

    expected_state = 'empty'
    if delete_status != models.DeleteStatus.done:
        expected_state = 'delete_in_progress'

    assert response == dict(data_state=expected_state)
