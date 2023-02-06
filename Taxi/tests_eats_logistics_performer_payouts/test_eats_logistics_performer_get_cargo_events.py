import psycopg2
import pytest

# pylint: disable=too-many-lines

# DB helpers:

PG_DBNAME = 'eats_logistics_performer_payouts'
PG_FILES = [
    'eats_logistics_performer_payouts/insert_all_factors.sql',
    'eats_logistics_performer_payouts/insert_shift_subjects.sql',
]


# Pulse helpers:


# pulse_value is a string with format 'yyyy-mm-dd HH:MM:SS+03'
def upsert_pulse(pg_cursor, pulse_name, pulse_value):
    # $1 - pulse name (aka id)
    # $2 - pulse value
    query_template = """
INSERT
INTO eats_logistics_performer_payouts.pulses ( id, timestamp_at, updated_at )
VALUES ( '{}', '{}'::TIMESTAMPTZ, NOW() )
ON CONFLICT ( id )
DO
    UPDATE
    SET timestamp_at = EXCLUDED.timestamp_at,
        updated_at = EXCLUDED.updated_at;
    """
    pg_cursor.execute(query_template.format(pulse_name, pulse_value))


# Common helpers:

CORP_CLIENT_ID_UNKNOWN = 'unknown'
CORP_CLIENT_ID = '54476874876780670000000000000000'  # 32 chars exactly.
CLAIM_UUID = 'afd90056-claim-uuid-0023ffc0'
PARK_ID = '37'
DRIVER_PROFILE_ID = '667a89f3'
DRIVER_PROFILE_ID_NOT_ON_DB = '838ee44a'
SHIFT_ID = 'shift-2001'

COURIER_ID = '254654'
PERFORMER_ID = '{}_{}'.format(PARK_ID, DRIVER_PROFILE_ID)
PROPOSAL_ADOPTION_ID = '{}_{}_{}'.format(
    CLAIM_UUID, PARK_ID, DRIVER_PROFILE_ID,
)

EATS_ORDER_0_NR = '220203-321935'
EATS_ORDER_1_NR = '220203-190863'

EATS_REGION_ID_INT = 3

EATS_ORDER_1_ID = '56703456'
EATS_REGION_ID = '3'

# Times, how they are obtained from processing.
CLAIM_TS_MSK0 = '2020-06-20T10:30:00.000000+0300'
CLAIM_TS_MSK1 = '2020-06-20T10:31:00.000000+0300'
CLAIM_TS_MSK2 = '2020-06-20T10:32:00.000000+0300'
CLAIM_TS_MSK3 = '2020-06-20T11:25:00.000000+0300'

PULSE_NAME = 'PERFORMER_FETCH'

# Must be literally "from the future" for every event -
# so the event get handled!
PULSE_TS_MSK = '2020-06-20 12:00:00+03'

# Times, how they are posted to elpp.
CLAIM_TS_GMT0 = '2020-06-20T07:30:00+00:00'
CLAIM_TS_GMT1 = '2020-06-20T07:31:00+00:00'
CLAIM_TS_GMT2 = '2020-06-20T07:32:00+00:00'
CLAIM_TS_GMT3 = '2020-06-20T08:25:00+00:00'

CLAIM_TS_GMT_DUE = '2020-06-20T08:30:00+00:00'

WAYBILL_CREATE_TS_GMT = '2020-06-20T07:29:40+00:00'

WB_ETAS_GMT = '2020-06-20T07:48:30+00:00'
WB_ETAD0_GMT = '2020-06-20T08:10:00+00:00'
WB_ETAD1_GMT = '2020-06-20T08:20:30+00:00'

WB_AS_TS_GMT = '2020-06-20T07:45:40+00:00'
WB_VS0_TS_GMT = '2020-06-20T07:46:00+00:00'
WB_VS1_TS_GMT = '2020-06-20T07:49:00+00:00'
WB_AD0_TS_GMT = '2020-06-20T08:04:00+00:00'
WB_VD0_TS_GMT = '2020-06-20T08:06:00+00:00'
WB_AD1_TS_GMT = '2020-06-20T08:21:10+00:00'
WB_VD1_TS_GMT = '2020-06-20T08:25:00+00:00'

AGG_LAST_READY_AT = '2020-06-20T07:47:00+00:00'
AGG_LAST_GIVEN_AT = '2020-06-20T07:49:00+00:00'
AGG_LAST_TAKEN_AT = WB_VS1_TS_GMT

