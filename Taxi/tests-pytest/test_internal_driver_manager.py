# -*- coding: utf-8 -*-

import datetime

import pytest

from taxi.core import async
from taxi.core import db
from taxi.external import oldtracker
from taxi.internal import driver_manager
from taxi.internal import geo_position


_NEW_BILLING_MIGRATION = {
    "commissions": {
        "enabled": {
            "moscow": [
                {
                    "first_date": "2019-02-01",
                    "last_date": "2019-02-01"
                }
            ]
        }
    },
}


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_status(patch):
    status = 'active'

    @patch('taxi.external.drivers_lookup.get_status')
    @async.inline_callbacks
    def get_status(driver_id, log_extra=None):
        yield
        async.return_value(status)

    assert (yield driver_manager.get_status('driver')) == status


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('use_backdoor', [True, False])
@pytest.inline_callbacks
def test_get_last_position(patch, use_backdoor):
    @patch('taxi.internal.driver_manager._get_backdoor_position')
    def _get_backdoor_position(driver_id, log_extra=None):
        return 'position'

    @patch('taxi.internal.driver_manager._get_position')
    def _get_position(driver_id, tvm_src_service=None, log_extra=None):
        return 'position'

    response = yield driver_manager.get_last_position(
        'driver_id', 'park_id', backdoor=use_backdoor
    )
    assert response == 'position'
    if use_backdoor:
        calls = [{'driver_id': 'driver_id', 'log_extra': None}]
        assert _get_position.calls == []
        assert _get_backdoor_position.calls == calls
    else:
        calls = [{'driver_id': 'park_id_id', 'log_extra': None,
                  'tvm_src_service': None}]
        assert _get_position.calls == calls
        assert _get_backdoor_position.calls == []


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_last_position_missing(patch):
    @patch('taxi.internal.driver_manager._get_position')
    def _get_position(driver_id, tvm_src_service=None, log_extra=None):
        return ()

    with pytest.raises(geo_position.PositionUnknownError):
        yield driver_manager.get_last_position('driver_id', 'park_id')


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_last_backdoor_position_internal(patch):
    lon = 37.5
    lat = 55.7
    direction = 180.0
    speed = 10.0
    now = datetime.datetime.utcnow()

    @patch('taxi.internal._driver_helpers.extract_clid_uuid')
    def _extract_clid_uuid(driver_id):
        return ('clid', 'uuid')

    @patch('taxi.external.oldtracker.fetch_single')
    @async.inline_callbacks
    def fetch_single(clid, uuid, backdoor=False, log_extra=None):
        yield
        response = (lon, lat, direction, speed, now)
        async.return_value(response)

    position = yield driver_manager._get_backdoor_position('driver_id')
    assert position == geo_position.DriverTrackPoint(
        lon, lat, geotime=now, direction=direction, speed=speed)
    assert _extract_clid_uuid.calls == [{'driver_id': 'driver_id'}]
    assert fetch_single.calls == [{
        'args': ('clid', 'uuid'),
        'kwargs': {'backdoor': True, 'log_extra': None},
    }]


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_get_last_backdoor_position_internal_missing(patch):

    @patch('taxi.external.oldtracker.fetch_single')
    @async.inline_callbacks
    def fetch_single(clid, uuid, backdoor=False, log_extra=None):
        yield
        raise oldtracker.MissingTrackError('no track')

    response = yield driver_manager._get_backdoor_position('driver_id')
    assert response == ()


@pytest.mark.filldb(_fill=False)
def test_validate_uuid():
    assert driver_manager.validate_uuid(u'Abc012')
    assert driver_manager.validate_uuid(u'012')
    assert driver_manager.validate_uuid(u'Abc')
    assert not driver_manager.validate_uuid(u'у7383113605')
    assert not driver_manager.validate_uuid(u'')

    assert driver_manager.validate_uuid('Abc012')
    assert driver_manager.validate_uuid('012')
    assert driver_manager.validate_uuid('Abc')
    assert not driver_manager.validate_uuid('')
    assert not driver_manager.validate_uuid('Москва')


@pytest.mark.filldb(
    dbcars='childchairs',
)
@pytest.mark.parametrize('car_id,driver_profile_id,expected_response', [
    ('car_id0', 'uuid', False),
    ('car_id1', 'uuid', False),
    ('car_id1', 'uuid1', True),
    ('car_id1', 'uuid2', True),
    ('car_id1', None, False),
    ('car_id2', 'uuid', True),
    ('car_id3', 'uuid', True),
])
@pytest.inline_callbacks
def test_has_child_tariff(car_id, driver_profile_id, expected_response):
    car_doc = yield db.dbcars.find_one({
        'car_id': car_id, 'park_id': 'park_id',
    })
    response = driver_manager._is_child_tariff_enabled(
        car_doc, driver_profile_id,
    )
    assert response is expected_response


@pytest.mark.filldb(
    dbcars='childchairs',
)
@pytest.mark.parametrize(
    'car_id,driver_profile_id,expected_boosters,expected_chairs', [
        ('car_id0', 'uuid', 0, []),
        ('car_id1', 'uuid', 0, []),
        ('car_id1', 'uuid1', 2, []),
        (
            'car_id1',
            'uuid2',
            0,
            [
                {
                    'group0': False,
                    'group1': True,
                    'group2': True,
                    'group3': False,
                },
            ],
        ),
        ('car_id1', None, 0, []),
        ('car_id2', 'uuid', 1, []),
        (
            'car_id3',
            'uuid',
            0,
            [
                {
                    'group0': False,
                    'group1': False,
                    'group2': True,
                    'group3': True,
                },
            ],
        ),
    ]
)
@pytest.inline_callbacks
def test_compile_car_requirements(
        car_id, driver_profile_id, expected_boosters, expected_chairs,
):
    car_doc = yield db.dbcars.find_one({
        'car_id': car_id, 'park_id': 'park_id',
    })
    response = driver_manager._compile_car_requirements(
        car_doc, driver_profile_id,
    )
    assert response['childbooster_amount'] == expected_boosters
    assert response['childseats'] == expected_chairs
