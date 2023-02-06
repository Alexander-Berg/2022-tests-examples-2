# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

import bson
import pytest

from taxi import config
from taxi.conf import settings
from taxi.core import async
from taxi.core import db
from taxi.external import tags_service
from taxi.internal import dbh
from taxi.internal.drivers_ratings import grades
from taxi.internal.drivers_ratings import helpers as ratings_helpers


def _check_upload_calls(append_tags, remove_tags, expected_count):
    has_append_tags = bool(append_tags)
    has_remove_tags = bool(remove_tags)
    # upload should have from 0 to 2 calls
    if expected_count == 0:
        assert not (has_append_tags or has_remove_tags)
    elif expected_count == 1:
        assert has_append_tags ^ has_remove_tags
    else:
        assert expected_count == 2
        assert has_append_tags and has_remove_tags


@pytest.mark.now('2016-09-01T13:00:00.0')
@pytest.mark.config(
    GRADE_STEPS_RULES={'__default__': [4, 4.2, 4.4, 4.6, 4.8, 5, 6, 7, 8]},
    ACCEPTANCE_RATE_FIRST_SKIP_RULES={'__default__': 30},
    ACCEPTANCE_RATE_MIN_RULES={'__default__': 0.5},
    ENABLE_GRADE_FOR_BRANDING={'__default__': False},
    COMPLETED_RATE_WARN_RULES={'__default__': 0.8},
    COMPLETED_RATE_MIN_RULES={'__default__': 0.7},
    COMPLETED_RATE_FIRST_SKIP_RULES={'__default__': 100},
    DRIVER_POINTS_FIRST_VALUE={'__default__': 100},
    DRIVER_POINTS_DISTANCE_THRESHOLDS={'__default__': [1000, 5000]},
    DRIVER_POINTS_ACTION_COSTS={
        '__default__': {
             '__default__': [1, 1, 1],
        }
    },
    DRIVER_POINTS_MIN_RULES={'__default__': 30},
    DRIVER_POINTS_WARN_RULES={'__default__': 60},
    DRIVER_POINTS_DISABLE_STEPS_RULES={
        '__default__': [60 * 60 * 24],
    },
    SELF_ASSIGN_GRADE_RULES={'__default__': 8},
    ENABLE_TAGS_FOR_BRANDING=True,
)
@pytest.mark.parametrize(
    'supercar,rating,stiker,park_boost,gold,park_partner,grade,agrade,updated,'
    'append_tags,remove_tags,expected_upload_calls,expected_bulk_match_calls,'
    'existing_tags,upload_settings_patch,enable_ip_tags_from_grades',
    [
        # test different ratings and grades
        (False, 3.9, True, 0, False, None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.0, True, 0, False, None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.1, True, 0, False, None, 1, 1, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.2, True, 0, False, None, 1, 1, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.3, True, 0, False, None, 2, 2, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.4, True, 0, False, None, 2, 2, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.5, True, 0, False, None, 3, 3, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.6, True, 0, False, None, 3, 3, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.7, True, 0, False, None, 4, 4, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.8, True, 0, False, None, 4, 4, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.9, True, 0, False, None, 5, 5, False,
            {}, {}, 0, 2, [], {}, True),
        (False, 5.0, True, 0, False, None, 5, 5, False,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 0.8, False, None, 6, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 1.8, False, None, 7, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 2.8, False, None, 8, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 3.8, False, None, 9, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 9.8, False, None, 9, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 3, True, 9.8, False, None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, False, 1, False, None, 4, 4, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 1, False, 0, 'car', None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.1, False, 0, 'car', None, 9, 9, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 1, False, 0, 'driver', None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.1, False, 0, 'driver', None, 9, 9, True,
            {}, {}, 0, 2, [], {}, True),
        (True, 1, False, 0, False, None, 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (True, 4.5, False, 0, False, None, 10, 10, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 2, False, None, 7, 5, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 0, False, None, 5, 5, False,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 4, False, None, 9, 5, True,
            {}, {}, 0, 2, [], {}, True),
        # test different park_partners
        (False, 1, False, 0, 'car', 'yandex', 0, 0, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 1, False, 0, 'car', 'selfemployed_fns', 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 4.1, False, 0, 'car', 'yandex', 9, 9, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 4.1, False, 0, 'car', 'selfemployed_fns', 9, 9, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 1, False, 0, 'driver', 'self_assign', 0, 0, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 4.1, False, 0, 'driver', 'self_assign', 9, 9, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 4.1, False, 0, 'driver', 'selfemployed_fns', 9, 9, True,
            {}, {}, 0, 2, [], {}, True),
        (True, 1, False, 0, False, 'yandex', 0, 0, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (True, 1, False, 0, False, 'selfemployed_fns', 0, 0, True,
            {}, {}, 0, 2, [], {}, True),
        (True, 4.5, False, 0, False, 'self_assign', 10, 10, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (True, 4.5, False, 0, False, 'selfemployed_fns', 10, 10, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 2, False, 'yandex', 8, 8, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 5, True, 2, False, 'selfemployed_fns', 8, 8, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 0, False, 'self_assign', 8, 8, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 5, True, 0, False, 'selfemployed_fns', 8, 8, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 5, True, 4, False, 'selfemployed_fns', 9, 8, True,
            {}, {}, 0, 2, [], {}, True),
        (False, 5, True, 0, False, 'other', 5, 5, False,
            {}, {}, 0, 2, [], {}, True),
        # test 'individual_entrepreneur' tag upload by configs
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {'individual_entrepreneur'}, {}, 1, 2, [], {}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {'individual_entrepreneur'}, {}, 1, 2, [],
            {'__default__': False, 'individual_entrepreneur': True}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True, {}, {}, 0, 2,
            ['sticker'], {'individual_entrepreneur': False}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {}, 0, 2, [], {'__default__': False}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {}, 0, 2, ['individual_entrepreneur'], {}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {}, 0, 2, ['individual_entrepreneur'],
            {'__default__': False, 'individual_entrepreneur': True}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {'individual_entrepreneur'}, 1, 2, ['individual_entrepreneur'],
            {'individual_entrepreneur': False}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {'individual_entrepreneur'}, 1, 2, ['individual_entrepreneur'],
            {'__default__': False}, True),
        (False, 5, True, 4, False, 'yandex', 9, 8, True, {}, {}, 0, 1,
            ['individual_entrepreneur'], {'__default__': False}, False),
        (False, 5, True, 4, False, 'yandex', 9, 8, True,
            {}, {}, 0, 1, [], {}, False),
])
@pytest.inline_callbacks
def test_grade_updater(
        supercar, rating, stiker, park_boost, gold, park_partner, grade,
        agrade, updated, append_tags, remove_tags, expected_upload_calls,
        expected_bulk_match_calls, existing_tags, upload_settings_patch,
        enable_ip_tags_from_grades, patch):
    yield db.drivers.remove({})
    yield db.dbdrivers.remove({})
    yield db.unique_drivers.remove({})
    yield db.golden_cars.remove({})
    default_driver_doc = {
        '_id': 'clid_uuid',
        '_state': 'active',
        'driver_license': 'LICENSE',
        'clid': 'clid',
        'uuid': 'uuid',
        'car': {
            'number': 'А123АА77',
        },
        'requirements': {
            'stiker': stiker,
        },
        'db_id': 'dbid',
        'is_supercar': supercar,
        'grades': [
            {
                'class': 'econom',
                'value': 5,
                'airport_value': 5
            },
            {
                'class': 'vip',
                'value': 5,
                'airport_value': 5
            },
        ]
    }
    yield db.drivers.save(default_driver_doc),
    yield db.dbdrivers.save({
        'driver_id': 'uuid',
        'park_id': 'dbid',
        'license_number': 'LICENSE',
        'driver_license_pd_id': 'pd_id_license',
        'work_status': 'working',
        'car_id': 'carid',
        'providers': 'yandex'
    })
    yield db.dbcars.save({
        'park_id': 'dbid',
        'car_id': 'carid',
        'number': 'А123АА77',
        'sticker_confirmed': stiker,
        'service': {
            'sticker': stiker
        }
    })
    yield db.supercars.remove({})
    if supercar:
        yield db.supercars.save({
            '_id': 'А123АА77',
            'conditions': {
                'park_in': ['clid']
            }
        })
    yield db.unique_drivers.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'udriver_id',
        'licenses': [
            {'license': 'LICENSE'},
        ],
        'profiles': [
            {'driver_id': 'clid_uuid'},
        ],
        'new_score': {
            'unified': {
                'total': ratings_helpers.normalize_rating(rating),
            }
        },
        'gl': {
            'econom': 'msk' if gold == 'driver' else None,
        },
    })
    yield db.parks.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'clid',
        'grade_boost': park_boost,
        'city': 'msk',
    })
    yield db.dbparks.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'dbid',
        'provider_config': {
            'yandex': {
                'clid': 'clid'
            }
        },
        'driver_partner_source': park_partner or '',
        'providers': 'yandex',
        'is_active': True
    })
    yield db.cities.save({
        '_id': 'msk',
        'eng': 'moscow',
    })

    @patch('taxi.internal.city_manager.get_allowed_classes')
    def get_allowed_classes(city_doc):
        return ['econom', 'vip']

    upload_settings = {
        '__default__': True, 'sticker': True, 'lightbox': True,
    }
    upload_settings.update(upload_settings_patch)
    yield config.BRANDING_TAGS_UPLOAD_SETTINGS.save(upload_settings)
    yield config.ENABLE_IP_TAGS_FROM_GRADES.save(enable_ip_tags_from_grades)

    is_individual_entrepreneur = (
        park_partner in grades.INDIVIDUAL_ENTREPRENEUR_PARTNER_SOURCES
    )

    @patch('taxi.external.tags_service.upload_request')
    @async.inline_callbacks
    def upload_request(tags_by_entity, provider_id, src_service, entity_type,
                       merge_policy, log_extra=None):
        assert provider_id == grades._TAGS_PROVIDER
        assert entity_type == tags_service.EntityType.PARK
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME

        tags = tags_by_entity.get(default_driver_doc['db_id'], set())
        if merge_policy == tags_service.MergePolicy.APPEND:
            assert append_tags == tags
        elif merge_policy == tags_service.MergePolicy.REMOVE:
            assert remove_tags == tags
        else:
            assert False, 'only append or remove merge policy enabled'
        yield async.return_value(True)

    @patch('taxi.external.tags_service.bulk_match_request')
    @async.inline_callbacks
    def bulk_match_request(entity_type, entities_list, src_service,
                           log_extra=None):
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME
        if entity_type == tags_service.EntityType.PARK:
            entities_count = 0
            if is_individual_entrepreneur:
                entities_count = 1
            assert len(entities_list) == entities_count
            yield async.return_value({'dbid': existing_tags})

        assert entity_type == tags_service.EntityType.DBID_UUID
        dbid_uuid = '{}_{}'.format(
            default_driver_doc['db_id'],
            default_driver_doc['uuid']
        )
        assert entities_list == [dbid_uuid]

        response_tags = []
        if stiker:
            response_tags.append('sticker')
        yield async.return_value({dbid_uuid: response_tags})

    if gold == 'car':
        yield db.golden_cars.save({'_id': 'А123АА77'})
    yield grades.GradeUpdater().run()

    assert len(upload_request.calls) == expected_upload_calls
    _check_upload_calls(append_tags, remove_tags, expected_upload_calls)
    assert len(bulk_match_request.calls) == expected_bulk_match_calls

    driver_doc = yield db.drivers.find_one('clid_uuid')
    assert driver_doc['grades'][0]['class'] == 'econom'
    assert driver_doc['grades'][0]['value'] == grade
    assert driver_doc['grades'][0]['airport_value'] == agrade