AGG_MIN_DIFF_RA = '12'
AGG_MIN_DIFF_GR = '2'

WAYBILL_RESOLVE_TS_GMT = WB_VD1_TS_GMT

WB_DIST_S_M = 1567
WB_DIST_D0_M = 507
WB_DIST_D1_M = 831

POINT_ID0 = '90ee9cf0-c48c-45a0-bdf4-29a34aa33bf9'
POINT_ID1 = '47e5a304-69d6-4dde-afda-3c5ac4da7937'
POINT_ID2 = '2e4a2283-6f13-49be-a664-4f2de2bbc433'
POINT_ID3 = '0c1530af-7ba3-4a41-8961-15c529c6ebfb'
POINT_ID4 = '6eca000d-d799-4397-8abb-7a3575ea53d3'
POINT_ID5 = 'b7af9d23-ed39-4e57-a04e-eb057ded4077'

CARGO_ORDER_ID = 'f68a3386-7a50-47be-82c1-1de8c297be05'


# Subject helpers:


def mk_int_factor(name, value):
    json = {'name': name, 'type': 'int', 'value': value}
    return json


def mk_string_factor(name, value):
    json = {'name': name, 'type': 'string', 'value': value}
    return json


def mk_decimal_factor(name, value):
    json = {'name': name, 'type': 'decimal', 'value': value}
    return json


def mk_datetime_factor(name, value):
    json = {'name': name, 'type': 'datetime', 'value': value}
    return json


SUBJECT_JSONS_CREATE = {
    'delivery': {
        CLAIM_UUID: {
            'id': {'id': CLAIM_UUID, 'type': 'delivery'},
            'factors': [
                mk_datetime_factor('created_at', CLAIM_TS_GMT0),
                mk_string_factor('corp_client_id', CORP_CLIENT_ID),
                mk_string_factor('eats_region_id', EATS_REGION_ID),
                mk_datetime_factor(
                    'estimated_package_ready_at', CLAIM_TS_GMT_DUE,
                ),
            ],
        },
    },
}

SUBJECT_JSONS_PRE_ASSIGN_DB_EMPTY = {
    'delivery': {
        CLAIM_UUID: {
            'id': {'id': CLAIM_UUID, 'type': 'delivery'},
            'factors': [mk_datetime_factor('proposed_at', CLAIM_TS_GMT1)],
        },
    },
    'delivery_proposal': {
        PROPOSAL_ADOPTION_ID: {
            'id': {'id': PROPOSAL_ADOPTION_ID, 'type': 'delivery_proposal'},
            'time_point_at': CLAIM_TS_GMT1,
            'relations': [
                {'id': COURIER_ID, 'type': 'performer'},
                {'id': SHIFT_ID, 'type': 'shift'},
            ],
        },
    },
}

SUBJECT_JSONS_ASSIGN = {
    'delivery': {
        CLAIM_UUID: {
            'id': {'id': CLAIM_UUID, 'type': 'delivery'},
            'relations': [{'id': COURIER_ID, 'type': 'performer'}],
            'factors': [
                mk_datetime_factor('actual_assigned_at', CLAIM_TS_GMT2),
            ],
        },
    },
}

