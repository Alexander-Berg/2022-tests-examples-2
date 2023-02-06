from __future__ import unicode_literals

import json
import pytest

from django import test as django_test

from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.internal.dbh import queues_settings


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_list_queue_zones():
    url = '/api/queues/zones/'
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_queue_description():
    url = '/api/queues/description/'
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_create_queue_settings(zone_id, value):
    url = '/api/queues/zones/'
    value['zone_id'] = zone_id
    data = {'set_values': value}
    response = yield django_test.Client().post(url, json.dumps(data),
                                               'application/json')
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_delete_queues_zone(zone_id, expected_code=200):
    url = '/api/queues/zones/{}/'.format(zone_id)
    data = {}
    response = yield django_test.Client().delete(url, data, 'application/json')
    assert response.status_code == expected_code


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_set_queue_settings(zone_id, values):
    url = '/api/queues/zones/{}/'.format(zone_id)
    data = {'set_values': values}
    response = yield django_test.Client().put(url, json.dumps(data),
                                              'application/json',
                                              REQUEST_METHOD='PATCH')
    assert response.status_code == 200


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_reset_queue_settings(zone_id, fields, expected_code=200):
    url = '/api/queues/zones/{}/'.format(zone_id)
    data = {'reset_values': fields}
    response = yield django_test.Client().put(url, json.dumps(data),
                                              'application/json',
                                              REQUEST_METHOD='PATCH')
    assert response.status_code == expected_code


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_get_queue_settings(zone_id, expected_code=200):
    url = '/api/queues/zones/{}/'.format(zone_id)
    response = yield django_test.Client().get(url)
    assert response.status_code == expected_code
    if expected_code == 200:
        async.return_value(json.loads(response.content))