@pytest.mark.now('2016-09-01T13:00:00.0')
@pytest.mark.config(
    GRADE_STEPS_RULES={'__default__': [4, 4.2, 4.4, 4.6, 4.8, 5, 6, 7, 8]},
    ACCEPTANCE_RATE_FIRST_SKIP_RULES={'__default__': 30},
    ACCEPTANCE_RATE_MIN_RULES={'__default__': 0.5},
    ENABLE_GRADE_FOR_BRANDING={'__default__': True},
)
@pytest.mark.parametrize(
    'rating,sticker,lightbox,grade,agrade,grade_for_branding,'
    'tags_for_branding_disabled,private_car,append_tags,remove_tags,'
    'existing_tags,expected_upload_calls,expected_bulk_match_calls,'
    'upload_settings_patch', [
        # no any grade and tag for branding
        (4.5, False, False, 3, 3, False, False, False,
         {}, {}, [], 0, 2, {}),
        (4.5, False, False, 3, 3, False, False, True,
         {}, {}, [], 0, 2, {'private_car': False}),
        (4.5, False, False, 3, 3, False, False, False, {},
         {'sticker', 'lightbox', 'grade_for_branding'},
         ['non_branding_tag', 'sticker', 'lightbox', 'grade_for_branding'],
         1, 2, {}),
        (4.5, False, False, 3, 3, False, False, False, {},
         {'sticker', 'lightbox', 'grade_for_branding'},
         ['non_branding_tag', 'sticker', 'lightbox', 'grade_for_branding'],
         1, 2, {'__default__': False}),
        (4.5, False, False, 3, 3, False, False, True, {'private_car'},
         {'sticker', 'lightbox', 'grade_for_branding'},
         ['non_branding_tag', 'sticker', 'lightbox', 'grade_for_branding'],
         2, 2, {'__default__': False, 'private_car': True}),
        # full branding
        (4.5, True, True, 9, 9, True, False, False,
         {'sticker', 'lightbox', 'grade_for_branding'}, {}, [], 1, 2, {}),
        (4.5, True, True, 9, 9, True, False, False, {}, {},
         ['tag', 'sticker', 'lightbox', 'grade_for_branding'], 0, 2, {}),
        (4.5, True, True, 9, 9, True, False, False,
         {'lightbox', 'grade_for_branding'}, {}, ['sticker'], 1, 2, {}),
        (4.5, True, True, 9, 9, True, False, False,
         {}, {'sticker'}, ['sticker', 'lightbox', 'grade_for_branding'], 1, 2,
         {'sticker': False}),
        (4.5, True, True, 9, 9, True, False, False,
         {}, {}, ['lightbox', 'grade_for_branding'], 0, 2, {'sticker': False}),
        (4.5, True, True, 9, 9, True, False, True, {}, {}, [], 0, 2,
         {'__default__': False, 'sticker': False, 'lightbox': False}),
        (4.5, True, True, 9, 9, True, False, True,
         {'grade_for_branding'}, {'private_car', 'sticker', 'lightbox'},
         ['private_car', 'sticker', 'lightbox'], 2, 2, {
             '__default__': False, 'sticker': False, 'lightbox': False,
             'grade_for_branding': True
         }),
        # lightbox and grade branding
        (4.5, False, True, 9, 9, True, False, False,
         {'lightbox', 'grade_for_branding'}, {}, [], 1, 2, {}),
        (4.5, False, True, 9, 9, True, False, False,
         {}, {}, ['lightbox', 'grade_for_branding'], 0, 2, {}),
        (4.5, False, True, 9, 9, True, False, False, {'lightbox'},
         {'sticker', 'private_car'},
         ['sticker', 'grade_for_branding', 'private_car'], 2, 2, {}),
        (4.5, False, True, 9, 9, True, False, True, {},
         {'sticker', 'private_car'},
         ['sticker', 'grade_for_branding', 'private_car'], 1, 2,
         {'lightbox': False, 'sticker': False, 'private_car': False}),
        (4.5, False, True, 9, 9, True, False, True, {},
         {'grade_for_branding', 'private_car'},
         ['grade_for_branding', 'private_car'], 1, 2,
         {'lightbox': False, '__default__': False, 'private_car': False}),
        (4.5, False, True, 9, 9, True, False, True, {}, {}, [], 0, 2,
         {'lightbox': False, '__default__': False, 'private_car': False}),
        # sticker and grade branding
        (4.5, True, False, 9, 9, True, False, False,
         {'sticker', 'grade_for_branding'}, {}, [], 1, 2, {}),
        (4.5, True, False, 9, 9, True, False, False,
         {}, {}, ['sticker', 'grade_for_branding'], 0, 2, {}),
        (4.5, True, False, 9, 9, True, False, False, {'sticker'},
         {'lightbox', 'private_car'},
         ['lightbox', 'grade_for_branding', 'private_car'], 2, 2, {}),
        (4.5, True, False, 9, 9, True, False, True, {},
         {'lightbox', 'private_car'},
         ['lightbox', 'grade_for_branding', 'private_car'], 1, 2,
         {'sticker': False, 'lightbox': False, 'private_car': False}),
        (4.5, True, False, 9, 9, True, False, True, {},
         {'grade_for_branding', 'private_car'},
         ['grade_for_branding', 'private_car'], 1, 2,
         {'sticker': False, '__default__': False, 'private_car': False}),
        (4.5, True, False, 9, 9, True, False, True, {}, {}, [], 0, 2,
         {'sticker': False, '__default__': False, 'private_car': False}),
        # disable tags updating by grade
        (4.5, True, True, 9, 9, True, True, False,
         {}, {}, [], 0, 1, {}),
])
@pytest.inline_callbacks
def test_grade_updater_branding(
        rating, sticker, lightbox, grade, agrade, grade_for_branding,
        tags_for_branding_disabled, private_car, append_tags, remove_tags,
        existing_tags, expected_upload_calls, expected_bulk_match_calls,
        upload_settings_patch, patch):
    upload_settings = {
        '__default__': True, 'sticker': True, 'lightbox': True,
    }
    upload_settings.update(upload_settings_patch)
    yield config.BRANDING_TAGS_UPLOAD_SETTINGS.save(upload_settings)
    yield config.ENABLE_TAGS_FOR_BRANDING.save(not tags_for_branding_disabled)

    @patch('taxi.external.tags_service.upload_request')
    @async.inline_callbacks
    def upload_request(tags_by_entity, provider_id, src_service, entity_type,
                       merge_policy, log_extra=None):
        assert provider_id == grades._TAGS_PROVIDER
        assert entity_type == tags_service.EntityType.DBID_UUID
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME

        tags = tags_by_entity.get('dbid_uuid', set())
        if merge_policy == tags_service.MergePolicy.APPEND:
            assert tags == append_tags
        elif merge_policy == tags_service.MergePolicy.REMOVE:
            assert tags == remove_tags
        else:
            assert False, 'Replace merge policy should not be called'

        yield async.return_value(True)

    @patch('taxi.external.tags_service.bulk_match_request')
    @async.inline_callbacks
    def bulk_match_request(entity_type, entities_list, src_service,
                           log_extra=None):
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME
        if entity_type == tags_service.EntityType.PARK:
            assert entities_list == []
            yield async.return_value({'park': []})

        assert entity_type == tags_service.EntityType.DBID_UUID
        assert entities_list == ['dbid_uuid']
        yield async.return_value({'dbid_uuid': existing_tags})

    yield db.drivers.save({
        '_id': 'clid_uuid',
        '_state': 'active',
        'driver_license': 'LICENSE',
        'clid': 'clid',
        'uuid': 'uuid',
        'car': {
            'number': 'А123АА77',
        },
        'requirements': {
            'stiker': sticker,
            'lightbox': lightbox,
        },
        'db_id': 'dbid',
        'is_supercar': False
    })
    yield db.dbdrivers.save({
        'driver_id': 'uuid',
        'park_id': 'dbid',
        'license_number': 'LICENSE',
        'driver_license_pd_id': 'pd_id_license',
        'work_status': 'working',
        'car_id': 'carid',
        'providers': 'yandex'
    })
    yield db.dbcars.save({
        'park_id': 'dbid',
        'car_id': 'carid',
        'number': 'А123АА77',
        'sticker_confirmed': sticker,
        'lightbox_confirmed': lightbox,
        'service': {
            'sticker': sticker,
            'lightbox': lightbox
        }
    })
    yield db.dbparks.save({
        '_id': 'dbid',
        'provider_config': {
            'yandex': {
                'clid': 'clid'
            }
        },
        'providers': 'yandex',
        'is_active': True
    })
    yield db.unique_drivers.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'udriver_id',
        'licenses': [
            {'license': 'LICENSE'},
        ],
        'profiles': [
            {'driver_id': 'clid_uuid'},
        ],
        'new_score': {
            'unified': {
                'total': ratings_helpers.normalize_rating(rating),
            }
        },
    })
    yield db.parks.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'clid',
        'city': 'msk',
    })
    yield db.cities.save({
        '_id': 'msk',
        'eng': 'moscow',
    })

    if private_car:
        yield db.private_car_numbers.save({
            '_id': 'А123АА77',
            'updated': datetime.datetime.utcnow(),
        })

    yield grades.GradeUpdater().run()
    driver_doc = yield db.drivers.find_one('clid_uuid')
    assert driver_doc['grades'][0]['class'] == 'econom'
    assert driver_doc['grades'][0]['value'] == grade
    assert driver_doc['grades'][0]['airport_value'] == agrade

    bulk_match_calls = len(bulk_match_request.calls)
    assert bulk_match_calls == expected_bulk_match_calls

    upload_calls = len(upload_request.calls)
    assert upload_calls == expected_upload_calls
    _check_upload_calls(append_tags, remove_tags, expected_upload_calls)