SUBJECT_JSONS_COMPLETE = {
    'delivery': {
        CLAIM_UUID: {
            'id': {'id': CLAIM_UUID, 'type': 'delivery'},
            'time_point_at': CLAIM_TS_GMT3,
            'factors': [mk_string_factor('status', 'delivered_finish')],
        },
    },
    'point': {
        POINT_ID1: {
            'id': {'id': POINT_ID1, 'type': 'point'},
            'time_point_at': WB_VS1_TS_GMT,
            'relations': [{'id': CLAIM_UUID, 'type': 'delivery'}],
            'factors': [
                mk_string_factor('type', 'source'),
                mk_int_factor('visit_order', 2),
                mk_int_factor('distance_from_prev_waypoint', WB_DIST_S_M),
                mk_datetime_factor('planned_arrived_at', WB_ETAS_GMT),
                mk_datetime_factor('actual_arrived_at', WB_AS_TS_GMT),
                mk_datetime_factor(
                    'actual_action_completed_at', WB_VS1_TS_GMT,
                ),
            ],
        },
        POINT_ID2: {
            'id': {'id': POINT_ID2, 'type': 'point'},
            'time_point_at': WB_VD1_TS_GMT,
            'relations': [{'id': CLAIM_UUID, 'type': 'delivery'}],
            'factors': [
                mk_string_factor('type', 'destination'),
                mk_int_factor('visit_order', 3),
                mk_int_factor('distance_from_prev_waypoint', WB_DIST_D1_M),
                mk_datetime_factor('planned_arrived_at', WB_ETAD1_GMT),
                mk_datetime_factor('actual_arrived_at', WB_AD1_TS_GMT),
                mk_datetime_factor(
                    'actual_action_completed_at', WB_VD1_TS_GMT,
                ),
            ],
        },
        POINT_ID0: {
            'id': {'id': POINT_ID0, 'type': 'point'},
            'time_point_at': WB_VS0_TS_GMT,
            'relations': [{'id': CLAIM_UUID, 'type': 'delivery'}],
            'factors': [
                mk_string_factor('type', 'source'),
                mk_int_factor('visit_order', 1),
                mk_int_factor('distance_from_prev_waypoint', WB_DIST_S_M),
                mk_datetime_factor('planned_arrived_at', WB_ETAS_GMT),
                mk_datetime_factor('actual_arrived_at', WB_AS_TS_GMT),
                mk_datetime_factor(
                    'actual_action_completed_at', WB_VS0_TS_GMT,
                ),
            ],
        },
        POINT_ID3: {
            'id': {'id': POINT_ID3, 'type': 'point'},
            'time_point_at': WB_VD0_TS_GMT,
            'relations': [{'id': CLAIM_UUID, 'type': 'delivery'}],
            'factors': [
                mk_string_factor('type', 'destination'),
                mk_int_factor('visit_order', 4),
                mk_int_factor('distance_from_prev_waypoint', WB_DIST_D0_M),
                mk_datetime_factor('planned_arrived_at', WB_ETAD0_GMT),
                mk_datetime_factor('actual_arrived_at', WB_AD0_TS_GMT),
                mk_datetime_factor(
                    'actual_action_completed_at', WB_VD0_TS_GMT,
                ),
            ],
        },
    },
    'order': {
        EATS_ORDER_1_NR: {
            'id': {'id': EATS_ORDER_1_NR, 'type': 'order'},
            'factors': [
                mk_int_factor('distance_to_rest_m', WB_DIST_S_M),
                mk_int_factor('distance_to_client_m', WB_DIST_D1_M),
                mk_datetime_factor('planned_arrived_source_at', WB_ETAS_GMT),
                mk_datetime_factor('actual_arrived_source_at', WB_AS_TS_GMT),
                mk_datetime_factor(
                    'planned_arrived_destination_at', WB_ETAD1_GMT,
                ),
                mk_datetime_factor(
                    'actual_arrived_destination_at', WB_AD1_TS_GMT,
                ),
                mk_datetime_factor('taken_at', WB_VS1_TS_GMT),
                mk_datetime_factor('delivered_at', WB_VD1_TS_GMT),
                mk_int_factor('in_batch_order', 1),
                mk_datetime_factor('last_package_ready_at', AGG_LAST_READY_AT),
                mk_datetime_factor('last_package_given_at', AGG_LAST_GIVEN_AT),
                mk_datetime_factor('last_package_taken_at', AGG_LAST_TAKEN_AT),
                mk_decimal_factor(
                    'min_ready_accepted_diff_m', AGG_MIN_DIFF_RA,
                ),
                mk_decimal_factor('min_given_ready_diff_m', AGG_MIN_DIFF_GR),
            ],
        },
        EATS_ORDER_0_NR: {
            'id': {'id': EATS_ORDER_0_NR, 'type': 'order'},
            'factors': [
                mk_int_factor('distance_to_rest_m', WB_DIST_S_M),
                mk_int_factor('distance_to_client_m', WB_DIST_D0_M),
                mk_datetime_factor('planned_arrived_source_at', WB_ETAS_GMT),
                mk_datetime_factor('actual_arrived_source_at', WB_AS_TS_GMT),
                mk_datetime_factor(
                    'planned_arrived_destination_at', WB_ETAD0_GMT,
                ),
                mk_datetime_factor(
                    'actual_arrived_destination_at', WB_AD0_TS_GMT,
                ),
                mk_datetime_factor('taken_at', WB_VS0_TS_GMT),
                mk_datetime_factor('delivered_at', WB_VD0_TS_GMT),
                mk_int_factor('in_batch_order', 2),
                mk_datetime_factor('last_package_ready_at', AGG_LAST_READY_AT),
                mk_datetime_factor('last_package_given_at', AGG_LAST_GIVEN_AT),
                mk_datetime_factor('last_package_taken_at', AGG_LAST_TAKEN_AT),
                mk_decimal_factor(
                    'min_ready_accepted_diff_m', AGG_MIN_DIFF_RA,
                ),
                mk_decimal_factor('min_given_ready_diff_m', AGG_MIN_DIFF_GR),
            ],
        },
    },
}


