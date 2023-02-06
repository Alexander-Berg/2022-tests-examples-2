import copy
import dataclasses
import typing

import pytest

from . import consts
from . import models


@dataclasses.dataclass
class StoreObject:
    entity_id: str
    entity_type: str
    data: dict


DEFAULT_DATA = dict(
    yandex_uid='yandex_uid',
    personal_phone_id='personal_phone_id',
    personal_email_id='personal_email_id',
    user_ip='user_ip',
    appmetrica_device_id='appmetrica_device_id',
    eater_id='eater_id',
    taxi_user_id='taxi_user_id',
    taxi_session='taxi_session',
    phone_id='phone_id',
    login_id='login_id',
    bound_uids=['uid1', 'uid2'],
    bound_taxi_sessions=['session1', 'session2'],
    extra_data={'extra_field': 123},
)


@pytest.fixture(name='grocery_sensitive_store')
def _grocery_sensitive_store(taxi_grocery_sensitive):
    async def _inner(
            objects: typing.List[StoreObject],
            request_id='request_id',
            status_code=200,
    ):
        response = await taxi_grocery_sensitive.post(
            '/sensitive/v1/store',
            json={
                'objects': list(map(dataclasses.asdict, objects)),
                'request_id': request_id,
            },
            headers={'X-Ya-Service-Ticket': consts.TVM_TICKET},
        )

        assert response.status_code == status_code

    return _inner


# Проверяем создание записи в базе.
async def test_pg_insert(grocery_sensitive_store, grocery_sensitive_db):
    request_id = 'request_id'
    store_objects = (
        StoreObject(
            entity_type=consts.ENTITY_TYPE,
            entity_id='id1',
            data=copy.deepcopy(DEFAULT_DATA),
        ),
        StoreObject(
            entity_type=consts.ENTITY_TYPE,
            entity_id='id2',
            data=copy.deepcopy(DEFAULT_DATA),
        ),
    )

    for index, obj in enumerate(store_objects):
        obj.data['yandex_uid'] += f'_{index}'

    await grocery_sensitive_store(objects=store_objects, request_id=request_id)

    for obj in store_objects:
        data_list = grocery_sensitive_db.load_data(
            entity_type=obj.entity_type, entity_id=obj.entity_id,
        )

        assert len(data_list) == 1
        assert data_list[0].format() == obj.data


# Проверяем обновдение записи в базе.
async def test_pg_update(grocery_sensitive_store, grocery_sensitive_db):
    request_id = 'request_id'
    obj = StoreObject(
        entity_type=consts.ENTITY_TYPE, entity_id='id1', data=DEFAULT_DATA,
    )

    grocery_sensitive_db.upsert(
        models.SensitiveData(
            entity_id=obj.entity_id,
            entity_type=obj.entity_type,
            request_id=request_id,
            yandex_uid='123',
        ),
    )

    await grocery_sensitive_store(objects=[obj], request_id=request_id)

    data_list = grocery_sensitive_db.load_data(
        entity_type=obj.entity_type, entity_id=obj.entity_id,
    )
    assert len(data_list) == 1
    assert data_list[0].format() == obj.data


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    'perms, expected_status_code',
    [
        ({'tvm_check_enabled': False}, 200),
        ({'tvm_check_enabled': True}, 403),
        ({'tvm_check_enabled': True, 'tvm_services': ['unknown']}, 403),
        (
            {
                'tvm_check_enabled': True,
                'tvm_services': [consts.TVM_SERVICE_NAME_SRC],
            },
            200,
        ),
    ],
)
async def test_handle_permissions(
        grocery_sensitive_store, taxi_config, perms, expected_status_code,
):
    taxi_config.set(
        GROCERY_SENSITIVE_HANDLE_PERMISSIONS={
            '__default__': {'tvm_check_enabled': False},
            '/sensitive/v1/store': perms,
        },
    )

    await grocery_sensitive_store([], status_code=expected_status_code)
