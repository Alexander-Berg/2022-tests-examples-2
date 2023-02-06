# encoding: utf-8

import pytest

from taxi.core import async
from taxi.external import experiments3
from taxi.internal import dbh
from taxi.internal.order_kit.plg import order_fsm
from taxi.internal.order_kit.plg import ordersync
from taxi.internal.order_kit.plg import status_handling


@pytest.fixture(autouse=True)
def mock_exp3_get_values(patch):
    @patch('taxi.external.experiments3.get_values')
    @async.inline_callbacks
    def mock_exp3_get_values(*args, **kwargs):
        yield
        result = [
            experiments3.ExperimentsValue(
                name='order_client_notification',
                value={'enabled': False}
            )
        ]

        async.return_value(result)


@pytest.fixture()
def mock_get_price(patch):
    class Context:
        request = None

    ctx = Context()

    @patch('taxi.external.cargo_orders.calc_price')
    @async.inline_callbacks
    def calc_price(calc_price_request, log_extra=None):
        ctx.request = calc_price_request
        yield async.return_value({
            'is_cargo_pricing': True,
            'receipt': {
                'total': 933.0,
                'total_distance': 3541.0878,
                'waiting': {'cost': 0.0, 'sum': 0.0, 'time': 60.0},
                'waiting_in_transit': {'cost': 20.0, 'sum': 10.0, 'time': 30.0},
            },
            'order_info': {
                'destination': {
                    'point': [37.642979, 55.734977],
                    'address': 'БЦ Аврора',
                },
                'source': {
                    'point': [37.642979, 55.734977],
                    'address': 'БЦ Аврора',
                },
            },
            'taxi_pricing_response': {
                'corp_decoupling': True,
                'fixed_price': True,
                'geoarea_ids': [
                    'g/2bab7eff1aa848b681370b2bd83cfbf9'
                ],
                'driver': {
                    'modifications': {
                        'for_fixed': [
                            549,
                            482,
                            843,
                            740,
                            647,
                            791,
                            913,
                            951,
                            892,
                            799,
                            889,
                            800,
                            891,
                            792
                        ],
                        'for_taximeter': [
                            549,
                            482,
                            843,
                            740,
                            647,
                            791,
                            913,
                            951,
                            892,
                            799,
                            889,
                            800,
                            891,
                            792
                        ]
                    },
                    'price': {
                        'total': 762.0
                    },
                    'meta': {
                        'waiting_in_destination_price': 0.0,
                        'waiting_in_transit_price': 0.0,
                        'paid_cancel_price': 699.0,
                        'req:cargo_type.lcv_l:price': 0.0,
                        'req:fake_middle_point_cargocorp_lcv_l.no_loaders_point:price': 63.0,
                        'req:cargo_type.lcv_l:count': 1.0,
                        'req:fake_middle_point_cargocorp_lcv_l.no_loaders_point:count': 1.0,
                        'waiting_price': 0.0,
                        'min_price': 699.0
                    },
                    'base_price': {
                        'boarding': 699.0,
                        'distance': 0.0,
                        'time': 0.0,
                        'waiting': 0.0,
                        'requirements': 0.0,
                        'transit_waiting': 0.0,
                        'destination_waiting': 0.0
                    },
                    'tariff_id': '5f806137efb9031bfad697db',
                    'category_id': 'a7ebb880cf8e4f73b2d8ce383cdaea75',
                    'category_prices_id': 'c/a7ebb880cf8e4f73b2d8ce383cdaea75',
                    'additional_prices': {},
                    'data': {
                        'country_code2': 'RU',
                        'zone': 'moscow',
                        'category': 'cargocorp',
                        'user_tags': [],
                        'surge_params': {
                            'value': 1.0,
                            'value_smooth': 1.0,
                            'value_raw': 1.0,
                            'antisurge': False
                        },
                        'requirements': {
                            'simple': [],
                            'select': {
                                'cargo_type': [
                                    {
                                        'name': 'lcv_l',
                                        'independent': True
                                    }
                                ],
                                'fake_middle_point_cargocorp_lcv_l': [
                                    {
                                        'name': 'no_loaders_point',
                                        'independent': True
                                    }
                                ]
                            }
                        },
                        'tariff': {
                            'boarding_price': 699.0,
                            'minimum_price': 0.0,
                            'waiting_price': {
                                'free_waiting_time': 1800,
                                'price_per_minute': 9.0
                            },
                            'requirement_prices': {
                                'cargo_type_int.lcv_m': 0.0,
                                'unloading': 9.0,
                                'cargo_type_int.van': 0.0,
                                'fake_middle_point_cargocorp_van': 0.0,
                                'fake_middle_point_cargocorp_lcv_m.one_loader_point': 192.0,
                                'fake_middle_point_cargocorp_lcv_m.no_loaders_point': 77.0,
                                'cargo_type_int': 0.0,
                                'fake_middle_point_cargocorp_lcv_m': 0.0,
                                'fake_middle_point_cargocorp_van.two_loaders_point': 700.0,
                                'fake_middle_point_cargocorp_van.no_loaders_point': 100.0,
                                'cargo_type_int.lcv_l': 0.0,
                                'cargo_loaders': 0.0,
                                'fake_middle_point_cargocorp_lcv_l': 0.0,
                                'fake_middle_point_cargocorp_van.one_loader_point': 250.0,
                                'fake_middle_point_cargocorp_lcv_m.two_loaders_point': 539.0,
                                'fake_middle_point_cargocorp_lcv_l.no_loaders_point': 63.0,
                                'fake_middle_point_cargocorp_lcv_l.one_loader_point': 156.0,
                                'fake_middle_point_cargocorp_lcv_l.two_loaders_point': 438.0
                            }
                        },
                        'user_data': {
                            'has_yaplus': False,
                            'has_cashback_plus': False
                        },
                        'category_data': {
                            'fixed_price': True,
                            'decoupling': False,
                            'corp_decoupling': True,
                            'paid_cancel_waiting_time_limit': 600.0,
                            'min_paid_supply_price_for_paid_cancel': 0.0
                        },
                        'payment_type': 'corp',
                        'experiments': [
                            'cashback_for_plus_availability'
                        ],
                        'temporary': {
                            'route_parts': [
                                {
                                    'part': {
                                        'geoarea': 'moscow',
                                        'entrance_distance': 0.0,
                                        'entrance_time': 0.0,
                                        'exit_distance': 0.0,
                                        'exit_time': 0.0
                                    },
                                    'price_distance': 0.0,
                                    'price_time': 0.0
                                }
                            ]
                        },
                        'rounding_factor': 1.0
                    },
                    'trip_information': {
                        'distance': 0.0,
                        'time': 0.0,
                        'jams': True,
                        'has_toll_roads': False
                    }
                },
                'user': {
                    'modifications': {
                        'for_fixed': [
                            929,
                            549,
                            482,
                            843,
                            740,
                            647,
                            791,
                            913,
                            952,
                            892,
                            799,
                            937,
                            936,
                            939,
                            938,
                            889,
                            800,
                            809,
                            845,
                            891,
                            924,
                            792
                        ],
                        'for_taximeter': [
                            929,
                            549,
                            482,
                            843,
                            740,
                            647,
                            791,
                            913,
                            952,
                            892,
                            799,
                            937,
                            936,
                            939,
                            938,
                            889,
                            800,
                            809,
                            891,
                            924,
                            792
                        ]
                    },
                    'price': {
                        'total': 902.0
                    },
                    'meta': {
                        'req:fake_middle_point_cargocorp_lcv_l.no_loaders_point:price': 63.0,
                        'waiting_in_destination_price': 0.0,
                        'waiting_in_transit_price': 0.0,
                        'min_price': 839.0,
                        'req:cargo_type.lcv_l:price': 0.0,
                        'paid_cancel_price': 839.0,
                        'req:cargo_type.lcv_l:count': 1.0,
                        'waiting_price': 0.0,
                        'req:fake_middle_point_cargocorp_lcv_l.no_loaders_point:count': 1.0
                    },
                    'base_price': {
                        'boarding': 838.8,
                        'distance': 0.0,
                        'time': 0.0,
                        'waiting': 0.0,
                        'requirements': 0.0,
                        'transit_waiting': 0.0,
                        'destination_waiting': 0.0
                    },
                    'tariff_id': '5f806137efb9031bfad697db-e765eb242bbf4c9fa9db2d50a6f850f5'
                    '-c4b66eeaed1444c6914f509e9bcad677',
                    'category_id': 'a7ebb880cf8e4f73b2d8ce383cdaea75',
                    'category_prices_id':
                        'd/5f806137efb9031bfad697db-e765eb242bbf4c9fa9db2d50a6f850f5-'
                        'c4b66eeaed1444c6914f509e9bcad677/a7ebb880cf8e4f73b2d8ce383cdaea75',
                    'additional_prices': {},
                    'data': {
                        'country_code2': 'RU',
                        'zone': 'moscow',
                        'category': 'cargocorp',
                        'user_tags': [],
                        'surge_params': {
                            'value': 1.0,
                            'value_smooth': 1.0,
                            'value_raw': 1.0,
                            'antisurge': False
                        },
                        'requirements': {
                            'simple': [],
                            'select': {
                                'cargo_type': [
                                    {
                                        'name': 'lcv_l',
                                        'independent': True
                                    }
                                ],
                                'fake_middle_point_cargocorp_lcv_l': [
                                    {
                                        'name': 'no_loaders_point',
                                        'independent': True
                                    }
                                ]
                            }
                        },
                        'tariff': {
                            'boarding_price': 838.8,
                            'minimum_price': 838.8,
                            'waiting_price': {
                                'free_waiting_time': 1800,
                                'price_per_minute': 10.8
                            },
                            'requirement_prices': {
                                'cargo_type_int.lcv_m': 0.0,
                                'unloading': 9.0,
                                'cargo_type_int.van': 0.0,
                                'fake_middle_point_cargocorp_van': 0.0,
                                'fake_middle_point_cargocorp_lcv_m.one_loader_point': 192.0,
                                'fake_middle_point_cargocorp_lcv_m.no_loaders_point': 77.0,
                                'cargo_type_int': 0.0,
                                'fake_middle_point_cargocorp_lcv_m': 0.0,
                                'fake_middle_point_cargocorp_van.two_loaders_point': 700.0,
                                'fake_middle_point_cargocorp_van.no_loaders_point': 100.0,
                                'cargo_type_int.lcv_l': 0.0,
                                'cargo_loaders': 0.0,
                                'fake_middle_point_cargocorp_lcv_l': 0.0,
                                'fake_middle_point_cargocorp_van.one_loader_point': 250.0,
                                'fake_middle_point_cargocorp_lcv_m.two_loaders_point': 539.0,
                                'fake_middle_point_cargocorp_lcv_l.no_loaders_point': 63.0,
                                'fake_middle_point_cargocorp_lcv_l.one_loader_point': 156.0,
                                'fake_middle_point_cargocorp_lcv_l.two_loaders_point': 438.0
                            }
                        },
                        'user_data': {
                            'has_yaplus': False,
                            'has_cashback_plus': False
                        },
                        'category_data': {
                            'fixed_price': True,
                            'decoupling': True,
                            'disable_surge': False,
                            'disable_paid_supply': True,
                            'corp_decoupling': True,
                            'paid_cancel_waiting_time_limit': 600.0,
                            'min_paid_supply_price_for_paid_cancel': 0.0
                        },
                        'payment_type': 'corp',
                        'experiments': [
                            'cashback_for_plus_availability'
                        ],
                        'temporary': {
                            'route_parts': [
                                {
                                    'part': {
                                        'geoarea': 'moscow',
                                        'entrance_distance': 0.0,
                                        'entrance_time': 0.0,
                                        'exit_distance': 0.0,
                                        'exit_time': 0.0
                                    },
                                    'price_distance': 0.0,
                                    'price_time': 0.0
                                }
                            ]
                        },
                        'rounding_factor': 1.0
                    },
                    'trip_information': {
                        'distance': 0.0,
                        'time': 0.0,
                        'jams': True,
                        'has_toll_roads': False
                    }
                },
                'taximeter_metadata': {
                    'show_price_in_taximeter': False,
                    'max_distance_from_point_b': 501
                },
                'currency': {
                    'name': 'RUB',
                    'symbol': '₽',
                    'fraction_digits': 0
                },
                'tariff_info': {
                    'time': {
                        'included_minutes': 0,
                        'price_per_minute': 0.0
                    },
                    'distance': {
                        'included_kilometers': 0,
                        'price_per_kilometer': 27.6
                    },
                    'point_a_free_waiting_time': 1800,
                    'point_b_free_waiting_time': 60,
                    'max_free_waiting_time': 600
                }
            }
        })

    return ctx