# Kwarg helpers:


def get_kwargs_with_payload(
        event_type,
        event_status,
        event_ts,
        event_payload,
        corp_client_id=CORP_CLIENT_ID,
):
    return {
        'corp_client_id': corp_client_id,
        'cargo_event_claim_uuid': CLAIM_UUID,
        'cargo_event_type': event_type,
        'cargo_event_timestamp': event_ts,
        'cargo_event_claim_status': event_status,
        'cargo_event_payload_data': event_payload,
    }


def get_kwargs_with_corp_client(corp_client_id):
    return get_kwargs_with_payload(
        'assign',
        'performer_found',
        CLAIM_TS_MSK1,
        {'driver_profile_id': DRIVER_PROFILE_ID, 'park_id': PARK_ID},
        corp_client_id=corp_client_id,
    )


CFG_CARGO_CORP_CLIENTS = [CORP_CLIENT_ID]

KWARGS_PRE_ASSIGN = get_kwargs_with_payload(
    'pre_assign',
    'performer_assigned',
    CLAIM_TS_MSK1,
    {'driver_profile_id': DRIVER_PROFILE_ID, 'park_id': PARK_ID},
)

KWARGS_ASSIGN = get_kwargs_with_payload(
    'assign',
    'performer_found',
    CLAIM_TS_MSK2,
    {'driver_profile_id': DRIVER_PROFILE_ID, 'park_id': PARK_ID},
)

KWARGS_COMPLETE = get_kwargs_with_payload(
    'complete',
    'delivered_finish',
    CLAIM_TS_MSK3,
    {
        'cargo_order_id': CARGO_ORDER_ID,
        'driver_profile_id': DRIVER_PROFILE_ID,
        'park_id': PARK_ID,
    },
)

KWARGS_COMPLETE_EMPTY = get_kwargs_with_payload(
    'complete',
    'cancelled',
    CLAIM_TS_MSK3,
    {'cargo_order_id': None, 'driver_profile_id': None, 'park_id': None},
)


# Mock helpers:

# The minimal data to satisfy claims/full parser.
CLAIMS_JSON_CLAIMS_FULL_BASE = {
    'created_ts': CLAIM_TS_GMT0,
    'id': CLAIM_UUID,
    'items': [],
    'route_points': [],
    'status': 'new',
    'updated_ts': CLAIM_TS_GMT0,
    'user_request_revision': 'v1',
    'version': 1,
}


def mk_route_point(point_id, external_order_id):
    json = {
        'id': point_id,
        'contact': {
            'name': 'test_name',
            'personal_phone_id': 'f36fd62356c74ed4875daea7a3ba8d91',
        },
        'address': {
            'fullname': 'Россия, Москва, улица Нижняя Масловка, 18',
            'shortname': 'улица Нижняя Масловка 18 ',
            'coordinates': [37.571938, 55.791901],
            'country': 'Российская Федерация',
            'city': 'Москва',
            'street': 'улица Нижняя Масловка',
            'building': '18 ',
            'sflat': '1',
            'comment': 'дест эксп\nКлиент: test',
        },
        'type': 'destination',
        'visit_order': 1,
        'visit_status': 'pending',
        'visited_at': {},
        'external_order_id': external_order_id,
    }
    return json


def get_claims_json_claims_full():
    json = CLAIMS_JSON_CLAIMS_FULL_BASE
    json['route_points'].append(mk_route_point(1, EATS_ORDER_0_NR))
    json['due'] = CLAIM_TS_GMT_DUE
    json['custom_context'] = {'region_id': EATS_REGION_ID_INT}
    return json


SEGMENT_ID0 = '60737ae9-fa23-43da-af2e-22252f740938'
SEGMENT_ID1 = 'bf5dcd45-8108-4c95-b066-2463c6938840'
WAYBILL_CONTACT = {
    'name': 'Дефолт Юзернейм',
    'personal_phone_id': '47c1332d90564e8196841734adbc506a',
}
WAYBILL_CLIENT_INFO = {
    'payment_info': {
        'type': 'corp',
        'method_id': 'corp-b8cfabb9d01d48079e35655c253035a9',
    },
    'user_locale': 'ru',
}
WAYBILL_POINT_COORDS = [37.576133, 55.690735]
WAYBILL_POINT_LABEL = 'cool_point'