def _mock_geofence(areq_request, method, url, **kwargs):
    zone_id = url.split('/')[-2]
    geometry = {
        'type': 'MultiPolygon',
        'coordinates': [[
            [[1, 2], [3, 4], [5, 6], [1, 2]],
            [[1, 2], [3, 4], [5, 6], [1, 2]],
        ]]
    }
    if method == 'GET':
        return areq_request.response(200, body={
            'geometry': geometry,
            'name': zone_id,
            'type': 'airport'
        })
    elif method == 'PUT':
        request_data = kwargs.get('data')
        assert request_data
        assert request_data['geometry'] == geometry
        assert request_data['name'] == zone_id
        assert request_data['type'] == 'parking'
        return areq_request.response(200)
    elif method == 'DELETE':
        return areq_request.response(200)


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_queue_description():
    response = yield _request_queue_description()
    Doc = queues_settings.Doc
    attribs = Doc.get_fields()
    default_doc = yield Doc.get_by_zone('__default__')
    props_without_description = []
    for prop in response:
        name = prop['name']
        assert name
        assert name in attribs
        attribs.remove(name)
        description = prop.get('description')
        if not description:
            props_without_description.append(name)
        assert 'default_value' in prop
        assert prop.get('default_value') == default_doc.get(name)
    # check all attribs has descriptions
    assert 'has no description in yaml doc for' and \
        not props_without_description
    assert 'has no property in yaml doc for' and not attribs


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_post_queues_zone():
    virtual_positions_probs = [
        {
            'min_size': 3,
            'probability': 100,
            'value': 3
        },
        {
            'min_size': 0,
            'max_size': 2,
            'probability': 100,
            'value': 1
        }
    ]
    parking_settings = {
        'platov_waiting': {
            'max_cars': 100,
            'rfid_only': False,
            'weight': 1
        },
        'platov_waiting_2': {
            'max_cars': 100,
            'rfid_only': False,
            'weight': 1
        },
    }
    yield _request_create_queue_settings(
        'platov_airport', {
            'enabled': True,
            'enable_geofence': True,
            'enable_virtual_queue': True,
            'activation_area': 'platov_activation',
            'deactivate_in_surrounding': True,
            'deactivate_seconds_gap': 42,
            'grade_probability': 0.8,
            'hide_current_place': True,
            'hide_remaining_time': True,
            'high_grade': 42,
            'home_zone': 'rostovondon',
            'max_minutes_boundary': 100500,
            'min_minutes_boundary': 31415,
            'show_best_parking_place': True,
            'show_best_parking_waiting_time': True,
            'show_queue_off': True,
            'surrounding_area': 'platov_airport',
            'use_new_messages': True,
            'view_enabled': True,
            'virtual_positions_max': 12,

            'dispatch_areas': ['platov_waiting'],
            'ml_visible_classes': ['econom', 'business'],
            'ml_whitelist_classes': ['econom'],
            'virtual_positions_probs': virtual_positions_probs,
            'parking_settings': parking_settings,
        })
    query = {'zone_id': 'platov_airport'}
    doc = yield db.queues_settings.find_one(query)
    assert doc['enabled']
    assert doc['enable_geofence']
    assert doc['enable_virtual_queue']
    assert doc['activation_area'] == 'platov_activation'
    assert doc['deactivate_in_surrounding']
    assert doc['deactivate_seconds_gap'] == 42
    assert doc['grade_probability'] == 0.8
    assert doc['hide_current_place']
    assert doc['hide_remaining_time']
    assert doc['high_grade'] == 42
    assert doc['home_zone'] == 'rostovondon'
    assert doc['max_minutes_boundary'] == 100500
    assert doc['min_minutes_boundary'] == 31415
    assert doc['show_best_parking_place']
    assert doc['show_best_parking_waiting_time']
    assert doc['show_queue_off']
    assert doc['surrounding_area'] == 'platov_airport'
    assert doc['use_new_messages']
    assert doc['view_enabled']
    assert doc['virtual_positions_max'] == 12
    assert doc['dispatch_areas'] == ['platov_waiting']
    assert doc['ml_visible_classes'] == ['econom', 'business']
    assert doc['ml_whitelist_classes'] == ['econom']

    assert doc['virtual_positions_probs'] == virtual_positions_probs
    assert doc['parking_settings'] == parking_settings


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_airport_queue_settings_zone_full(areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        return _mock_geofence(areq_request, method, url, **kwargs)

    virtual_positions_probs = [
        {
            'min_size': 3,
            'probability': 100,
            'value': 3
        },
        {
            'min_size': 0,
            'max_size': 2,
            'probability': 100,
            'value': 1
        }
    ]
    parking_settings = {
        'platov_waiting': {
            'max_cars': 100,
            'rfid_only': False,
            'weight': 1
        },
        'platov_waiting_2': {
            'max_cars': 100,
            'rfid_only': False,
            'weight': 1
        },
    }
    yield _request_create_queue_settings(
        'platov_airport', {
            'activation_area': 'platov_activation',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon',
        })
    query = {'zone_id': 'platov_airport'}
    doc = yield db.queues_settings.find_one(query)
    assert doc['activation_area'] == 'platov_activation'
    assert doc['surrounding_area'] == 'platov_airport'

    yield _request_set_queue_settings(
        'platov_airport', {
            'enabled': True,
            'enable_geofence': True,
            'enable_virtual_queue': True,
            'activation_area': 'platov_activation',
            'deactivate_in_surrounding': True,
            'deactivate_seconds_gap': 42,
            'grade_probability': 0.8,
            'hide_current_place': True,
            'hide_remaining_time': True,
            'high_grade': 42,
            'home_zone': 'rostovondon',
            'max_minutes_boundary': 100500,
            'min_minutes_boundary': 31415,
            'show_best_parking_place': True,
            'show_best_parking_waiting_time': True,
            'show_queue_off': True,
            'surrounding_area': 'platov_airport',
            'use_new_messages': True,
            'view_enabled': True,
            'virtual_positions_max': 12,

            'dispatch_areas': ['platov_waiting'],
            'ml_visible_classes': ['econom', 'business'],
            'ml_whitelist_classes': ['econom'],
            'virtual_positions_probs': virtual_positions_probs,
            'parking_settings': parking_settings,
        })

    query = {'zone_id': 'platov_airport'}
    doc = yield db.queues_settings.find_one(query)
    assert doc['enabled']
    assert doc['enable_geofence']
    assert doc['enable_virtual_queue']
    assert doc['activation_area'] == 'platov_activation'
    assert doc['deactivate_in_surrounding']
    assert doc['deactivate_seconds_gap'] == 42
    assert doc['grade_probability'] == 0.8
    assert doc['hide_current_place']
    assert doc['hide_remaining_time']
    assert doc['high_grade'] == 42
    assert doc['home_zone'] == 'rostovondon'
    assert doc['max_minutes_boundary'] == 100500
    assert doc['min_minutes_boundary'] == 31415
    assert doc['show_best_parking_place']
    assert doc['show_best_parking_waiting_time']
    assert doc['show_queue_off']
    assert doc['surrounding_area'] == 'platov_airport'
    assert doc['use_new_messages']
    assert doc['view_enabled']
    assert doc['virtual_positions_max'] == 12
    assert doc['dispatch_areas'] == ['platov_waiting']
    assert doc['ml_visible_classes'] == ['econom', 'business']
    assert doc['ml_whitelist_classes'] == ['econom']

    assert doc['virtual_positions_probs'] == virtual_positions_probs
    assert doc['parking_settings'] == parking_settings


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_airport_queue_settings_zone_multi():
    yield _request_create_queue_settings(
        'platov_airport', {
            'activation_area': 'platov_airport',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon',
            'enabled': True
        })
    yield _request_create_queue_settings(
        'svo', {
            'activation_area': 'platov_airport',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon'
        })
    # +1 default
    assert 3 == (yield db.queues_settings.count())


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_queues_zones():
    assert [{'name': '__default__'}] == _request_list_queue_zones()

    yield test_create_airport_queue_settings_zone_multi()

    response = _request_list_queue_zones()
    response_zones = {elem['name'] for elem in response}

    expected = {'__default__', 'platov_airport', 'svo'}
    assert expected == response_zones


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_queues_zone():
    yield test_get_queues_zones()
    yield _request_delete_queues_zone('platov_airport')
    response = _request_list_queue_zones()
    response_zones = {elem['name'] for elem in response}
    expected = {'__default__', 'svo'}
    assert expected == response_zones

    yield _request_delete_queues_zone('svo')
    response = _request_list_queue_zones()
    response_zones = {elem['name'] for elem in response}
    expected = {'__default__'}
    assert expected == response_zones

    yield _request_delete_queues_zone('__default__', 400)
    response = _request_list_queue_zones()
    response_zones = {elem['name'] for elem in response}
    expected = {'__default__'}
    assert expected == response_zones


def _make_value(name, source, value):
    return {'name': name,
            'source': source,
            'value': value,
            'description': name}


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_airport_queue_settings_zone():
    yield db.queues_settings._collection.drop()
    yield db.queues_settings._collection.insert({'zone_id': '__default__'})
    default = {
        'enabled': False,
        'enable_geofence': True,
        'enable_virtual_queue': True,
        'deactivate_in_surrounding': True,
        'deactivate_seconds_gap': 42,
        'grade_probability': 0.8,
    }
    platov = {
        'enabled': True,
        'activation_area': 'platov_activation',
        'surrounding_area': 'platov_airport',
        'home_zone': 'rostovondon',
    }
    yield _request_set_queue_settings('__default__', default)
    yield _request_create_queue_settings('platov_airport', platov)

    doc = yield _request_get_queue_settings('platov_airport')
    assert doc
    expected_values = {
        'enabled': True,
        'activation_area': 'platov_activation',
        'surrounding_area': 'platov_airport',
        'enable_geofence': True,
        'enable_virtual_queue': True,
        'deactivate_in_surrounding': True,
        'deactivate_seconds_gap': 42,
        'grade_probability': 0.8,
        'home_zone': 'rostovondon',
    }
    assert doc == expected_values


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_airport_queue_settings_zone_404():
    yield _request_get_queue_settings('platov_airport', expected_code=404)


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_reset_airport_queue_zone_fields():
    fields_to_set = {
        'enabled': True,
        'enable_geofence': True,
        'enable_virtual_queue': True,
        'activation_area': 'platov_activation',
        'deactivate_in_surrounding': True,
        'deactivate_seconds_gap': 42,
        'grade_probability': 0.8,
        'hide_current_place': True,
        'hide_remaining_time': True,
    }
    yield _request_create_queue_settings('platov_airport', {
        'activation_area': 'platov_activation',
        'surrounding_area': 'platov_airport',
        'home_zone': 'rostovondon',
    })
    yield _request_set_queue_settings('platov_airport', fields_to_set)
    fields_to_reset = ['enable_geofence',
                       'grade_probability',
                       'hide_current_place']
    yield _request_reset_queue_settings('platov_airport', fields_to_reset)

    query = {'zone_id': 'platov_airport'}
    doc = yield db.queues_settings.find_one(query)
    for field in fields_to_reset:
        assert field not in doc

    for field in fields_to_set:
        if field not in fields_to_reset:
            assert field in doc


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_reset_airport_queue_zone_fields_default():
    fields_to_set = {
        'enabled': True,
        'enable_geofence': True,
        'enable_virtual_queue': True,
        'activation_area': 'platov_activation',
        'deactivate_in_surrounding': True,
        'deactivate_seconds_gap': 42,
        'grade_probability': 0.8,
        'hide_current_place': True,
        'hide_remaining_time': True,
    }
    yield _request_set_queue_settings('__default__', fields_to_set)
    fields_to_reset = ['enable_geofence',
                       'grade_probability',
                       'hide_current_place']
    yield _request_reset_queue_settings('__default__', fields_to_reset,
                                        expected_code=200)


# Parking tests
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_parking_names(zone_id):
    url = '/api/queues/zones/{}/parkings/'.format(zone_id)
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_parking(zone_id, parking_id):
    url = '/api/queues/zones/{}/parkings/{}/'.format(zone_id, parking_id)
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_delete_parking(zone_id, parking_id):
    url = '/api/queues/zones/{}/parkings/{}/'.format(zone_id, parking_id)
    response = yield django_test.Client().delete(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_patch_parking(zone_id, parking_id, geometry, expected_code=200):
    url = '/api/queues/zones/{}/parkings/{}/'.format(zone_id, parking_id)
    data = {'set_values': {'geometry': geometry}}
    response = yield django_test.Client().put(url, json.dumps(data),
                                              'application/json',
                                              REQUEST_METHOD='PATCH')
    assert response.status_code == expected_code
    if response.status_code == 200:
        async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_post_parking(zone_id, parking_id, geometry, expected_code=200):
    url = '/api/queues/zones/{}/parkings/'.format(zone_id)
    data = {
        'set_values': {
            'name': parking_id,
            'geometry': geometry
        }
    }
    response = yield django_test.Client().post(url, json.dumps(data),
                                               'application/json')
    assert response.status_code == expected_code
    if response.status_code == 200:
        async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_queues_parkings(areq_request):
    yield test_set_airport_queue_settings_zone_full(areq_request)
    response = yield _request_parking_names('platov_airport')
    parkings = {parking['name'] for parking in response}
    expected = {'platov_waiting', 'platov_waiting_2'}
    assert parkings == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_parking(areq_request, monkeypatch):
    geometry = {
        'type': 'MultiPolygon',
        'coordinates': [[
            [[1, 2], [3, 4], [5, 6], [1, 2]],
            [[1, 2], [3, 4], [5, 6], [1, 2]],
        ]]
    }
    zone_id = 'platov_airport'
    parking_id = 'platov_waiting'

    @areq_request
    def requests_request(method, url, **kwargs):
        return _mock_geofence(areq_request, method, url, **kwargs)

    monkeypatch.setattr(settings, 'TAXI_GEOFENCE_HOST', 'http://test-host')

    yield test_set_airport_queue_settings_zone_full(areq_request)
    response = yield _request_parking(zone_id, parking_id)
    assert response['geometry'] == geometry


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_patch_parking(areq_request, monkeypatch):
    geometry = {
        'type': 'MultiPolygon',
        'coordinates': [[
            [[1, 2], [3, 4], [5, 6], [1, 2]],
            [[1, 2], [3, 4], [5, 6], [1, 2]],
        ]]
    }
    zone_id = 'platov_airport'
    parking_id = 'platov_waiting'

    @areq_request
    def requests_request(method, url, **kwargs):
        return _mock_geofence(areq_request, method, url, **kwargs)

    monkeypatch.setattr(settings, 'TAXI_GEOFENCE_HOST', 'http://test-host')

    yield test_set_airport_queue_settings_zone_full(areq_request)
    yield _request_post_parking(zone_id, parking_id, geometry)
    yield _request_patch_parking(zone_id, parking_id, geometry)


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_parking(areq_request, monkeypatch):
    zone_id = 'platov_airport'
    parking_id = 'platov_waiting'

    @areq_request
    def requests_request(method, url, **kwargs):
        return _mock_geofence(areq_request, method, url, **kwargs)

    monkeypatch.setattr(settings, 'TAXI_GEOFENCE_HOST', 'http://test-host')

    yield test_set_airport_queue_settings_zone_full(areq_request)
    yield _request_delete_parking(zone_id, parking_id)


# Dispatch tests
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_dispatch_zone_names(zone_id):
    url = '/api/queues/zones/{}/dispatch_areas/'.format(zone_id)
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_create_queue_dispatch_area(zone_id, dispatch_area_name, values,
                                        expected_code=200):
    url = '/api/queues/zones/{}/dispatch_areas/'.format(zone_id)
    values['name'] = dispatch_area_name
    data = {'set_values': values}
    response = yield django_test.Client().post(url, json.dumps(data),
                                               'application/json')
    assert response.status_code == expected_code
    if response.status_code == 200:
        async.return_value(json.loads(response.content))
    async.return_value({})


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_patch_queue_dispatch_area(zone_id, dispatch_area_name, values,
                                       reset_values=[]):
    url = '/api/queues/zones/{}/dispatch_areas/{}/'.format(zone_id,
                                                           dispatch_area_name)
    data = {
        'set_values': values,
        'reset_values': reset_values
    }
    response = yield django_test.Client().put(url, json.dumps(data),
                                              'application/json',
                                              REQUEST_METHOD='PATCH')
    assert response.status_code == 200
    async.return_value({})


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_get_queue_dispatch_area(zone_id, dispatch_area_name):
    url = '/api/queues/zones/{}/dispatch_areas/{}/'.format(zone_id,
                                                           dispatch_area_name)
    response = yield django_test.Client().get(url)
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def _request_delete_queue_dispatch_area(zone_id, dispatch_area_name):
    url = '/api/queues/zones/{}/dispatch_areas/{}/'.format(zone_id,
                                                           dispatch_area_name)
    data = {}
    response = yield django_test.Client().delete(url, data, 'application/json')
    assert response.status_code == 200
    async.return_value(json.loads(response.content))


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_get_dispatch_names(areq_request):
    yield test_set_airport_queue_settings_zone_full(areq_request)
    response = yield _request_dispatch_zone_names('platov_airport')
    dispatch_zones = {dispatch_zone['name'] for dispatch_zone in response}
    expected = {'platov_waiting'}
    assert dispatch_zones == expected


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_create_dispatch_area():
    zone_id = 'platov_airport'
    dispatch_area_id = 'platov_waiting'
    ml_model_name = 'platov_airport'
    yield _request_create_queue_settings(
        zone_id, {
            'activation_area': 'platov_activation',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon',
        })
    yield _request_create_queue_dispatch_area(
        zone_id, dispatch_area_id, {
            'ml_model_name': ml_model_name
        })
    doc = yield _request_get_queue_settings(zone_id)
    dispatch_settings = doc.get('dispatch_area_settings')
    assert dispatch_settings
    assert dispatch_area_id in dispatch_settings
    assert dispatch_settings[dispatch_area_id]['ml_model_name'] == \
        ml_model_name

    doc = db.queues_settings._collection.find_one({'zone_id': zone_id})
    assert set(doc['dispatch_areas']) == {dispatch_area_id}
    doc_settings = doc['dispatch_area_settings']
    assert doc_settings[dispatch_area_id]['ml_model_name'] == ml_model_name


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_set_get_dispatch_area():
    zone_id = 'platov_airport'
    dispatch_area_id = 'platov_waiting'
    ml_model_name = 'platov_airport'
    yield _request_create_queue_settings(
        zone_id, {
            'activation_area': 'platov_activation',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon',
        })
    yield _request_create_queue_dispatch_area(
        zone_id, dispatch_area_id, {
            'ml_model_name': ml_model_name
        })

    values = {
        'ml_model_name': 'new_model',
        'ml_whitelist_classes': ['econom'],
        'parking_penalty_min': {'__default__': 42}
    }
    yield _request_patch_queue_dispatch_area(zone_id, dispatch_area_id, values)
    doc = db.queues_settings._collection.find_one({'zone_id': zone_id})
    assert doc['dispatch_area_settings'][dispatch_area_id] == values

    settings = yield _request_get_queue_dispatch_area(zone_id,
                                                      dispatch_area_id)
    assert settings == values


@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_delete_dispatch_area():
    zone_id = 'platov_airport'
    ml_model_name = 'platov_airport'
    yield _request_create_queue_settings(
        zone_id, {
            'activation_area': 'platov_activation',
            'surrounding_area': 'platov_airport',
            'home_zone': 'rostovondon',
        })
    yield _request_create_queue_dispatch_area(
        zone_id, 'dispatch_zone_1', {
            'ml_model_name': ml_model_name
        })
    yield _request_create_queue_dispatch_area(
        zone_id, 'dispatch_zone_2', {
            'ml_model_name': ml_model_name
        })

    @pytest.inline_callbacks
    def check_zones_in_db(zone_id, expected_zones):
        query = {'zone_id': zone_id}
        doc = yield db.queues_settings._collection.find_one(query)
        dispatch_areas = doc['dispatch_areas']
        expected = set(expected_zones)
        assert set(dispatch_areas) == expected
        dispatch_area_settings = doc['dispatch_area_settings']
        assert set(dispatch_area_settings) == expected

    response = yield _request_dispatch_zone_names(zone_id)
    dispatch_zones = {dispatch_zone['name'] for dispatch_zone in response}
    expected = {'dispatch_zone_1', 'dispatch_zone_2'}
    assert dispatch_zones == expected
    check_zones_in_db(zone_id, expected)

    yield _request_delete_queue_dispatch_area(zone_id, 'dispatch_zone_1')
    response = yield _request_dispatch_zone_names('platov_airport')
    dispatch_zones = {dispatch_zone['name'] for dispatch_zone in response}
    expected = {'dispatch_zone_2'}
    assert dispatch_zones == expected
    check_zones_in_db(zone_id, expected)

    yield _request_delete_queue_dispatch_area(zone_id, 'dispatch_zone_2')
    response = yield _request_dispatch_zone_names('platov_airport')
    dispatch_zones = {dispatch_zone['name'] for dispatch_zone in response}
    expected = set()
    assert dispatch_zones == expected
    check_zones_in_db(zone_id, expected)
