import json


import pytest


HANDLER = '/v1/driver/delivery'
LOGGER_ENDPOINT = '/driver-work-rules/service/v1/change-logger'
PARK_ID2 = 'park2'
DRIVER_ID2 = 'driver2'
# has no thermo info before
PARK_ID4 = 'park4'
DRIVER_ID4 = 'driver4'
AUTHOR = {
    'consumer': 'driver-profile-view',
    'identity': {'type': 'driver', 'driver_profile_id': 'uuid'},
}


async def test_driver_delivery_update_not_found(
        taxi_driver_profiles, mockserver, load_json,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        return

    response = await taxi_driver_profiles.patch(
        HANDLER,
        params={'park_id': 'bla', 'driver_profile_id': 'bla'},
        json={
            'delivery': {'thermopack': True, 'thermobag': True},
            'author': AUTHOR,
        },
    )
    assert response.status_code == 404
    assert _mock_change_logger.times_called == 0


@pytest.mark.parametrize(
    'thermobag,thermopack,profi_courier,old_value,new_value',
    [
        (
            True,
            True,
            True,
            '{"thermobag":false,"thermopack":false,"profi_courier":false}',
            '{"thermobag":true,"thermopack":true,"profi_courier":true}',
        ),
        (
            True,
            None,
            None,
            '{"thermobag":false,"thermopack":false,"profi_courier":false}',
            '{"thermobag":true,"thermopack":false,"profi_courier":false}',
        ),
        (
            None,
            None,
            True,
            '{"thermobag":false,"thermopack":false,"profi_courier":false}',
            '{"thermobag":false,"thermopack":false,"profi_courier":true}',
        ),
    ],
)
async def test_driver_delivery_update(
        taxi_driver_profiles,
        mockserver,
        load_json,
        mongodb,
        thermobag,
        thermopack,
        profi_courier,
        old_value,
        new_value,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': PARK_ID2,
            'change_info': {
                'object_id': DRIVER_ID2,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {'field': 'Delivery', 'old': old_value, 'new': new_value},
                ],
            },
            'author': {
                'dispatch_user_id': 'uuid',
                'display_name': 'driver',
                'user_ip': '',
            },
        }

    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID2, 'park_id': PARK_ID2},
    )
    assert not driver['delivery']['thermopack']
    assert not driver['delivery']['thermobag']
    assert not driver['delivery']['profi_courier']

    delivery = {}
    if thermobag is not None:
        delivery['thermobag'] = thermobag
    if thermopack is not None:
        delivery['thermopack'] = thermopack
    if profi_courier is not None:
        delivery['profi_courier'] = profi_courier

    response = await taxi_driver_profiles.patch(
        HANDLER,
        params={'park_id': PARK_ID2, 'driver_profile_id': DRIVER_ID2},
        json={'delivery': delivery, 'author': AUTHOR},
    )
    assert response.status_code == 200
    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID2, 'park_id': PARK_ID2},
    )
    if thermopack is not None:
        assert driver['delivery']['thermopack'] == thermopack
    if thermobag is not None:
        assert driver['delivery']['thermobag'] == thermobag
    if profi_courier is not None:
        assert driver['delivery']['profi_courier'] == profi_courier
    assert _mock_change_logger.times_called == 1


async def test_driver_delivery_update_to_same_value(
        taxi_driver_profiles, mockserver, load_json, mongodb,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        return

    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID2, 'park_id': PARK_ID2},
    )
    assert not driver['delivery']['thermopack']
    assert not driver['delivery']['thermobag']
    assert not driver['delivery']['profi_courier']
    response = await taxi_driver_profiles.patch(
        HANDLER,
        params={'park_id': PARK_ID2, 'driver_profile_id': DRIVER_ID2},
        json={
            'delivery': {
                'thermopack': False,
                'thermobag': False,
                'profi_courier': False,
            },
            'author': AUTHOR,
        },
    )
    assert response.status_code == 200
    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID2, 'park_id': PARK_ID2},
    )
    assert not driver['delivery']['thermopack']
    assert not driver['delivery']['thermobag']
    assert not driver['delivery']['profi_courier']
    assert _mock_change_logger.times_called == 0


async def test_driver_delivery_update_thermopack_both(
        taxi_driver_profiles, mockserver, load_json, mongodb,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        options = '{"thermobag":true,"thermopack":true,"profi_courier":true}'
        assert body == {
            'park_id': PARK_ID4,
            'change_info': {
                'object_id': DRIVER_ID4,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [{'field': 'Delivery', 'old': '{}', 'new': options}],
            },
            'author': {
                'dispatch_user_id': 'uuid',
                'display_name': 'driver',
                'user_ip': '',
            },
        }

    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID4, 'park_id': PARK_ID4},
    )
    assert 'delivery' not in driver
    response = await taxi_driver_profiles.patch(
        HANDLER,
        params={'park_id': PARK_ID4, 'driver_profile_id': DRIVER_ID4},
        json={
            'delivery': {
                'thermopack': True,
                'thermobag': True,
                'profi_courier': True,
            },
            'author': AUTHOR,
        },
    )
    assert response.status_code == 200
    driver_after = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID4, 'park_id': PARK_ID4},
    )
    assert driver_after['delivery']['thermopack']
    assert driver_after['delivery']['thermobag']
    assert driver_after['delivery']['profi_courier']
    assert driver['updated_ts'] != driver_after['updated_ts']
    assert (
        'modified_date' in driver
        and driver['modified_date'] != driver_after['modified_date']
    ) or driver_after['modified_date']
    assert _mock_change_logger.times_called == 1


async def test_driver_delivery_update_eats_equipment(
        taxi_driver_profiles, mockserver, load_json, mongodb,
):
    @mockserver.json_handler(LOGGER_ENDPOINT)
    def _mock_change_logger(request):
        body = json.loads(request.get_data())
        body.pop('entity_id')
        assert body == {
            'park_id': PARK_ID4,
            'change_info': {
                'object_id': DRIVER_ID4,
                'object_type': 'MongoDB.Docs.Driver.DriverDoc',
                'diff': [
                    {
                        'field': 'Delivery',
                        'old': '{}',
                        'new': '{"eats_equipment":true}',
                    },
                ],
            },
            'author': {
                'dispatch_user_id': 'uuid',
                'display_name': 'driver',
                'user_ip': '',
            },
        }

    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID4, 'park_id': PARK_ID4},
    )
    assert 'delivery' not in driver

    response = await taxi_driver_profiles.patch(
        HANDLER,
        params={'park_id': PARK_ID4, 'driver_profile_id': DRIVER_ID4},
        json={'delivery': {'eats_equipment': True}, 'author': AUTHOR},
    )
    assert response.status_code == 200
    driver = mongodb.dbdrivers.find_one(
        {'driver_id': DRIVER_ID4, 'park_id': PARK_ID4},
    )
    assert 'thermopack' not in driver['delivery']
    assert 'thermobag' not in driver['delivery']
    assert 'profi_courier' not in driver['delivery']
    assert driver['delivery']['eats_equipment']
    assert _mock_change_logger.times_called == 1