LOC_ID0 = '17195fdb8e1e4679b1a336ba8c86cbee'
LOC_ID1 = '2dae9362960d484391a6cd58bee2a4ca'
LOC_ID2 = '34b0a858ccd04841ade83cd14f72beed'


def mk_waybill_point(point_id, segment_id, visit_order):
    json = {
        'segment_id': segment_id,
        'point_id': point_id,
        'visit_order': visit_order,
    }
    return json


def mk_claim_point(point_id, visit_order, location_id, point_type):
    json = {
        'point_id': point_id,
        'visit_order': visit_order,
        'location_id': location_id,
        'type': point_type,
        'contact': WAYBILL_CONTACT,
    }
    return json


def mk_exec_point(
        point_id,
        segment_id,
        visit_order,
        location_id,
        point_type,
        visit_status,
        eta,
        dist_to_point,
        order_nr,
        changelog,
):
    json = {
        'segment_id': segment_id,
        'point_id': point_id,
        'is_resolved': True,
        'last_status_change_ts': changelog[-1]['timestamp'],
        'visit_status': visit_status,
        'changelog': changelog,
        'visit_order': visit_order,
        'external_order_id': order_nr,
        'claim_point_id': 1042091,
        'type': point_type,
        'label': WAYBILL_POINT_LABEL,
        'phones': [],
        'address': {
            'location_id': location_id,
            'coordinates': WAYBILL_POINT_COORDS,
        },
        'need_confirmation': False,
        'location': {'id': location_id, 'coordinates': WAYBILL_POINT_COORDS},
    }
    if eta is not None:
        json['eta'] = eta
    if dist_to_point is not None:
        json['dist_to_point'] = dist_to_point
    return json


def mk_changelog(status, timestamp):
    json = {'status': status, 'timestamp': timestamp}
    return json


