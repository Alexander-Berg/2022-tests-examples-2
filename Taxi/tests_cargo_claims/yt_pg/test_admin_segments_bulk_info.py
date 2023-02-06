import os

import pytest

from testsuite.utils import matching


@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_segments_bulk_info_success(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()

    response = await taxi_cargo_claims.post(
        '/v1/admin/segments/bulk-info', json={'segment_ids': segment_ids},
    )
    assert response.status_code == 200
    assert response.json() == {
        'segments': [
            {
                'id': matching.any_string,
                'locations': [
                    {
                        'location_id': matching.uuid_string,
                        'coordinates': [37.5, 55.7],
                        'fullname': 'БЦ Аврора',
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'Садовническая улица',
                        'building': '82',
                        'porch': '4',
                    },
                    {
                        'location_id': matching.uuid_string,
                        'coordinates': [37.6, 55.6],
                        'fullname': 'Свободы, 30',
                        'country': 'Украина',
                        'city': 'Киев',
                        'street': 'Свободы',
                        'building': '30',
                        'porch': '2',
                        'floor': '12',
                        'flat': '87B',
                        'door_code': '0к123',
                        'comment': 'other_comment',
                    },
                    {
                        'location_id': matching.uuid_string,
                        'coordinates': [37.8, 55.4],
                        'fullname': 'Склад',
                        'country': 'Россия',
                        'city': 'Москва',
                        'street': 'МКАД',
                        'building': '50',
                    },
                ],
                'points': [
                    {
                        'claim_point_id': 1,
                        'point_id': matching.any_string,
                        'location_id': matching.uuid_string,
                        'visit_order': 1,
                        'visit_status': 'pending',
                        'revision': 1,
                        'type': 'pickup',
                        'is_fixed_visit_order': False,
                        'is_resolved': False,
                        'is_return_required': False,
                        'resolution': {
                            'is_visited': False,
                            'is_skipped': False,
                        },
                        'last_status_change_ts': matching.datetime_string,
                        'changelog': [
                            {
                                'status': 'pending',
                                'timestamp': matching.datetime_string,
                            },
                        ],
                        'contact': {
                            'name': 'string',
                            'personal_phone_id': '+71111111111_id',
                        },
                        'label': 'source',
                        'phones': [
                            {
                                'type': 'source',
                                'label': 'phone_label.source',
                                'view': 'main',
                            },
                            {
                                'type': 'emergency',
                                'label': 'phone_label.emergency',
                                'view': 'extra',
                            },
                        ],
                        'need_confirmation': True,
                        'leave_under_door': False,
                        'meet_outside': False,
                        'no_door_call': False,
                        'modifier_age_check': False,
                        'segment_point_type': 'source',
                    },
                    {
                        'claim_point_id': 2,
                        'point_id': matching.any_string,
                        'location_id': matching.uuid_string,
                        'visit_order': 2,
                        'visit_status': 'pending',
                        'revision': 1,
                        'type': 'dropoff',
                        'is_fixed_visit_order': False,
                        'is_resolved': False,
                        'is_return_required': False,
                        'resolution': {
                            'is_visited': False,
                            'is_skipped': False,
                        },
                        'last_status_change_ts': matching.datetime_string,
                        'changelog': [
                            {
                                'status': 'pending',
                                'timestamp': matching.datetime_string,
                            },
                        ],
                        'contact': {
                            'name': 'string',
                            'personal_phone_id': '+72222222222_id',
                            'phone_additional_code': '123 45 678',
                        },
                        'label': 'destination',
                        'phones': [
                            {
                                'type': 'destination',
                                'label': 'phone_label.destination',
                                'view': 'extra',
                            },
                            {
                                'type': 'emergency',
                                'label': 'phone_label.emergency',
                                'view': 'extra',
                            },
                        ],
                        'need_confirmation': True,
                        'leave_under_door': False,
                        'meet_outside': False,
                        'no_door_call': False,
                        'modifier_age_check': False,
                        'segment_point_type': 'destination',
                    },
                    {
                        'claim_point_id': 3,
                        'point_id': matching.any_string,
                        'location_id': matching.uuid_string,
                        'visit_order': 3,
                        'visit_status': 'pending',
                        'revision': 1,
                        'type': 'return',
                        'is_fixed_visit_order': False,
                        'is_resolved': False,
                        'is_return_required': False,
                        'resolution': {
                            'is_visited': False,
                            'is_skipped': False,
                        },
                        'last_status_change_ts': matching.datetime_string,
                        'changelog': [
                            {
                                'status': 'pending',
                                'timestamp': matching.datetime_string,
                            },
                        ],
                        'contact': {
                            'name': 'string',
                            'personal_phone_id': '+79999999999_id',
                        },
                        'label': 'return',
                        'phones': [
                            {
                                'type': 'return',
                                'label': 'phone_label.return',
                                'view': 'extra',
                            },
                            {
                                'type': 'emergency',
                                'label': 'phone_label.emergency',
                                'view': 'extra',
                            },
                        ],
                        'need_confirmation': True,
                        'leave_under_door': False,
                        'meet_outside': False,
                        'no_door_call': False,
                        'modifier_age_check': False,
                        'segment_point_type': 'return',
                    },
                ],
                'points_user_version': 1,
                'items': [
                    {
                        'item_id': matching.uuid_string,
                        'pickup_point': matching.any_string,
                        'dropoff_point': matching.any_string,
                        'return_point': matching.any_string,
                        'size': {'length': 20.0, 'width': 5.8, 'height': 0.5},
                        'weight': 10.2,
                        'quantity': 3,
                        'title': 'item title 1',
                    },
                    {
                        'item_id': matching.uuid_string,
                        'pickup_point': matching.any_string,
                        'dropoff_point': matching.any_string,
                        'return_point': matching.any_string,
                        'size': {'length': 2.2, 'width': 5.0, 'height': 1.0},
                        'weight': 5.0,
                        'quantity': 1,
                        'title': 'item title 2',
                    },
                ],
                'status': 'performer_lookup',
                'claim_revision': 1,
                'claim_version': 1,
                'custom_context': {},
                'claim_features': [],
                'diagnostics': {
                    'claim_id': matching.uuid_string,
                    'segment_created_ts': matching.datetime_string,
                    'segment_updated_ts': matching.datetime_string,
                },
                'performer_requirements': {
                    'cargo_type': 'lcv_m',
                    'cargo_loaders': 2,
                    'taxi_classes': ['cargo'],
                    'dispatch_requirements': {
                        'soft_requirements': [
                            {
                                'logistic_group': 'lavka',
                                'performers_restriction_type': 'group_only',
                                'type': 'performer_group',
                            },
                        ],
                    },
                    'special_requirements': {
                        'virtual_tariffs': [
                            {
                                'class': 'express',
                                'special_requirements': [
                                    {'id': 'food_delivery'},
                                ],
                            },
                            {
                                'class': 'cargo',
                                'special_requirements': [{'id': 'cargo_etn'}],
                            },
                        ],
                    },
                },
                'client_info': {
                    'payment_info': {
                        'type': 'corp',
                        'method_id': 'corp-01234567890123456789012345678912',
                    },
                    'user_locale': 'en',
                },
                'claim_origin_info': {
                    'origin': 'api',
                    'displayed_origin': 'API',
                    'user_agent': 'Yandex',
                },
                'allow_batch': False,
                'corp_client_id': '01234567890123456789012345678912',
                'updated_ts': matching.datetime_string,
                'zone_id': 'moscow',
                'emergency_phone_id': '+79098887777_id',
                'skip_act': False,
                'claim_id': matching.uuid_string,
                'claim_comment': 'Очень полезный комментарий',
                'processing_flow': 'disabled',
                'pricing': {'offer_id': 'taxi_offer_id_1'},
                'estimations': [
                    {
                        'offer_id': 'taxi_offer_id_1',
                        'offer_price': '999.0010',
                        'offer_price_mult': '1198.8012',
                        'tariff_class': 'cargo',
                    },
                ],
            },
        ],
    }


@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_segments_bulk_info_same(
        taxi_cargo_claims, create_segment, get_db_segment_ids,
):
    await create_segment()
    segment_ids = await get_db_segment_ids()
    admin_response = await taxi_cargo_claims.post(
        '/v1/admin/segments/bulk-info', json={'segment_ids': segment_ids},
    )
    assert admin_response.status_code == 200

    response = await taxi_cargo_claims.post(
        '/v1/segments/bulk-info',
        json={
            'segment_ids': [
                {'segment_id': segment_id} for segment_id in segment_ids
            ],
        },
    )
    assert response.status_code == 200
    assert admin_response.json() == response.json()


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
@pytest.mark.yt(
    dyn_table_data=['yt_raw_denorm.yaml', 'yt_indexes_claim_segments.yaml'],
)
async def test_segments_bulk_info_pg_yt(
        taxi_cargo_claims, create_segment, get_segment_id,
):
    await create_segment()
    segment_id = await get_segment_id()

    segment_1 = await taxi_cargo_claims.post(
        '/v1/admin/segments/info', params={'segment_id': segment_id},
    )

    segment_2 = await taxi_cargo_claims.post(
        '/v1/admin/segments/info',
        params={'segment_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )

    assert segment_1.status_code == 200
    assert segment_2.status_code == 200

    expected_response = [segment_1.json(), segment_2.json()]

    response = await taxi_cargo_claims.post(
        '/v1/admin/segments/bulk-info',
        json={'segment_ids': [segment_id, '9756ae927d7b42dc9bbdcbb832924343']},
    )

    assert response.status_code == 200
    assert response.json()['segments'] == expected_response
