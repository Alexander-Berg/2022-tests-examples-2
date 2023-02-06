import copy
import datetime

import pytest

from dmp_suite.clickhouse.meta import CHMeta
from atlas_etl.layer.clickhouse.ods_order.impl import (
    data_processor,
    transform_clients
)
from atlas_etl.layer.clickhouse.ods_order.table import AtlasOdsOrder

from dmp_suite.string_utils import to_unicode

EMPTY_PARSED_DOCUMENT = {
    b'plan_cost__alternative_type': None,
    b'plan_cost__by_tariffs_values': None,
    b'plan_cost__by_tariffs_names': None,
    b'cand_first_subvention_geoareas': None,
    b'cand_perf_gprs_time': None,
    b'discount_price': None,
    b'transporting_time': None,
    b'price_modifiers__tariff_categories': None,
    b'cand_perf_cp__left_dist': None,
    b'source_geopoint': None,
    b'driver_id': None,
    b'cand_cnt': None,
    b'cand_perf_driver_eta': None,
    b'cand_perf_driver_points': None,
    b'source_geoareas': None,
    b'discount_reason': None,
    b'city': None,
    b'discount_driver_less_coeff': None,
    b'user_id': None,
    b'fixed_price__show_price_in_taximeter': None,
    b'application': None,
    b'surge_value': None,
    b'user_fraud': None,
    b'source_quadkey': None,
    b'cand_first_cp__id': None,
    b'cand_first_adjusted_point__geopoint': None,
    b'cand_perf_adjusted_point__geopoint': None,
    b'updated': None,
    b'cand_first_reposition_mode': None,
    b'cand_first_taximeter_version': None,
    b'cand_perf_dp': None,
    b'cand_first_push_on_driver_arriving_send_at_eta': None,
    b'cand_perf_cp__left_time': None,
    b'cand_first_driver_points': None,
    b'fixed_price__price_original': None,
    b'cand_perf_line_dist': None,
    b'cand_first_gprs_time': None,
    b'cand_perf_dist': None,
    b'corp_client_id': None,
    b'corp_user_id': None,
    b'corp_contract_id': None,
    b'discount_value': None,
    b'cand_perf_push_on_driver_arriving_send_at_eta': None,
    b'plan_cost__extra_distance_multiplier': None,
    b'discount_discard_surge': None,
    b'failed_cnt': None,
    b'price_modifiers__reason': None,
    b'request_classes': None,
    b'car_class': None,
    b'car_class_refined': None,
    b'paid_supply_price': None,
    b'price_modifiers__pay_subventions': None,
    b'dest_cnt': None,
    b'payment_type': None,
    b'payment_method_id': None,
    b'surge_beta': None,
    b'dest_geopoint': None,
    b'plan_cost__distance': None,
    b'cand_perf_push_on_driver_arriving_sent': None,
    b'driver_dbid': None,
    b'cancelled_cnt': None,
    b'assigned_cnt': None,
    b'cand_first_driver_eta': None,
    b'no_cars_order': None,
    b'fixed_price__destination': None,
    b'price_modifiers__type': None,
    b'cand_first_time': None,
    b'cost': None,
    b'plan_cost__recalculated': None,
    b'cand_first_driver_classes': None,
    b'fixed_price__price': None,
    b'driver_license': None,
    b'cand_perf_subvention_geoareas': None,
    b'cancel_wasted_time': None,
    b'fixed_price__destination_quadkey': None,
    b'surcharge': None,
    b'cand_first_cp__left_time': None,
    b'order_type': None,
    b'cand_perf_reposition_mode': None,
    b'status_updated': None,
    b'driving_time': None,
    b'cand_perf_taximeter_version': None,
    b'plan_cost__time': None,
    b'dttm_utc_1_min': None,
    b'driver_clid': None,
    b'cand_perf_cp__dest_quadkey': None,
    b'ts_1_min': None,
    b'cand_first_cp__left_dist': None,
    b'seen_timeout_cnt': None,
    b'cand_first_point': None,
    b'fixed_price__driver_price': None,
    b'status': None,
    b'reorder_cnt': None,
    b'offer_timeout_cnt': None,
    b'order_id': None,
    b'taxi_status': None,
    b'cand_perf_cp__id': None,
    b'cand_first_dist': None,
    b'dest_quadkey': None,
    b'requirements': None,
    b'cand_first_push_on_driver_arriving_sent': None,
    b'search_time': None,
    b'cand_perf_point': None,
    b'cand_first_cp__dest_quadkey': None,
    b'seen_cnt': None,
    b'price_modifiers__value': None,
    b'cand_perf_driver_classes': None,
    b'created': None,
    b'cand_perf_time': None,
    b'driver_uuid': None,
    b'surge_alpha': None,
    b'cand_first_line_dist': None,
    b'cand_first_dp': None,
    b'paid_supply': None,
    b'user_agent': None,
    b'discount_method': None,
    b'nearest_zone': None,
    b'waiting_time': None,
    b'cand_first_tags': None,
    b'fastest_class_flg': None,
    b'calc_alternative_type': None,
    b'user_tags': None,
    b'overdraft_flg': None,
    b'order_due': None,
    b'preorder_flg': False,
    b'cand_perf_tags': None,
    b'source_metrica_action': None,
    b'multiorder_order_number': None,
    b'order_source': 'yandex',
    b'cargo_ref_id': None,
    b'agent_id': None,
    b'agent_order_id': None,
    b'agent_user_type': None,
    b'dispatch_check_in__pickup_line': None,
    b'dispatch_check_in__check_in_time': None,
    b'reject_cnt': None,
    b'reject_manual_cnt': None,
    b'reject_autocancel_cnt': None,
    b'reject_seenimpossible_cnt': None,
    b'reject_missingtariffs_cnt': None,
    b'reject_wrongway_cnt': None,
    b'seen_received_to_assigned_time': None,
    b'performer_candidate_index': None,
    b'candidates_taximeter_version': None,
}