# The minimal data to satisfy waybill/info parser.
DISPATCH_JSON_WAYBILL_INFO = {
    'waybill': {
        'router_id': 'logistic-dispatch',
        'external_ref': (
            'logistic-dispatch/dc772b4b-979d-49b1-bb31-65fd7927b061'
        ),
        'points': [
            mk_waybill_point(POINT_ID0, SEGMENT_ID0, 1),
            mk_waybill_point(POINT_ID1, SEGMENT_ID1, 2),
            mk_waybill_point(POINT_ID2, SEGMENT_ID1, 3),
            mk_waybill_point(POINT_ID3, SEGMENT_ID0, 4),
            mk_waybill_point(POINT_ID4, SEGMENT_ID1, 5),
            mk_waybill_point(POINT_ID5, SEGMENT_ID0, 6),
        ],
        'taxi_order_requirements': {},
        'special_requirements': {'virtual_tariffs': []},
        'optional_return': False,
        'items': [],
    },
    'dispatch': {
        'revision': 10,
        'created_ts': WAYBILL_CREATE_TS_GMT,
        'updated_ts': WAYBILL_CREATE_TS_GMT,
        'is_waybill_accepted': True,
        'is_waybill_declined': False,
        'is_performer_assigned': False,
        'status': 'resolved',
        'resolution': 'complete',
        'resolved_at': WAYBILL_RESOLVE_TS_GMT,
    },
    'execution': {
        'paper_flow': False,
        'points': [
            mk_exec_point(
                POINT_ID0,
                SEGMENT_ID0,
                1,
                LOC_ID0,
                'source',
                'visited',
                WB_ETAS_GMT,
                WB_DIST_S_M,
                EATS_ORDER_0_NR,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('arrived', WB_AS_TS_GMT),
                    mk_changelog('visited', WB_VS0_TS_GMT),
                ],
            ),
            mk_exec_point(
                POINT_ID1,
                SEGMENT_ID1,
                2,
                LOC_ID0,
                'source',
                'visited',
                WB_ETAS_GMT,
                0,
                EATS_ORDER_1_NR,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('arrived', WB_AS_TS_GMT),
                    mk_changelog('visited', WB_VS1_TS_GMT),
                ],
            ),
            mk_exec_point(
                POINT_ID2,
                SEGMENT_ID1,
                3,
                LOC_ID1,
                'destination',
                'visited',
                WB_ETAD1_GMT,
                WB_DIST_D1_M,
                EATS_ORDER_1_NR,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('arrived', WB_AD1_TS_GMT),
                    mk_changelog('visited', WB_VD1_TS_GMT),
                ],
            ),
            mk_exec_point(
                POINT_ID3,
                SEGMENT_ID0,
                4,
                LOC_ID1,
                'destination',
                'visited',
                WB_ETAD0_GMT,
                WB_DIST_D0_M,
                None,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('arrived', WB_AD0_TS_GMT),
                    mk_changelog('visited', WB_VD0_TS_GMT),
                ],
            ),
            mk_exec_point(
                POINT_ID4,
                SEGMENT_ID1,
                5,
                LOC_ID1,
                'return',
                'skipped',
                None,
                None,
                None,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('skipped', WAYBILL_RESOLVE_TS_GMT),
                ],
            ),
            mk_exec_point(
                POINT_ID5,
                SEGMENT_ID0,
                6,
                LOC_ID2,
                'return',
                'skipped',
                None,
                None,
                None,
                [
                    mk_changelog('pending', WAYBILL_CREATE_TS_GMT),
                    mk_changelog('skipped', WAYBILL_RESOLVE_TS_GMT),
                ],
            ),
        ],
        'segments': [
            {
                'id': SEGMENT_ID0,
                'status': 'delivered_finish',
                'zone_id': 'moscow',
                'client_info': WAYBILL_CLIENT_INFO,
                'claim_id': '891a5206405448f48afa46f54e4ec056',
            },
            {
                'id': SEGMENT_ID1,
                'status': 'delivered_finish',
                'zone_id': 'moscow',
                'client_info': WAYBILL_CLIENT_INFO,
                'claim_id': '891a5206405448f48afa46f54e4ec056',
            },
        ],
    },
    'diagnostics': {},
    'segments': [
        {
            'id': SEGMENT_ID0,
            'items': [],
            'locations': [],
            'points': [
                mk_claim_point(POINT_ID0, 1, LOC_ID0, 'pickup'),
                mk_claim_point(POINT_ID3, 4, LOC_ID1, 'dropoff'),
                mk_claim_point(POINT_ID5, 6, LOC_ID2, 'return'),
            ],
            'performer_requirements': {
                'taxi_classes': [
                    'courier',
                    'express',
                    'eda',
                    'lavka',
                    'scooters',
                ],
                'special_requirements': {'virtual_tariffs': []},
            },
            'allow_batch': True,
            'allow_alive_batch_v1': False,
            'client_info': WAYBILL_CLIENT_INFO,
            'zone_id': 'moscow',
        },
        {
            'id': SEGMENT_ID1,
            'items': [],
            'locations': [],
            'points': [
                mk_claim_point(POINT_ID1, 2, LOC_ID0, 'pickup'),
                mk_claim_point(POINT_ID2, 3, LOC_ID1, 'dropoff'),
                mk_claim_point(POINT_ID4, 5, LOC_ID2, 'return'),
            ],
            'performer_requirements': {
                'taxi_classes': [
                    'courier',
                    'express',
                    'eda',
                    'lavka',
                    'scooters',
                ],
                'special_requirements': {'virtual_tariffs': []},
            },
            'allow_batch': True,
            'allow_alive_batch_v1': False,
            'client_info': WAYBILL_CLIENT_INFO,
            'zone_id': 'moscow',
        },
    ],
}


DP_EDA_ORDERS_PROVIDER = {
    'cargo': False,
    'eda': True,
    'lavka': False,
    'retail': False,
    'taxi': False,
    'taxi_walking_courier': False,
}
DP_DATA = {'orders_provider': DP_EDA_ORDERS_PROVIDER}


def mk_dp_retrieve_response(request):
    profiles_json = {'profiles': []}
    courier_ids_list = request.json['id_in_set']
    for courier_id in courier_ids_list:
        dp_item = {'data': DP_DATA, 'park_driver_profile_id': courier_id}
        profiles_json['profiles'].append(dp_item)

    return profiles_json


# Tests:

# corp_client
# Checks, whether the events are skipped by corp_client_id.
@pytest.mark.pgsql('eats_logistics_performer_payouts', files=PG_FILES)
@pytest.mark.parametrize(
    'stq_kwargs,skip_count,subject_calls,dp_calls',
    [
        pytest.param(
            get_kwargs_with_corp_client(CORP_CLIENT_ID_UNKNOWN),
            1,
            0,
            0,
            id='skip, unknown',
        ),
        pytest.param(
            get_kwargs_with_corp_client(CORP_CLIENT_ID),
            1,
            0,
            0,
            id='skip, no config',
        ),
        pytest.param(
            get_kwargs_with_corp_client('afde-corp-client-not-in-config-0'),
            1,
            0,
            0,
            marks=pytest.mark.config(
                EATS_LOGISTICS_PERFORMER_PAYOUTS_CARGO_CORP_CLIENTS=[
                    '1190-corp-client-in-config-00000',
                    '1247-corp-client-in-config-00000',
                ],
            ),
            id='skip, not in config',
        ),
        pytest.param(
            get_kwargs_with_corp_client('afde-corp-client-in-config-00000'),
            0,
            1,
            1,
            marks=pytest.mark.config(
                EATS_LOGISTICS_PERFORMER_PAYOUTS_CARGO_CORP_CLIENTS=[
                    'afde-corp-client-in-config-00000',
                ],
            ),
            id='no skip',
        ),
    ],
)
async def test_claim_event_corp_client(
        dp_calls,
        mockserver,
        pgsql,
        skip_count,
        stq_kwargs,
        stq_runner,
        subject_calls,
        testpoint,
):
    # driver-profiles mock.
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def driver_profiles_handler(request):
        return mk_dp_retrieve_response(request)

    # cargo-claims mock.
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_claims_full_handler(request):
        return get_claims_json_claims_full()

    # Permissive testpoint.
    @testpoint('skip_cargo_event')
    def skip_tp(data):
        pass

    # Permissive testpoint
    @testpoint('test_subject_from_claim_event')
    def subject_tp(data):
        pass

    pg_cursor = pgsql[PG_DBNAME].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    upsert_pulse(pg_cursor, PULSE_NAME, PULSE_TS_MSK)

    await stq_runner.eats_logistics_performer_get_cargo_events.call(
        task_id='test_task', kwargs=stq_kwargs,
    )

    assert skip_tp.times_called == skip_count
    assert subject_tp.times_called == subject_calls
    assert driver_profiles_handler.times_called == dp_calls
    assert claims_claims_full_handler.times_called + skip_count == 1


# payload parsing
# Ensures, that incomplete payload aborts the task, but does not fail it
# (so it is not retried in that case).
# No mocks required here, because handler usage happens after successful
# parsing.
@pytest.mark.pgsql('eats_logistics_performer_payouts', files=PG_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_CARGO_CORP_CLIENTS=CFG_CARGO_CORP_CLIENTS,
)
@pytest.mark.parametrize(
    'stq_kwargs',
    [
        pytest.param(
            get_kwargs_with_payload(
                'assign',
                'performer_found',
                CLAIM_TS_MSK0,
                {'driver_profile_id': None, 'park_id': PARK_ID},
            ),
            id='faulty_assign',
        ),
        pytest.param(
            get_kwargs_with_payload(
                'complete',
                'cancelled',
                CLAIM_TS_MSK0,
                {
                    'cargo_order_id': None,
                    'driver_profile_id': DRIVER_PROFILE_ID,
                    'park_id': PARK_ID,
                },
            ),
            id='faulty_complete',
        ),
    ],
)
async def test_claim_event_parse(
        mockserver, pgsql, stq, stq_kwargs, stq_runner, testpoint,
):
    # driver-profiles mock.
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def driver_profiles_handler(request):
        return mk_dp_retrieve_response(request)

    # Permissive testpoint.
    @testpoint('skip_cargo_event')
    def skip_tp(data):
        pass

    # Permissive testpoint
    @testpoint('test_subject_request')
    def subject_tp(data):
        pass

    pg_cursor = pgsql[PG_DBNAME].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    upsert_pulse(pg_cursor, PULSE_NAME, PULSE_TS_MSK)

    await stq_runner.eats_logistics_performer_get_cargo_events.call(
        task_id='test_task', kwargs=stq_kwargs,
    )

    assert driver_profiles_handler.times_called >= 0  # Useless assert for pep8
    assert skip_tp.times_called == 0
    assert subject_tp.times_called == 0


