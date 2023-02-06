import pytest

import datetime

from taxi.core import db
from taxi.internal.dbh import queues_settings


@pytest.inline_callbacks
def test_create_or_update():
    # At first no elements exists.
    assert 0 == (yield db.queues_settings.count())

    # Insert one document.
    new_doc = queues_settings.Doc()
    new_doc.zone_id = 'platov_airport'
    new_doc.updated = datetime.datetime.utcnow()

    # simple data
    new_doc.enabled = True
    new_doc.enable_geofence = True
    new_doc.enable_virtual_queue = True
    new_doc.activation_area = 'platov_activation'
    new_doc.deactivate_in_surrounding = True
    new_doc.deactivate_seconds_gap = 42
    new_doc.grade_probability = 0.8
    new_doc.hide_current_place = True
    new_doc.hide_remaining_time = True
    new_doc.high_grade = 42
    new_doc.home_zone = 'rostovondon'
    new_doc.max_minutes_boundary = 100500
    new_doc.min_minutes_boundary = 31415
    new_doc.show_best_parking_place = True
    new_doc.show_best_parking_waiting_time = True
    new_doc.show_queue_off = True
    new_doc.surrounding_area = 'platov_airport'
    new_doc.use_new_messages = True
    new_doc.view_enabled = True
    new_doc.virtual_positions_max = 12

    # arrays
    new_doc.dispatch_areas = ['platov_waiting']
    new_doc.ml_visible_classes = ['econom', 'business']
    new_doc.ml_whitelist_classes = ['econom']

    # objects
    new_doc.dispatch_area_settings = 'dispatch_area_settings'
    new_doc.virtual_positions_probs = 'virtual_positions_probs'
    new_doc.parking_settings = 'parking_settings'
    yield new_doc.create_or_update()

    doc = yield db.queues_settings.find_one()
    doc.pop('_id')
    assert doc == new_doc


@pytest.inline_callbacks
def test_get_names():
    new_doc = queues_settings.Doc()
    new_doc.zone_id = 'platov_airport'
    new_doc.updated = datetime.datetime.utcnow()
    yield new_doc.create_or_update()

    new_doc = queues_settings.Doc()
    new_doc.zone_id = 'svo'
    new_doc.updated = datetime.datetime.utcnow()
    yield new_doc.create_or_update()

    assert 2 == (yield db.queues_settings.count())

    names = yield queues_settings.Doc.get_names()
    assert set(names) == {'platov_airport', 'svo'}


@pytest.inline_callbacks
def test_reset_fields():
    Doc = queues_settings.Doc
    new_doc = Doc()
    new_doc.zone_id = 'platov_airport'
    new_doc.updated = datetime.datetime.utcnow()
    new_doc.enabled = True
    new_doc.enable_geofence = True
    new_doc.enable_virtual_queue = True
    new_doc.activation_area = 'platov_activation'
    new_doc.deactivate_in_surrounding = True
    new_doc.deactivate_seconds_gap = 42
    yield new_doc.create_or_update()

    fields_to_reset = [Doc.enable_geofence, Doc.deactivate_in_surrounding]

    yield new_doc.reset_fields(fields_to_reset)

    doc = yield db.queues_settings.find_one()
    for field in fields_to_reset:
        assert field not in doc
    for field in new_doc.keys():
        if field not in fields_to_reset:
            assert field in doc


@pytest.inline_callbacks
def test_get_parking_names():
    zone_id = 'platov_airport'

    Doc = queues_settings.Doc
    new_doc = Doc()
    new_doc.zone_id = zone_id
    new_doc.updated = datetime.datetime.utcnow()
    new_doc.activation_area = 'platov_activation'
    new_doc.surrounding_area = 'platov_surrounding'
    new_doc.parking_settings = {
        'platov_parking_1': {
            'max_cars': 100,
            'weight': 1
        },
        'platov_parking_2': {
            'max_cars': 100,
            'weight': 1
        }
    }
    yield new_doc.create_or_update()
    parkings = yield queues_settings.Doc.get_parking_names(zone_id)
    assert set(parkings) == {'platov_parking_1', 'platov_parking_2'}


@pytest.inline_callbacks
def test_get_dispatch_names():
    zone_id = 'platov_airport'

    Doc = queues_settings.Doc
    new_doc = Doc()
    new_doc.zone_id = zone_id
    new_doc.updated = datetime.datetime.utcnow()
    new_doc.activation_area = 'platov_activation'
    new_doc.surrounding_area = 'platov_surrounding'
    new_doc.dispatch_areas = ['terminal_1', 'terminal_2']
    yield new_doc.create_or_update()

    dispatch_zones = \
        yield queues_settings.Doc.get_dispatch_zone_names(zone_id)
    assert set(dispatch_zones) == {'terminal_1', 'terminal_2'}


@pytest.inline_callbacks
def test_get_all():
    Doc = queues_settings.Doc
    new_doc = Doc()
    new_doc.zone_id = 'platov_airport'
    new_doc.updated = datetime.datetime.utcnow()
    new_doc.enabled = True
    yield new_doc.create_or_update()

    new_doc = Doc()
    new_doc.zone_id = 'svo'
    new_doc.updated = datetime.datetime.utcnow()
    new_doc.enabled = False
    yield new_doc.create_or_update()

    doc = yield Doc.get_all()
    assert {'platov_airport', 'svo'} == set(doc.keys())
    assert not doc['svo'][Doc.enabled]
    assert doc['platov_airport'][Doc.enabled]
