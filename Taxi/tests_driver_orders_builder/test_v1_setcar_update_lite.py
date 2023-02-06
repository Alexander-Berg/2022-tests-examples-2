import json

import pytest

from testsuite.utils import matching

HANDLER = '/v1/setcar/update-lite'
DRIVER = 'driver1'
ORDER = '4d605a2849d747079b5d8c7012830419'
PARK = 'park1'

_ORDER_SETCAR_ITEMS = 'Order:SetCar:Items'
_ORDER_SETCAR_MD5 = 'Order:SetCar:MD5'
_ORDER_SETCAR_DRIVER_RESERV_MD5 = 'Order:SetCar:Driver:Reserv:MD5'

SIMPLE_SETCAR = {'id': ORDER}
COMMON_SETCAR = {'id': ORDER, 'cargo': {}}


@pytest.fixture(name='set_setcar')
def _set_setcar(redis_store):
    def _wrapper(setcar: dict, park_id=PARK, order_id=ORDER):
        redis_store.hset(
            _ORDER_SETCAR_ITEMS + ':' + park_id, order_id, json.dumps(setcar),
        )

    return _wrapper


@pytest.fixture(name='update_lite_request')
async def _update_lite_request(taxi_driver_orders_builder):
    async def _wrapper(
            changes: list, park_id=PARK, driver_id=DRIVER, order_id=ORDER,
    ):
        response = await taxi_driver_orders_builder.post(
            HANDLER,
            params={
                'driver_profile_id': driver_id,
                'park_id': park_id,
                'order_id': order_id,
            },
            json={'changes': changes},
        )
        return response

    return _wrapper


@pytest.mark.parametrize(
    'handler_request, setcar_item, expected_response',
    [
        (
            {'changes': [{'field': 'cargo', 'value': {}}]},
            SIMPLE_SETCAR,
            COMMON_SETCAR,
        ),
        (
            {
                'changes': [
                    {
                        'field': 'cargo',
                        'value': {'replaced': True},
                        'allow_replace': True,
                    },
                ],
            },
            COMMON_SETCAR,
            {'id': ORDER, 'cargo': {'replaced': True}},
        ),
        (
            {
                'changes': [
                    {
                        'field': 'cargo',
                        'value': {'replaced': True},
                        'allow_replace': False,
                    },
                ],
            },
            COMMON_SETCAR,
            COMMON_SETCAR,
        ),
    ],
)
@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'cargo': True,
    },
)
async def test_simple_key_path(
        taxi_driver_orders_builder,
        setcar_item,
        redis_store,
        handler_request,
        expected_response,
):
    redis_store.hset(
        _ORDER_SETCAR_ITEMS + ':' + PARK, ORDER, json.dumps(setcar_item),
    )
    redis_store.set(_ORDER_SETCAR_MD5 + ':' + PARK, 'some_md5')
    redis_store.set(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + PARK + ':' + DRIVER,
        'some_driver_md5',
    )
    old_md5 = redis_store.get(_ORDER_SETCAR_MD5 + ':' + PARK)
    old_driver_md5 = redis_store.get(
        _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + PARK + ':' + DRIVER,
    )

    response = await taxi_driver_orders_builder.post(
        HANDLER,
        params={
            'driver_profile_id': DRIVER,
            'park_id': PARK,
            'order_id': ORDER,
        },
        json=handler_request,
    )
    assert response.status_code == 200, response.text
    response = response.json()
    assert response == expected_response

    assert redis_store.get(_ORDER_SETCAR_MD5 + ':' + PARK) != old_md5
    assert (
        redis_store.get(
            _ORDER_SETCAR_DRIVER_RESERV_MD5 + ':' + PARK + ':' + DRIVER,
        )
        != old_driver_md5
    )


@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'cargo.version': True,
    },
)
async def test_set_nested_field(update_lite_request, set_setcar):
    set_setcar({'id': ORDER, 'cargo': {'is_batch_order': False}})

    response = await update_lite_request(
        changes=[{'field': 'cargo.version', 'value': 'version0_1'}],
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo': {'is_batch_order': False, 'version': 'version0_1'},
        'id': matching.any_string,
    }


@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'cargo.version': True,
    },
)
async def test_update_nested_field(set_setcar, update_lite_request):
    set_setcar(
        {
            'id': ORDER,
            'cargo': {'is_batch_order': False, 'version': 'version0_0'},
        },
    )

    response = await update_lite_request(
        changes=[
            {
                'field': 'cargo.version',
                'value': 'version0_1',
                'allow_replace': True,
            },
        ],
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo': {'is_batch_order': False, 'version': 'version0_1'},
        'id': matching.any_string,
    }


@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'cargo.version': True,
    },
)
async def test_set_parent_and_nested_fields(update_lite_request, set_setcar):
    set_setcar({'id': ORDER})
    response = await update_lite_request(
        changes=[
            {
                'field': 'cargo.version',
                'value': 'version0_1',
                'allow_replace': True,
            },
        ],
    )
    assert response.status_code == 200
    assert response.json() == {
        'cargo': {'version': 'version0_1'},
        'id': matching.any_string,
    }


@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'cargo.version': True,
    },
)
async def test_setcar_not_found(update_lite_request):
    response = await update_lite_request(
        changes=[
            {
                'field': 'cargo.version',
                'value': 'version0_1',
                'allow_replace': True,
            },
        ],
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'Not found',
        'message': 'Setcar was not found',
    }


@pytest.mark.config(
    SETCAR_UPDATEREQUEST_LITE_ALLOWED_FIELDS={
        '__default__': False,
        'path.to.key.long': True,
    },
)
async def test_too_complex_key(update_lite_request, set_setcar):
    set_setcar({'id': ORDER})
    response = await update_lite_request(
        changes=[
            {'field': 'path.to.key.long', 'value': {}, 'allow_replace': True},
        ],
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'Bad Request',
        'message': (
            'Now we can set value by so complex key. See TAXICOMMON-3093'
        ),
    }


async def test_not_allowed_key(update_lite_request, set_setcar):
    set_setcar({'id': ORDER})
    response = await update_lite_request(
        changes=[{'field': 'not-allowed', 'value': {}, 'allow_replace': True}],
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': 'Conflict',
        'message': 'Updating field \'not-allowed\' disabled by config',
    }