# performer checking
# Ensures, that tasks, referring to driver profile, not present on DB are
# skipped
@pytest.mark.pgsql('eats_logistics_performer_payouts', files=PG_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_CARGO_CORP_CLIENTS=CFG_CARGO_CORP_CLIENTS,
)
@pytest.mark.parametrize(
    'stq_kwargs',
    [
        pytest.param(
            get_kwargs_with_payload(
                'assign',
                'performer_found',
                CLAIM_TS_MSK0,
                {
                    'driver_profile_id': DRIVER_PROFILE_ID_NOT_ON_DB,
                    'park_id': PARK_ID,
                },
            ),
            id='dp_not_found_assign',
        ),
        pytest.param(
            get_kwargs_with_payload(
                'complete',
                'cancelled',
                CLAIM_TS_MSK0,
                {
                    'cargo_order_id': CARGO_ORDER_ID,
                    'driver_profile_id': DRIVER_PROFILE_ID_NOT_ON_DB,
                    'park_id': PARK_ID,
                },
            ),
            id='dp_not_found_complete',
        ),
    ],
)
async def test_claim_event_no_performer(
        mockserver, pgsql, stq, stq_kwargs, stq_runner, testpoint,
):
    # driver-profiles retrieve mock.
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def driver_profiles_handler(request):
        return mk_dp_retrieve_response(request)

    # Permissive testpoint.
    @testpoint('skip_cargo_event')
    def skip_tp(data):
        pass

    # Permissive testpoint.
    @testpoint('performer_not_on_db')
    def no_performer_tp(data):
        pass

    # Permissive testpoint
    @testpoint('test_subject_request')
    def subject_tp(data):
        pass

    pg_cursor = pgsql[PG_DBNAME].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    upsert_pulse(pg_cursor, PULSE_NAME, PULSE_TS_MSK)

    await stq_runner.eats_logistics_performer_get_cargo_events.call(
        task_id='test_task', kwargs=stq_kwargs,
    )

    assert driver_profiles_handler.times_called >= 0  # Useless assert for pep8
    assert skip_tp.times_called == 0
    assert no_performer_tp.times_called == 1
    assert subject_tp.times_called == 0


# handling
# Checks, whether the correct factors are posted, while handling a given event.
@pytest.mark.pgsql('eats_logistics_performer_payouts', files=PG_FILES)
@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_CARGO_CORP_CLIENTS=CFG_CARGO_CORP_CLIENTS,
)
@pytest.mark.parametrize(
    'stq_kwargs,claims_full_calls,waybill_info_calls,subject_calls,order_linking_calls,subject_jsons',  # noqa: E501
    [
        pytest.param(
            KWARGS_ASSIGN, 1, 0, 1, 0, SUBJECT_JSONS_ASSIGN, id='assign',
        ),
        pytest.param(
            KWARGS_COMPLETE, 0, 0, 0, 0, SUBJECT_JSONS_COMPLETE, id='complete',
        ),
    ],
)
async def test_claim_event_handling(
        claims_full_calls,
        mockserver,
        pgsql,
        stq,
        stq_kwargs,
        stq_runner,
        subject_calls,
        subject_jsons,
        testpoint,
        waybill_info_calls,
        order_linking_calls,
):
    # driver-profiles mock.
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def driver_profiles_handler(request):
        return mk_dp_retrieve_response(request)

    # cargo-claims mock.
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def claims_claims_full_handler(request):
        return get_claims_json_claims_full()

    # cargo-dispatch mock.
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def dispatch_waybill_info_handler(request):
        return DISPATCH_JSON_WAYBILL_INFO

    # Permissive testpoint.
    @testpoint('skip_cargo_event')
    def skip_tp(data):
        pass

    # Strict testpoint
    @testpoint('test_subject_from_claim_event')
    def subject_tp(data):
        subj_type = data['id']['type']
        subj_id = data['id']['id']

        subjects = subject_jsons.get(subj_type)
        assert subjects is not None

        subject = subjects.get(subj_id)
        assert subject is not None

        assert data == subject

    pg_cursor = pgsql[PG_DBNAME].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    upsert_pulse(pg_cursor, PULSE_NAME, PULSE_TS_MSK)

    await stq_runner.eats_logistics_performer_get_cargo_events.call(
        task_id='test_task', kwargs=stq_kwargs,
    )

    assert driver_profiles_handler.times_called >= 0  # Useless assert for pep8
    assert skip_tp.times_called == 0
    assert subject_tp.times_called == subject_calls
    assert claims_claims_full_handler.times_called == claims_full_calls
    assert dispatch_waybill_info_handler.times_called == waybill_info_calls
    assert (
        stq.eats_logistics_performer_payouts_link_orders.times_called
        == order_linking_calls
    )