@pytest.mark.filldb(_fill=False)
@pytest.mark.config(
    ENABLE_GRADE_FOR_BRANDING={'__default__': False},
    PRIVATE_DRIVER_DISCOUNT_GRADE_RULES={
        '__default__': {},
        'msk': {
            'lightbox': True,
            'sticker': False,
            'full_branding': True
        }
    }
)
@pytest.mark.parametrize('park,driver_requirements,expected_result', [
    (
        {'city': 'msk'},
        {'stiker': True, 'lightbox': True},
        True
    ),
    (
        {'city': 'msk'},
        {'stiker': True},
        False
    ),
    (
        {},
        {'stiker': True, 'lightbox': True},
        False
    ),
    (
        {},
        {'lightbox': True},
        False
    ),
    # Full branding
    (
        {'enable_grade_for_full_branding': True},
        {},
        False
    ),
    (
        {'enable_grade_for_full_branding': True},
        {'lightbox': True},
        False
    ),
    (
        {'enable_grade_for_full_branding': True},
        {'stiker': True},
        False
    ),
    (
        {'enable_grade_for_full_branding': True},
        {'lightbox': True, 'stiker': True},
        True
    ),
    # Lightbox branding
    (
        {'enable_grade_for_lightbox': True},
        {},
        False
    ),
    (
        {'enable_grade_for_lightbox': True},
        {'lightbox': True},
        True
    ),
    (
        {'enable_grade_for_lightbox': True},
        {'stiker': True},
        False
    ),
    (
        {'enable_grade_for_lightbox': True},
        {'lightbox': True, 'stiker': True},
        True
    ),
    # Sticker branding
    (
        {'enable_grade_for_sticker': True},
        {},
        False
    ),
    (
        {'enable_grade_for_sticker': True},
        {'lightbox': True},
        False
    ),
    (
        {'enable_grade_for_sticker': True},
        {'stiker': True},
        True
    ),
    (
        {'enable_grade_for_sticker': True},
        {'lightbox': True, 'stiker': True},
        True
    ),
    # Lightbox || Sticker branding
    (
        {'enable_grade_for_lightbox': True, 'enable_grade_for_sticker': True},
        {},
        False
    ),
    (
        {'enable_grade_for_lightbox': True, 'enable_grade_for_sticker': True},
        {'lightbox': True},
        True
    ),
    (
        {'enable_grade_for_lightbox': True, 'enable_grade_for_sticker': True},
        {'stiker': True},
        True
    ),
    (
        {'enable_grade_for_lightbox': True, 'enable_grade_for_sticker': True},
        {'lightbox': True, 'stiker': True},
        True
    ),
    # Full branding || lightbox
    (
        {
            'enable_grade_for_full_branding': True,
            'enable_grade_for_lightbox': True
        },
        {},
        False
    ),
    (
        {
            'enable_grade_for_full_branding': True,
            'enable_grade_for_lightbox': True
        },
        {'lightbox': True},
        True
    ),
    (
        {
            'enable_grade_for_full_branding': True,
            'enable_grade_for_lightbox': True
        },
        {'stiker': True},
        False
    ),
    (
        {
            'enable_grade_for_full_branding': True,
            'enable_grade_for_lightbox': True
        },
        {'lightbox': True, 'stiker': True},
        True
    ),
])
@pytest.inline_callbacks
def test_grade_get_grade_for_branding(park, driver_requirements, patch,
                                      expected_result):
    @patch('taxi.internal.city_manager.get_allowed_classes')
    def get_allowed_classes(city_doc):
        return ['econom']

    park_doc = {'city': 'default'}
    park_doc.update(park)
    driver = dbh.drivers.Doc({
        'requirements': driver_requirements,
        'car': {'number': '123'}
    })
    yield db.private_car_numbers.save({
        '_id': '123',
        'updated': datetime.datetime.utcnow(),
    })

    updater = grades.GradeUpdater()
    yield updater._prepare()

    result = updater._get_grade_for_branding(park_doc, driver)
    assert result == expected_result