def test_table_structure():
    meta = CHMeta(AtlasOdsOrder)
    assert set(meta.field_names()) == set(map(to_unicode, EMPTY_PARSED_DOCUMENT.keys()))


def test_empty():
    assert dict(data_processor({})({})) == EMPTY_PARSED_DOCUMENT


def test_surge_beta():
    order_proc_data = {
        'order': {
            'request': {
                'sp': 0.9,
                'sp_alpha': 1.7,
                'sp_beta': 0.4,
                'sp_surcharge': 0.0
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)

    expected.update({
        b'surge_alpha': 1.7,
        b'surge_beta': 0.4,
        b'surge_value': 0.9,
        b'surcharge': 0.0
    })

    assert result == expected


def test_corp_fields():
    order_proc_data = {
        'order': {
            'request': {
                'corp': {
                    'client_id': '123ert',
                    'user_id': '456tyu'
                }
            }
        }
    }
    corp_client_to_contract = {
        '123ert': '098/hjk'
    }
    result = dict(data_processor(corp_client_to_contract)(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)

    expected.update({
        b'corp_client_id': '123ert',
        b'corp_user_id': '456tyu',
        b'corp_contract_id': '098/hjk',
    })

    assert result == expected


def test_clients_transform():
    clients_data = [
        {'_id': '123'},
        {
            '_id': '234',
            'services': {
                'taxi': {
                    'contract_id': 'ct/234',
                    'is_active': True
                }
            }
        },
        {
            '_id': '345',
            'services': {
                'taxi': {
                    'contract_id': 'ct/345',
                    'is_active': False
                }
            }
        },
        {
            '_id': '456',
            'services': {
                'taxi': {
                    'contract_id': ''
                }
            }
        },
    ]
    result = {k: v for k, v in transform_clients(clients_data)}
    expected = {
        '234': 'ct/234'
    }
    assert result == expected


def test_payment_fields():
    order_proc_data = {
        'order': {
            'request': {
                'payment': {
                    'type': 'coop_account',
                    'payment_method_id': 'business-ccad1e0978144466b64b4ff469ee0467'
                }
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))

    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'payment_type': 'coop_account',
        b'payment_method_id': 'business-ccad1e0978144466b64b4ff469ee0467',
    })

    assert result == expected


def test_cargo_fields():
    order_proc_data = {
        'order': {
            'request': {
                'cargo_ref_id': 'order/bc13af65-3d7b-4b2a-b3ed-e76eee97a6eb'
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'cargo_ref_id': 'order/bc13af65-3d7b-4b2a-b3ed-e76eee97a6eb',
    })

    assert result == expected


@pytest.mark.parametrize(
    'performer_index, expected_car_class, expected_car_class_refined',
    [
        (None, 'econom', 'econom',),
        (0, 'econom', 'start'),
        (1, 'econom', 'business'),
        (2, 'econom', 'econom'),
    ]
)
def test_car_class(performer_index, expected_car_class, expected_car_class_refined):
    order_proc_data = {
        'order': {
            'request': {
                'class': [
                    'econom',
                    'business',
                    'start'
                ]
            }
        },
        'candidates': [
            {'tariff_class': 'start'},
            {'tariff_class': 'business'},
            {'tariff_class': 'econom'},
        ],
        'performer': {
            'candidate_index': performer_index
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'cand_cnt': 3,
        b'car_class': expected_car_class,
        b'car_class_refined': expected_car_class_refined,
        b'fastest_class_flg': True,
        b'request_classes': ['econom', 'business', 'start'],
        b'candidates_taximeter_version': ['', '', ''],
        b'performer_candidate_index': performer_index,
    })

    assert result == expected


@pytest.mark.parametrize(
    'order_proc_data, expected_order_source',
    [
        ({}, 'yandex'),
        ({'order': {}}, 'yandex'),
        ({'order': {'source': 'call_center'}}, 'call_center'),
        ({'order': {'source': 'light_business'}}, 'light_business')
    ]
)
def test_order_source(order_proc_data, expected_order_source):
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'order_source': expected_order_source,
    })

    assert result == expected


def test_order_agent_fields():
    order_proc_data = {
        'order': {
            'agent': {
                'agent_id': 'gepard',
                'agent_order_id': '1234567890',
                'agent_user_type': 'corporate'
            }
        }
    }

    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'agent_id': 'gepard',
        b'agent_order_id': '1234567890',
        b'agent_user_type': 'corporate'
    })

    assert result == expected


