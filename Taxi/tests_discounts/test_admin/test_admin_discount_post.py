import http
import json

import pytest

from tests_discounts.test_admin import admin_test_utils


DISCOUNTS_PARAMETRIZE_VALUES = [
    pytest.param(
        None,
        None,
        None,
        admin_test_utils.DEFAULT_DB_STATE,
        id='check default db state',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120e1',
                'discount_class': 'valid_class',
                'description': 'testsuite_discount',
                'enabled': False,
                'discount_method': 'full',
                'calculation_params': {
                    'round_digits': 3,
                    'calculation_method': 'calculation_table',
                    'discount_calculator': {
                        'table': [{'cost': 100.0, 'discount': 0.2}],
                    },
                },
                'select_params': {
                    'classes': ['econom'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-01-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [1],
            },
        },
        None,
        400,
        admin_test_utils.DEFAULT_DB_STATE,
        id='check duplicate discount creation',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120e1',
                'discount_class': 'valid_class',
                'reference_entity_id': 1,
                'description': 'testsuite_discount',
                'enabled': True,
                'discount_method': 'subvention-fix',
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business', 'econom'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                    'ride_properties': ['valid_property1', 'valid_property2'],
                },
                'zones_list': [1],
            },
        },
        None,
        200,
        admin_test_utils.patch_db_state(
            admin_test_utils.DEFAULT_DB_STATE,
            update_patch={
                'user_discounts': [
                    {
                        'id': 1,
                        'discount_series_id': '0120e1',
                        'reference_entity_id': 2,
                    },
                ],
                'discounts_lists': [
                    {
                        'id': 1,
                        'zonal_list_id': 1,
                        'reference_entity_id': 2,
                        'prev_item': None,
                        'next_item': None,
                    },
                ],
            },
            append_patch={
                'discounts_entities': [
                    {
                        'reference_entity_id': 2,
                        'draft_id': admin_test_utils.DRAFT_ID,
                        'discount_class': 'valid_class',
                        'description': 'testsuite_discount',
                        'enabled': True,
                        'discount_method': 'subvention-fix',
                        'calculation_params': {
                            'round_digits': 4,
                            'calculation_method': 'calculation_formula',
                            'discount_calculator': {
                                'calculation_formula_v1_a1': 1.0,
                                'calculation_formula_v1_a2': 2.0,
                                'calculation_formula_v1_p1': 3.0,
                                'calculation_formula_v1_p2': 4.0,
                                'calculation_formula_v1_c1': 5.0,
                                'calculation_formula_v1_c2': 6.0,
                                'calculation_formula_v1_threshold': 100.0,
                            },
                        },
                        'select_params': {
                            'classes': ['business', 'econom'],
                            'discount_target': 'all',
                            'datetime_params': {
                                'date_from': '2100-02-01T00:00:00',
                                'timezone_type': 'utc',
                            },
                            'ride_properties': [
                                'valid_property1',
                                'valid_property2',
                            ],
                        },
                        'driver_less_coeff': None,
                        'discount_meta_info': {},
                        'prev_entity': 1,
                        'update_meta_info': {
                            'tickets': ['ticket-1'],
                            'user_login': 'user',
                            'date': '2019-12-04T12:34:56',
                        },
                    },
                ],
            },
        ),
        id='check update discount',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120e1',
                'discount_class': 'invalid_class',
                'reference_entity_id': 1,
                'description': 'testsuite_discount',
                'enabled': True,
                'discount_method': 'subvention-fix',
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business', 'econom'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [1],
            },
        },
        None,
        400,
        admin_test_utils.DEFAULT_DB_STATE,
        id='invalid discount class',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120e1',
                'reference_entity_id': 1,
                'description': 'testsuite_discount',
                'enabled': True,
                'discount_method': 'subvention-fix',
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business', 'econom'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                    'ride_properties': ['invalid_property'],
                },
                'zones_list': [1],
            },
        },
        None,
        400,
        admin_test_utils.DEFAULT_DB_STATE,
        id='invalid discount ride property',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120e1',
                'reference_entity_id': 1,
                'description': 'testsuite_discount',
                'discount_class': 'valid_class',
                'enabled': True,
                'discount_method': 'subvention-fix',
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 101.0,
                        'calculation_formula_v1_p2': 50.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business', 'econom'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [1],
            },
        },
        None,
        400,
        admin_test_utils.DEFAULT_DB_STATE,
        id='invalid calculation discount value',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120ab',
                'discount_class': 'valid_class',
                'description': 'testsuite_discount1',
                'enabled': True,
                'discount_method': 'full',
                'driver_less_coeff': 0.7,
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [2],
            },
        },
        None,
        400,
        admin_test_utils.DEFAULT_DB_STATE,
        id='create second discount in missing zone',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120ab',
                'discount_class': 'valid_class',
                'description': 'testsuite_discount1',
                'enabled': True,
                'discount_method': 'full',
                'driver_less_coeff': 0.7,
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['business'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [2],
            },
        },
        [
            """
            INSERT INTO
            discounts.zonal_lists(zone_name,enabled,zone_type)
            VALUES ('testsuite_zone_1',true,'tariff_zone') """,
        ],
        200,
        admin_test_utils.patch_db_state(
            admin_test_utils.DEFAULT_DB_STATE,
            append_patch={
                'zonal_lists': [
                    {
                        'zonal_list_id': 2,
                        'zone_name': 'testsuite_zone_1',
                        'enabled': True,
                        'zone_type': 'tariff_zone',
                    },
                ],
                'user_discounts': [
                    {
                        'id': 2,
                        'discount_series_id': '0120ab',
                        'reference_entity_id': 2,
                    },
                ],
                'discounts_lists': [
                    {
                        'id': 2,
                        'zonal_list_id': 2,
                        'reference_entity_id': 2,
                        'prev_item': None,
                        'next_item': None,
                    },
                ],
                'discounts_entities': [
                    {
                        'reference_entity_id': 2,
                        'draft_id': admin_test_utils.DRAFT_ID,
                        'discount_class': 'valid_class',
                        'description': 'testsuite_discount1',
                        'enabled': True,
                        'discount_method': 'full',
                        'driver_less_coeff': 0.7,
                        'calculation_params': {
                            'round_digits': 4,
                            'calculation_method': 'calculation_formula',
                            'discount_calculator': {
                                'calculation_formula_v1_a1': 1.0,
                                'calculation_formula_v1_a2': 2.0,
                                'calculation_formula_v1_p1': 3.0,
                                'calculation_formula_v1_p2': 4.0,
                                'calculation_formula_v1_c1': 5.0,
                                'calculation_formula_v1_c2': 6.0,
                                'calculation_formula_v1_threshold': 100.0,
                            },
                        },
                        'select_params': {
                            'classes': ['business'],
                            'discount_target': 'all',
                            'datetime_params': {
                                'date_from': '2100-02-01T00:00:00',
                                'timezone_type': 'utc',
                            },
                        },
                        'discount_meta_info': {},
                        'prev_entity': None,
                        'update_meta_info': {
                            'tickets': ['ticket-1'],
                            'user_login': 'user',
                            'date': '2019-12-04T12:34:56',
                        },
                    },
                ],
            },
        ),
        id='create second discount in second zone',
    ),
    pytest.param(
        {
            'discount': {
                'discount_series_id': '0120abcd',
                'discount_class': 'valid_class',
                'description': 'testsuite_discountN',
                'enabled': True,
                'discount_method': 'full',
                'driver_less_coeff': 0.7,
                'calculation_params': {
                    'round_digits': 4,
                    'calculation_method': 'calculation_formula',
                    'discount_calculator': {
                        'calculation_formula_v1_a1': 1.0,
                        'calculation_formula_v1_a2': 2.0,
                        'calculation_formula_v1_p1': 3.0,
                        'calculation_formula_v1_p2': 4.0,
                        'calculation_formula_v1_c1': 5.0,
                        'calculation_formula_v1_c2': 6.0,
                        'calculation_formula_v1_threshold': 100.0,
                    },
                },
                'select_params': {
                    'classes': ['comfortplus'],
                    'discount_target': 'all',
                    'datetime_params': {
                        'date_from': '2100-02-01T00:00:00',
                        'timezone_type': 'utc',
                    },
                },
                'zones_list': [1],
            },
        },
        None,
        200,
        admin_test_utils.patch_db_state(
            admin_test_utils.DEFAULT_DB_STATE,
            update_patch={
                'discounts_lists': [
                    {
                        'id': 1,
                        'zonal_list_id': 1,
                        'reference_entity_id': 1,
                        'prev_item': 2,
                        'next_item': None,
                    },
                ],
            },
            append_patch={
                'user_discounts': [
                    {
                        'id': 2,
                        'discount_series_id': '0120abcd',
                        'reference_entity_id': 2,
                    },
                ],
                'discounts_lists': [
                    {
                        'id': 2,
                        'zonal_list_id': 1,
                        'reference_entity_id': 2,
                        'prev_item': None,
                        'next_item': 1,
                    },
                ],
                'discounts_entities': [
                    {
                        'reference_entity_id': 2,
                        'draft_id': admin_test_utils.DRAFT_ID,
                        'discount_class': 'valid_class',
                        'description': 'testsuite_discountN',
                        'enabled': True,
                        'discount_method': 'full',
                        'driver_less_coeff': 0.7,
                        'calculation_params': {
                            'round_digits': 4,
                            'calculation_method': 'calculation_formula',
                            'discount_calculator': {
                                'calculation_formula_v1_a1': 1.0,
                                'calculation_formula_v1_a2': 2.0,
                                'calculation_formula_v1_p1': 3.0,
                                'calculation_formula_v1_p2': 4.0,
                                'calculation_formula_v1_c1': 5.0,
                                'calculation_formula_v1_c2': 6.0,
                                'calculation_formula_v1_threshold': 100.0,
                            },
                        },
                        'select_params': {
                            'classes': ['comfortplus'],
                            'discount_target': 'all',
                            'datetime_params': {
                                'date_from': '2100-02-01T00:00:00',
                                'timezone_type': 'utc',
                            },
                        },
                        'discount_meta_info': {},
                        'prev_entity': None,
                        'update_meta_info': {
                            'tickets': ['ticket-1'],
                            'user_login': 'user',
                            'date': '2019-12-04T12:34:56',
                        },
                    },
                ],
            },
        ),
        id='add discount to zone with discount',
    ),
]