@pytest.mark.filldb(_fill=False)
@pytest.mark.now('2017-12-14T13:00:00.0')
@pytest.mark.config(
    GRADE_STEPS_RULES={'__default__': [4, 4.2, 4.4, 4.6, 4.8, 5, 6, 7, 8]},
    NEWBIE_FOR_GRADES_TIME={
        '__default__': 3600 * 24 * 14,  # 2 weeks
        'kiev': 3600 * 24 * 2,  # 2 days
    },
    NEWBIE_FOR_GRADES_GRADE={'__default__': 5, 'moscow': 10},
)
@pytest.mark.parametrize(
    'first_order_complete,city,rating,expected_newbie_grade', [
    (
        # newbie -- get default grade
        {
            'id': 'test_order_id',
            'completed': datetime.datetime(2017, 12, 10)
        },
        'tver',
        4,
        5
    ),
    (
        # newbie -- get city grade
        {
            'id': 'test_order_id',
            'completed': datetime.datetime(2017, 12, 10)
        },
        'moscow',
        4,
        10
    ),
    (
        # newbie -- get 0 grade by low rating
        {
            'id': 'test_order_id',
            'completed': datetime.datetime(2017, 12, 10)
        },
        'moscow',
        3,
        None
    ),
    (
        # no newbie -- no grade
        {
            'id': 'test_order_id',
            'completed': datetime.datetime(2017, 12, 10)
        },
        'kiev',
        4,
        None
    ),
    (
        # no newbie -- no grade
        {
            'id': 'test_order_id',
            'completed': datetime.datetime(2017, 11, 25)
        },
        None,
        4,
        None
    ),
    (
        # no orders -- no grade
        {},
        None,
        4,
        None
    )
])
@pytest.inline_callbacks
def test_get_newbie_grade(first_order_complete, city, rating,
                          expected_newbie_grade, patch):
    @patch('taxi.internal.city_manager.get_allowed_classes')
    def get_allowed_classes(city_doc):
        return ['econom']

    yield db.unique_drivers.remove({})
    yield db.unique_drivers.save({
        'licenses': [{'license': 'test_license'}],
        'first_order_complete': first_order_complete,
    })
    unique_driver = yield dbh.unique_drivers.Doc.find_one_by_license(
        'test_license'
    )

    updater = grades.GradeUpdater()
    yield updater._prepare()
    result = updater._get_newbie_grade(unique_driver, rating, city)
    assert result == expected_newbie_grade