def test_check_in_fields():
    order_proc_data = {
        'dispatch_check_in': {
            'pickup_line': 'svo_d_line1',
            'check_in_time': datetime.datetime(2021, 9, 21, 9, 52, 34, 281)
        }
    }

    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update({
        b'dispatch_check_in__pickup_line': 'svo_d_line1',
        b'dispatch_check_in__check_in_time': 1632217954,
    })

    assert result == expected


def test_fix_null_status_updates_element():
    order_proc_data = {
        'created': datetime.datetime(2021, 9, 21, 9, 52, 34, 281),
        'order_info': {
            'statistics': {
                'status_updates': [None]
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update(
        {
            b'assigned_cnt': 0,
            b'cancelled_cnt': 0,
            b'created': datetime.datetime(2021, 9, 21, 9, 52, 34, 281),
            b'dttm_utc_1_min': '2021-09-21 09:52:34',
            b'failed_cnt': 0,
            b'offer_timeout_cnt': 0,
            b'seen_cnt': 0,
            b'seen_timeout_cnt': 0,
            b'ts_1_min': 1632217954,
            b'reject_cnt': 0,
            b'reject_manual_cnt': 0,
            b'reject_autocancel_cnt': 0,
            b'reject_seenimpossible_cnt': 0,
            b'reject_missingtariffs_cnt': 0,
            b'reject_wrongway_cnt': 0,
            b'seen_received_to_assigned_time': [],
        }
    )
    assert result == expected


def test_status_updates_reject_stats():
    def gen_status_created(start: datetime.datetime, step=datetime.timedelta(microseconds=20)):
        dttm = start
        while True:
            yield dttm
            dttm += step

    c_gen = gen_status_created(datetime.datetime(2021, 9, 21, 9, 52, 34, 283))
    order_proc_data = {
        'created': datetime.datetime(2021, 9, 21, 9, 52, 34, 281),
        'order_info': {
            'statistics': {
                'status_updates': [
                    {'c': next(c_gen), 'q': 'reject', 'r': 'manual'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'manual'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'autocancel'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'seenimpossible'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'missingtariffs'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'autocancel'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'missingtariffs'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'missingtariffs'},
                    {'c': next(c_gen), 'q': 'reject', 'r': 'wrongway'},
                ]
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update(
        {
            b'assigned_cnt': 0,
            b'cancelled_cnt': 0,
            b'created': datetime.datetime(2021, 9, 21, 9, 52, 34, 281),
            b'dttm_utc_1_min': '2021-09-21 09:52:34',
            b'failed_cnt': 0,
            b'offer_timeout_cnt': 0,
            b'seen_cnt': 0,
            b'seen_timeout_cnt': 0,
            b'ts_1_min': 1632217954,
            b'reject_cnt': 9,
            b'reject_manual_cnt': 2,
            b'reject_autocancel_cnt': 2,
            b'reject_seenimpossible_cnt': 1,
            b'reject_missingtariffs_cnt': 3,
            b'reject_wrongway_cnt': 1,
            b'seen_received_to_assigned_time': []
        }
    )
    assert result == expected


def test_status_updates_seen_received_to_assigned():
    order_proc_data = {
        'created': datetime.datetime(2022, 5, 3, 21, 38, 45),
        'order_info': {
            'statistics': {
                'status_updates': [
                    {'c': datetime.datetime(2022, 5, 3, 21, 38, 46), 'q': 'create', 's': 'pending'},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 27), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 27), 'q': 'seen_received', 'i': 0},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 28), 'q': 'seen', 'i': 0},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 33), 'q': 'reject', 'r': 'manual', 'i': 0},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 35), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 35), 'q': 'unset_unconfirmed_performer', 'i': 1},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 43), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 44), 'q': 'seen_received', 'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 45), 'q': 'seen', 'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 50), 'q': 'requestconfirm_assigned', 's': 'assigned',
                     'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 39, 50), 'q': 'requestconfirm_driving', 't': 'driving',
                     'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 47, 20), 'q': 'requestconfirm_waiting', 't': 'waiting',
                     'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 49, 23), 'q': 'requestconfirm_transporting',
                     't': 'transporting', 'i': 2},
                    {'c': datetime.datetime(2022, 5, 3, 21, 54, 52), 'q': 'destinations_statuses_updated'},
                    {'c': datetime.datetime(2022, 5, 3, 21, 54, 59), 'q': 'destinations_statuses_updated'},
                    {'c': datetime.datetime(2022, 5, 3, 22, 3, 0), 'q': 'requestconfirm_complete', 's': 'finished',
                     't': 'complete', 'i': 2},
                ]
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update(
        {
            b'assigned_cnt': 1,
            b'cancelled_cnt': 0,
            b'created': datetime.datetime(2022, 5, 3, 21, 38, 45),
            b'driving_time': 450.0,
            b'dttm_utc_1_min': '2022-05-03 21:38:45',
            b'failed_cnt': 0,
            b'offer_timeout_cnt': 0,
            b'search_time': 65.0,
            b'seen_cnt': 2,
            b'seen_timeout_cnt': 0,
            b'transporting_time': 817.0,
            b'ts_1_min': 1651613925,
            b'reject_cnt': 1,
            b'reject_manual_cnt': 1,
            b'reject_autocancel_cnt': 0,
            b'reject_seenimpossible_cnt': 0,
            b'reject_missingtariffs_cnt': 0,
            b'reject_wrongway_cnt': 0,
            b'seen_received_to_assigned_time': [6.0],
            b'waiting_time': 450.0,
        }
    )
    assert result == expected