@pytest.mark.filldb(order_proc='cargo_pricing')
@pytest.mark.config(
    CARGO_ORDERS_CALC_PRICE_ON_SERVER=True,
    CARGO_ORDERS_CALC_PRICE_FROM_PY2_ENABLED=['presetcar', 'finish'],
    CORP_SOURCES_NO_USER=['cargo'],
)
@pytest.inline_callbacks
def test_handle_preupdate_proc_cargo_fixprice(mock_get_price):

    proc_orig = yield dbh.order_proc.Doc.find_one_by_id(
        '8fa174f64a0b4d8488395bc9f652addd'
    )
    state = order_fsm.OrderFsm(proc_orig)

    state.proc.preupdated_proc_data.presetcar_performer_index = -1

    yield status_handling._handle_preupdate_proc_cargo_fixprice(state)
    proc = state.proc

    assert mock_get_price.request.tariff_class == 'lavka'
    assert mock_get_price.request.driver_id == 'd1975425eed4801c6767e4f8b775edb8'
    assert mock_get_price.request.transport_type == 'electric_bicycle'
    assert mock_get_price.request.park_db_id == '1fa4756764a0b4d8498095fc9fs5gaddd'

    assert not proc.order.fixed_price_discard_reason

    fixed_price = proc.order.fixed_price
    assert fixed_price.destination == [37.642979, 55.734977]
    assert fixed_price.price == 933.0
    assert fixed_price.driver_price == 933.0
    assert not fixed_price.show_price_in_taximeter
    assert fixed_price.max_distance_from_b == 501
    assert fixed_price.paid_supply_price is None

    req = proc.order.request
    assert req.surge_price == 1
    assert req.surcharge is None
    assert req.surcharge_alpha is None
    assert req.surcharge_beta is None

    preupd = proc.preupdated_proc_data
    assert preupd.presetcar_fixed_price == {
        'order.fixed_price.destination': [37.642979, 55.734977],
        'order.fixed_price.driver_price': 933.0,
        'order.fixed_price.max_distance_from_b': 501,
        'order.fixed_price.paid_supply_price': None,
        'order.fixed_price.price': 933.0,
        'order.fixed_price.price_original': 933.0,
        'order.fixed_price.show_price_in_taximeter': False
    }
    assert preupd.presetcar_surge == {
        'order.request.sp': 1.0,
        'order.request.sp_alpha': None,
        'order.request.sp_beta': None,
        'order.request.sp_surcharge': None
    }
    assert preupd.presetcar_decoupling == {
        'order.decoupling.driver_price_info.category_id': 'a7ebb880cf8e4f73b2d8ce383cdaea75',
        'order.decoupling.driver_price_info.fixed_price': 762.0,
        'order.decoupling.driver_price_info.sp': 1.0,
        'order.decoupling.driver_price_info.sp_alpha': None,
        'order.decoupling.driver_price_info.sp_beta': None,
        'order.decoupling.driver_price_info.sp_surcharge': None,
        'order.decoupling.driver_price_info.tariff_id': '5f806137efb9031bfad697db',
        'order.decoupling.user_price_info.category_id': 'a7ebb880cf8e4f73b2d8ce383cdaea75',
        'order.decoupling.user_price_info.fixed_price': 902.0,
        'order.decoupling.user_price_info.sp': 1.0,
        'order.decoupling.user_price_info.sp_alpha': None,
        'order.decoupling.user_price_info.sp_beta': None,
        'order.decoupling.user_price_info.sp_surcharge': None,
        'order.decoupling.user_price_info.tariff_id':
            '5f806137efb9031bfad697db-e765eb242bbf4c9fa9db2d50a6f850f5-c4b66eeaed1444c6914f509e9bcad677'
    }
    assert preupd.presetcar_unset_fixed_price_discard_reason == {
        'order.fixed_price_discard_reason': True,
    }