@pytest.mark.parametrize('driver_requirements,expected_result', [
    ({}, False),
    ({'lightbox': True}, True),
    ({'stiker': True}, True),
])
@pytest.mark.filldb(_fill=False)
def test_is_driver_branded(driver_requirements, expected_result):
    driver = dbh.drivers.Doc({
        'requirements': driver_requirements
    })
    result = grades._is_driver_branded(driver)
    assert result == expected_result


@pytest.mark.filldb(_fill=False)
def test_all_fields_are_unique():
    names = dir(grades)
    field_names = [name for name in names if name[-6:] == '_FIELD']
    fields = [str(getattr(grades, name)) for name in field_names]
    assert len(set(fields)) == len(fields)


@pytest.mark.config(
    ACCEPTANCE_RATE_ALL_FIELDS_RULES={
      "__default__": "udcawrmon",
    },
    ACCEPTANCE_RATE_DISABLE_STEPS_RULES={
      "__default__": [
        {
          "amnesty_attempts": 20,
          "disable_time": 3600
        }
      ]
    },
    ACCEPTANCE_RATE_FIRST_SKIP_RULES={
        "__default__": 0,
    },
    ACCEPTANCE_RATE_FIRST_SUCCESS_TRIPS_RULES={
        "__default__": 10
    },
    ACCEPTANCE_RATE_MIN_RULES={
        "__default__": 0.3,
    },
    ACCEPTANCE_RATE_STAT_LIMIT_RULES={
        "__default__": 100
    },
    ACCEPTANCE_RATE_SUCCESS_FIELDS_RULES={
        "__default__": "udcawm"
    },
    ACCEPTANCE_RATE_WARN_RULES={
        "__default__": 0.6
    },
    ENABLE_TAGS_FOR_BRANDING=True,
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_bug_11009(patch):
    @patch('taxi.util.itertools_ext.chunks')
    def chunks(iterable, chunk_size):
        yield [db.drivers.find_one().result]
        yield [db.drivers.find_one().result]

    @patch('taxi.external.tags_service.upload_request')
    @async.inline_callbacks
    def upload_request(tags_by_entity, provider_id, src_service, entity_type,
                       merge_policy, log_extra=None):
        assert provider_id == grades._TAGS_PROVIDER
        assert merge_policy == tags_service.MergePolicy.REMOVE
        assert entity_type == tags_service.EntityType.DBID_UUID
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME
        yield async.return_value(True)

    @patch('taxi.external.tags_service.bulk_match_request')
    @async.inline_callbacks
    def bulk_match_request(entity_type, entities_list, src_service,
                           log_extra=None):
        assert src_service == settings.IMPORT_TVM_SERVICE_NAME
        if entity_type == tags_service.EntityType.PARK:
            assert entities_list == []
            yield async.return_value({'park': []})

        assert entity_type == tags_service.EntityType.DBID_UUID
        assert entities_list == ['dbid_uuid']
        yield async.return_value({'dbid_uuid': ['dbid_uuid']})

    updater = grades.GradeUpdater()
    updater.DRIVER_CHUNK_SIZE = 1
    yield db.drivers.remove({})
    yield db.dbdrivers.remove({})
    yield db.unique_drivers.remove({})
    yield db.golden_cars.remove({})
    yield db.drivers.save({
        '_id': 'clid_uuid',
        '_state': 'active',
        'driver_license': 'LICENSE',
        'clid': 'clid',
        'uuid': 'uuid',
        'car': {
            'number': 'А123АА77',
        },
        'requirements': {},
        'db_id': 'dbid',
        'completed_rate': 0.02,
        'acceptance_rate': 1,
        'grades': [
            {
                'class': 'econom',
                'value': 5,
                'airport_value': 5
            },
            {
                'class': 'vip',
                'value': 5,
                'airport_value': 5
            },
        ]
    })
    yield db.dbdrivers.save({
        'driver_id': 'uuid',
        'park_id': 'dbid',
        'license_number': 'license',
        'driver_license_pd_id': 'pd_id_license',
        'work_status': 'working',
        'car_id': 'carid',
        'providers': 'yandex'
    })
    yield db.dbcars.save({
        'park_id': 'dbid',
        'car_id': 'carid',
        'number': 'А123АА77'
    })
    yield db.dbparks.save({
        '_id': 'dbid',
        'provider_config': {
            'yandex': {
                'clid': 'clid'
            }
        },
        'providers': 'yandex',
        'is_active': True
    })
    yield db.unique_drivers.save({
        'updated_ts': bson.timestamp.Timestamp(0, 0),
        '_id': 'udriver_id',
        'licenses': [
            {'license': 'LICENSE'},
        ],
        'profiles': [
            {'driver_id': 'clid_uuid'},
        ],
        'order_stats': list('c' * 2 + 'o' * 2 + 'n' * 64),
        'dp': 50,
    })
    yield db.parks.save({
        '_id': 'clid',
        'city': 'msk',
    })
    yield db.cities.save({
        '_id': 'msk',
        'eng': 'moscow',
    })
    updater.run()
    driver = db.drivers.find_one().result
    assert driver['acceptance_rate'] >= 0.6
