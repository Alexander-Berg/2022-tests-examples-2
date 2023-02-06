import pytest
import freezegun

from taxi.robowarehouse.lib.concepts import registrars
from taxi.robowarehouse.lib.concepts import warehouses
from taxi.robowarehouse.lib.test_utils.helpers import assert_items_equal
from taxi.robowarehouse.lib.misc.helpers import generate_id
from taxi.robowarehouse.lib.misc import datetime_utils


@pytest.mark.asyncio
async def test_get_all():
    registrar1 = await registrars.factories.create()
    registrar2 = await registrars.factories.create()

    result = await registrars.get_all()

    result = [el.to_dict() for el in result]
    expected = [el.to_dict() for el in (registrar1, registrar2)]

    result.sort(key=lambda el: el['registrar_id'])
    expected.sort(key=lambda el: el['registrar_id'])

    assert len(result) == 2
    assert_items_equal(result, expected)


@pytest.mark.asyncio
async def test_get_by_registrar_id():
    await registrars.factories.create()
    registrar = await registrars.factories.create()

    result = await registrars.get_by_registrar_id(registrar_id=registrar.registrar_id)

    assert result.to_dict() == registrar.to_dict()


@pytest.mark.asyncio
async def test_get_by_registrar_id_not_found_error():
    registrar_id = generate_id()

    with pytest.raises(registrars.exceptions.RegistrarNotFoundError):
        await registrars.get_by_registrar_id(registrar_id=registrar_id)


@pytest.mark.asyncio
async def test_create():
    registrar1 = await registrars.factories.create()
    registrar2 = registrars.factories.build()

    result = await registrars.create(registrars.CreateRegistrarRequest.from_orm(registrar2))

    regitrar_list = await registrars.get_all()
    regitrar_list = [el.to_dict() for el in regitrar_list]
    expected = [el.to_dict() for el in (registrar1, registrar2)]

    assert result.to_dict() == registrar2.to_dict()
    assert_items_equal(regitrar_list, expected)


@pytest.mark.asyncio
async def test_add_warehouses():
    await registrars.factories.create()
    registrar = await registrars.factories.create()
    warehouse1 = await warehouses.factories.create()
    warehouse2 = await warehouses.factories.create()

    await registrars.add_warehouses(registrar, [warehouse1, warehouse2])

    registrars_warehouses = await registrars.get_all_registrars_warehouses()
    result = [el.to_dict() for el in registrars_warehouses]
    expected = [
        {'registrar_id': registrar.registrar_id, 'warehouse_id': el.warehouse_id}
        for el in (warehouse1, warehouse2)
    ]
    result.sort(key=lambda el: el['warehouse_id'])
    expected.sort(key=lambda el: el['warehouse_id'])

    assert_items_equal(result, expected)


@pytest.mark.parametrize('registrar_id, phone, update_body', [
    (None, '+7123456789', {'first_name': 'test'}),
    (generate_id(), None, {'email': 'test@test', 'last_name': 'testov'}),
    (generate_id(), '+7123456789', {'external_system': 'TELEGRAM', 'external_registrar_id': '12345'}),
])
@freezegun.freeze_time('2020-01-02 03:04:05', tz_offset=-3)
@pytest.mark.asyncio
async def test_update(registrar_id, phone, update_body):
    now = datetime_utils.get_now()

    registrar1 = await registrars.factories.create(registrar_id=registrar_id, phone=phone)
    registrar2 = await registrars.factories.create()

    update_request = registrars.UpdateRegistrarRequest(**update_body)
    result = await registrars.update(registrar_id=registrar_id, phone=phone, update_request=update_request)

    new_registrar1 = await registrars.get_by_registrar_id(registrar1.registrar_id)
    new_registrar2 = await registrars.get_by_registrar_id(registrar2.registrar_id)

    assert new_registrar2.to_dict() == registrar2.to_dict()
    assert new_registrar1.to_dict() == {**registrar1.to_dict(), 'updated_at': now, **update_body}
    assert result.to_dict() == new_registrar1.to_dict()


@pytest.mark.parametrize('registrar_id, update_body, exception', [
    (None, {'first_name': 'test'}, ValueError),
    (generate_id(), {'first_name': None}, registrars.exceptions.RegistrarNothingUpdate),
    (generate_id(), {'first_name': 'test'}, registrars.exceptions.RegistrarNotFoundError),
])
@pytest.mark.asyncio
async def test_update_errors(registrar_id, update_body, exception):
    update_body = registrars.UpdateRegistrarRequest(**update_body)
    with pytest.raises(exception):
        await registrars.update(registrar_id=registrar_id, update_request=update_body)