@pytest.mark.filldb(
    order_proc='cargo_pricing',
    orders='cargo_pricing',
)
@pytest.mark.config(
    CARGO_ORDERS_CALC_PRICE_ON_SERVER=True,
    CARGO_ORDERS_CALC_PRICE_FROM_PROCESSING_PY2=['finished'],
    DISPATCH_CLASSES_ORDER=['express', 'econom', 'lavka'],
    CARGO_ORDERS_CALC_PRICE_FROM_PY2_ENABLED=['presetcar', 'finish'],
    CORP_SOURCES_NO_USER=['cargo'],
)
@pytest.inline_callbacks
def test_handle_preupdate_finish_proc_cargo_fixprice(
        patch,
        mock_get_price,
        corp_clients_get_client_by_client_id_mock):
    @patch('taxi.internal.city_manager.get_doc')
    @async.inline_callbacks
    def _get_city_doc(city_id):
        yield
        city = dbh.cities.Doc({'_id': city_id, 'country': 'rus'})
        async.return_value(city)

    @patch('taxi.internal.city_kit.country_manager._get_countries_dict_fresh')
    @async.inline_callbacks
    def get_countries(*args, **kwargs):
        yield
        async.return_value({'rus': {
            '_id': 'rus',
            'phone_code': '7',
            'national_access_code': '8',
            'phone_max_length': 11,
            'phone_min_length': 11,
        }})

    order_id = '8fa174f64a0b4d8488395bc9f652addd'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.status = 'finished'

    yield ordersync.sync_and_handle_order(
        proc, 0, log_extra=None
    )

    assert mock_get_price.request.tariff_class == 'lavka'
    assert mock_get_price.request.driver_id == 'd1975425eed4801c6767e4f8b775edb8'

    new_order = yield dbh.orders.Doc.find_one_by_id(
        order_id
    )
    new_proc = yield dbh.order_proc.Doc.find_one_by_id(
        order_id
    )

    cost = 933
    payment = new_order['payment_tech']
    assert new_order['cost'] == cost
    assert payment['user_to_pay']['ride'] == cost * 10000
    assert payment['without_vat_to_pay']['ride'] == cost * 10000

    assert new_proc['order']['cost'] == cost
    assert new_proc['order']['decoupling']['user_price_info']['cost'] == cost
    assert new_proc['order']['decoupling']['driver_price_info']['cost'] == cost