def test_status_updates_seen_received_to_assigned_multiple():
    order_proc_data = {
        'created': datetime.datetime(2022, 6, 9, 17, 55, 45),
        'order_info': {
            'statistics': {
                'status_updates': [
                    {'c': datetime.datetime(2022, 6, 9, 17, 55, 45), 'q': 'create', 's': 'pending'},
                    {'c': datetime.datetime(2022, 6, 9, 17, 55, 48), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 11), 'q': 'seen_timeout', 'i': 0},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 13), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 14), 'q': 'seen_received', 'i': 1},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 14), 'q': 'seen', 'i': 1},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 22), 'q': 'requestconfirm_assigned', 's': 'assigned',
                     'i': 1},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 22), 'q': 'requestconfirm_driving', 't': 'driving',
                     'i': 1},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 27), 'q': 'autoreorder', 'r': 'manual', 's': 'pending',
                     'i': 1},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 27), 'q': 'new_driver_found'},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 29), 'q': 'seen_received', 'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 29), 'q': 'seen', 'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 32), 'q': 'requestconfirm_assigned', 's': 'assigned',
                     'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 17, 56, 32), 'q': 'requestconfirm_driving', 't': 'driving',
                     'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 18, 2, 0), 'q': 'requestconfirm_waiting', 't': 'waiting',
                     'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 18, 2, 5), 'q': 'requestconfirm_transporting',
                     't': 'transporting', 'i': 2},
                    {'c': datetime.datetime(2022, 6, 9, 18, 14, 15), 'q': 'requestconfirm_complete', 's': 'finished',
                     't': 'complete', 'i': 2},
                ]
            }
        }
    }
    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update(
        {
            b'assigned_cnt': 2,
            b'cancelled_cnt': 0,
            b'created': datetime.datetime(2022, 6, 9, 17, 55, 45),
            b'driving_time': 338.0,
            b'dttm_utc_1_min': '2022-06-09 17:55:45',
            b'failed_cnt': 0,
            b'offer_timeout_cnt': 0,
            b'search_time': 37.0,
            b'seen_cnt': 2,
            b'seen_timeout_cnt': 1,
            b'transporting_time': 730.0,
            b'ts_1_min': 1654797345,
            b'reject_cnt': 0,
            b'reject_manual_cnt': 0,
            b'reject_autocancel_cnt': 0,
            b'reject_seenimpossible_cnt': 0,
            b'reject_missingtariffs_cnt': 0,
            b'reject_wrongway_cnt': 0,
            b'seen_received_to_assigned_time': [8.0, 3.0],
            b'waiting_time': 338.0,
        }
    )
    assert result == expected


def test_candidates_taximeter_version():
    order_proc_data = {
        'candidates': [
            {'taximeter_version': '10.24 (14710)'},
            {'taximeter_version': '10.25 (14711)'},
            {'taximeter_version': '10.26 (14712)'},
        ],
        'performer': {
            'candidate_index': 1
        }
    }

    result = dict(data_processor({})(order_proc_data))
    expected = copy.deepcopy(EMPTY_PARSED_DOCUMENT)
    expected.update(
        {
            b'cand_cnt': 3,
            b'cand_first_taximeter_version': '10.24 (14710)',
            b'cand_perf_taximeter_version': '10.25 (14711)',
            b'candidates_taximeter_version': [
                '10.24 (14710)', '10.25 (14711)', '10.26 (14712)'
            ],
            b'performer_candidate_index': 1,
        }
    )
    assert result == expected
