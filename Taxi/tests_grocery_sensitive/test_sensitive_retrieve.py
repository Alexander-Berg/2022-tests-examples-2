import pytest

from . import consts
from . import models

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.config(
        TVM_ENABLED=True,
        GROCERY_SENSITIVE_RETRIEVE_PERMISSIONS={
            '__default__': {'tvm_services': [consts.TVM_SERVICE_NAME_SRC]},
        },
    ),
]

DEFAULT_DATA = models.SensitiveData(
    entity_type=consts.ENTITY_TYPE,
    entity_id=consts.ENTITY_ID,
    yandex_uid='yandex_uid',
    personal_phone_id='personal_phone_id',
    user_data=dict(
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
    ),
    extra_data={'extra_field': 123},
)


@pytest.fixture(name='grocery_sensitive_retrieve')
def _grocery_sensitive_retrieve(taxi_grocery_sensitive):
    async def _inner(
            entity_type=consts.ENTITY_TYPE,
            entity_id=consts.ENTITY_ID,
            status_code=200,
    ):
        response = await taxi_grocery_sensitive.post(
            '/sensitive/v1/retrieve',
            json={'entity_type': entity_type, 'entity_id': entity_id},
            headers={'X-Ya-Service-Ticket': consts.TVM_TICKET},
        )

        assert response.status_code == status_code
        return response.json()

    return _inner


@pytest.fixture(name='default_data')
def _default_data(grocery_sensitive_db):
    grocery_sensitive_db.upsert(DEFAULT_DATA)
    return DEFAULT_DATA


# Проверяем happy path
async def test_basic(grocery_sensitive_retrieve, default_data):
    response = await grocery_sensitive_retrieve(
        entity_type=default_data.entity_type, entity_id=default_data.entity_id,
    )

    assert response == {'data': default_data.format()}


# Проверяем 404, если нет данных
async def test_404(grocery_sensitive_retrieve):
    await grocery_sensitive_retrieve(status_code=404)


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
        grocery_sensitive_retrieve,
        taxi_config,
        default_data,
        perms,
        expected_status_code,
):
    taxi_config.set(
        GROCERY_SENSITIVE_HANDLE_PERMISSIONS={
            '__default__': {'tvm_check_enabled': False},
            '/sensitive/v1/retrieve': perms,
        },
    )

    await grocery_sensitive_retrieve(status_code=expected_status_code)


@pytest.mark.parametrize(
    'perms, expected_status_code',
    [
        ({'tvm_services': ['unknown']}, 403),
        ({'tvm_services': [consts.TVM_SERVICE_NAME_SRC]}, 200),
    ],
)
async def test_retrieve_permissions(
        grocery_sensitive_retrieve,
        taxi_config,
        default_data,
        perms,
        expected_status_code,
):
    taxi_config.set(
        GROCERY_SENSITIVE_RETRIEVE_PERMISSIONS={
            '__default__': {},
            consts.ENTITY_TYPE: perms,
        },
    )

    await grocery_sensitive_retrieve(status_code=expected_status_code)