@pytest.mark.filldb(
    order_proc='cargo_pricing',
    orders='cargo_pricing',
)
@pytest.mark.config(
    CARGO_ORDERS_CALC_PRICE_ON_SERVER=True,
    CARGO_ORDERS_CALC_PRICE_FROM_PROCESSING_PY2=['cancelled'],
    CARGO_ORDERS_CALC_PRICE_FROM_PY2_ENABLED=['presetcar', 'finish'],
)
@pytest.inline_callbacks
def test_finish_proc_cargo_fixprice_no_performer(patch, mock_get_price):
    @patch('taxi.internal.city_manager.get_doc')
    @async.inline_callbacks
    def _get_city_doc(city_id):
        yield
        city = dbh.cities.Doc({'_id': city_id, 'country': 'rus'})
        async.return_value(city)

    @patch('taxi.internal.city_kit.country_manager._get_countries_dict_fresh')
    @async.inline_callbacks
    def get_countries(*args, **kwargs):
        yield
        async.return_value({'rus': {
            '_id': 'rus',
            'phone_code': '7',
            'national_access_code': '8',
            'phone_max_length': 11,
            'phone_min_length': 11,
        }})

    order_id = '8fa174f64a0b4d8488395bc9f652addd'
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    proc.order.status = 'cancelled'
    proc.preupdated_proc_data.presetcar_performer_index = None
    proc.order_info.statistics.status_updates = []
    proc.candidates = []
    state = order_fsm.OrderFsm(proc)

    yield status_handling._handle_finish_preupdate_proc_cargo_fixprice(state)

    assert state.proc.order['cost'] == 933

    assert mock_get_price.request.tariff_class == 'econom'
    assert mock_get_price.request.driver_id is None