@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES ('testsuite_zone',true,'tariff_zone') """,
    ],
)
@pytest.mark.parametrize(
    'discount_target,extra_select_params,expected_status',
    (
        ('newbie', {}, http.HTTPStatus.OK),
        ('tag_service', {}, http.HTTPStatus.BAD_REQUEST),
        ('tag_service', {'user_tags': []}, http.HTTPStatus.BAD_REQUEST),
        ('tag_service', {'user_tags': ['10']}, http.HTTPStatus.OK),
        ('selected', {}, http.HTTPStatus.BAD_REQUEST),
        ('selected', {'selected_user_tags': []}, http.HTTPStatus.OK),
        ('selected', {'selected_user_tags': ['10']}, http.HTTPStatus.OK),
    ),
)
@pytest.mark.config(DISCOUNTS_CLASSES=['valid_class'])
async def test_create_discount(
        taxi_discounts,
        pgsql,
        discount_target,
        extra_select_params,
        expected_status,
):
    create_discount_requiest = {
        'discount': {
            'discount_series_id': '0120e1',
            'discount_class': 'valid_class',
            'description': 'testsuite_discount',
            'enabled': False,
            'discount_method': 'full',
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'select_params': {
                'classes': ['econom'],
                'discount_target': discount_target,
                'datetime_params': {
                    'date_from': '2100-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
            },
            'zones_list': [1],
        },
    }
    create_discount_requiest['discount']['select_params'].update(
        extra_select_params,
    )
    await admin_test_utils.create_discount(
        create_discount_requiest,
        taxi_discounts,
        pgsql,
        expected_status,
        admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )


@pytest.mark.pgsql('discounts', queries=admin_test_utils.DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'discount_request,db_patch,expected_code,expected_db_state',
    DISCOUNTS_PARAMETRIZE_VALUES,
)
@pytest.mark.config(
    DISCOUNTS_CLASSES=['valid_class'],
    DISCOUNTS_RIDE_PROPERTIES=[
        'valid_property1',
        'valid_property2',
        'valid_property3',
        'valid_property4',
    ],
)
async def test_v1_admin_discounts_post(
        taxi_discounts,
        discount_request,
        db_patch,
        expected_code,
        expected_db_state,
        pgsql,
):
    if db_patch:
        admin_test_utils.patch_db(pgsql, db_patch)

    if discount_request:
        await admin_test_utils.create_discount(
            discount_request,
            taxi_discounts,
            pgsql,
            expected_code,
            admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
        )

    db_discounts = admin_test_utils.DBState(pgsql)
    admin_test_utils.assert_sorted(
        db_discounts.zonal_lists,
        expected_db_state['zonal_lists'],
        'zonal_list_id',
    )
    admin_test_utils.assert_sorted(
        db_discounts.user_discounts, expected_db_state['user_discounts'], 'id',
    )
    admin_test_utils.assert_sorted(
        db_discounts.discounts_lists,
        expected_db_state['discounts_lists'],
        'id',
    )

    admin_test_utils.assert_sorted_ignore_date(
        db_discounts.discounts_entities,
        expected_db_state['discounts_entities'],
        'reference_entity_id',
    )


@pytest.mark.pgsql('discounts', queries=admin_test_utils.DEFAULT_QUERIES)
@pytest.mark.parametrize(
    'discount_request,db_patch,expected_code,expected_db_state',
    DISCOUNTS_PARAMETRIZE_VALUES,
)
@pytest.mark.config(
    DISCOUNTS_CLASSES=['valid_class'],
    DISCOUNTS_RIDE_PROPERTIES=[
        'valid_property1',
        'valid_property2',
        'valid_property3',
        'valid_property4',
    ],
)
async def test_v1_admin_discounts_check(
        taxi_discounts,
        discount_request,
        db_patch,
        expected_code,
        expected_db_state,
        pgsql,
):
    if db_patch:
        admin_test_utils.patch_db(pgsql, db_patch)

    if discount_request:
        check_response = await taxi_discounts.post(
            'v1/admin/discounts/check',
            data=json.dumps(discount_request),
            headers=admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
        )
        check_response_json = check_response.json()
        assert check_response.status_code == expected_code, check_response_json
        if expected_code == 200:
            assert 'data' in check_response_json
            assert 'diff' in check_response_json
            assert (
                check_response_json['diff']['new']
                == discount_request['discount']
            )
            assert check_response_json['data'] == discount_request


@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES ('testsuite_zone',true,'tariff_zone') """,
    ],
)
async def test_create_old_discount_utc(taxi_discounts, pgsql):
    create_discount_requiest = {
        'discount': {
            'discount_series_id': '0120e1',
            'description': 'testsuite_discount',
            'enabled': False,
            'discount_method': 'full',
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'select_params': {
                'classes': ['econom'],
                'discount_target': 'all',
                'datetime_params': {
                    'date_from': '2019-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
            },
            'zones_list': [1],
        },
    }
    await admin_test_utils.create_discount(
        create_discount_requiest,
        taxi_discounts,
        pgsql,
        400,
        admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )


@pytest.mark.config(DISCOUNTS_CLASSES=['valid_class'])
@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES ('testsuite_zone',true,'tariff_zone'),
               ('moscow',true,'tariff_zone')""",
    ],
)
@pytest.mark.now('2021-03-03T16:00:00Z')
async def test_create_discount_with_limit(taxi_discounts, pgsql, mockserver):
    @mockserver.json_handler('/billing-limits/v1/create')
    def _mock_limits(request):
        return {
            'approvers': ['me', 'you'],
            'currency': 'RUB',
            'label': 'msk',
            'ref': 'limit_id',
            'tags': [],
            'account_id': 'account_id',
            'tickets': ['TAXIRATE-1'],
            'windows': [
                {
                    'label': '7-дневный',
                    'size': 604800,
                    'threshold': 100,
                    'type': 'sliding',
                    'value': '1000.0000',
                },
                {
                    'label': 'Дневной',
                    'size': 86400,
                    'threshold': 200,
                    'tumbling_start': '2019-10-31T21:00:00.000000+00:00',
                    'type': 'tumbling',
                    'value': '200.0000',
                },
            ],
        }

    create_discount_request = {
        'discount': {
            'discount_series_id': '0120e1',
            'discount_class': 'valid_class',
            'description': 'testsuite_discount',
            'enabled': False,
            'discount_method': 'full',
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'select_params': {
                'classes': ['econom'],
                'discount_target': 'all',
                'datetime_params': {
                    'date_from': '2025-03-03T15:00:00',
                    'timezone_type': 'local',
                },
            },
            'zones_list': [1, 2],
        },
        'limits': {
            'daily_limit': {'value': '100', 'threshold': 100},
            'weekly_limit': {
                'value': '1000',
                'threshold': 100,
                'check_current_week': True,
            },
        },
    }

    await admin_test_utils.create_discount(
        create_discount_request,
        taxi_discounts,
        pgsql,
        200,
        admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )


@pytest.mark.pgsql(
    'discounts',
    queries=[
        """
        INSERT INTO discounts.zonal_lists(zone_name,enabled,zone_type)
        VALUES ('testsuite_zone',true,'tariff_zone') """,
    ],
)
@pytest.mark.now('2019-03-08T00:00:00Z')
@pytest.mark.config(
    DISCOUNTS_CHECK_TAGS_TOPIC=True,
    DISCOUNTS_EXTERNAL_CLIENTS_ENABLED={
        '__default__': False,
        'passenger-tags': True,
    },
)
async def test_create_discount_tags_check(taxi_discounts, pgsql, mockserver):
    @mockserver.json_handler('/passenger-tags/v1/topics/items')
    def _mock_tags(request):
        return {'items': [], 'limit': 1, 'offset': 0}

    create_discount_requiest = {
        'discount': {
            'discount_series_id': '0120e1',
            'description': 'testsuite_discount',
            'enabled': False,
            'discount_method': 'full',
            'calculation_params': {
                'round_digits': 3,
                'calculation_method': 'calculation_table',
                'discount_calculator': {
                    'table': [{'cost': 100.0, 'discount': 0.2}],
                },
            },
            'select_params': {
                'classes': ['econom'],
                'discount_target': 'all',
                'datetime_params': {
                    'date_from': '2025-01-01T00:00:00',
                    'timezone_type': 'utc',
                },
                'user_tags': ['non_existent_tag'],
            },
            'zones_list': [1],
        },
    }
    await admin_test_utils.create_discount(
        create_discount_requiest,
        taxi_discounts,
        pgsql,
        400,
        admin_test_utils.DEFAULT_DISCOUNTS_HEADERS,
    )
