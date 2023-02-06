import pytest

from . import conftest


DEFAULT_EXPECTED_RESULT = (
    '\ufeffexplicit_d2d_tanker_key\ttariff_unloading_price\t'
    'tariff_linear_overweight_price\tuuid_id\r\n'
    '150.0\t9.0\t15.0\te238265a8cdd4179b9505861c8719946\r\n'
    '\t\t\te850d77875b94abd995e9ea20da56a32\r\n'
    '150.0\t9.0\t15.0\t1234\r\n'
)

DEFAULT_FIELD_NAMES = [
    'tariff_d2d_price',
    'tariff_unloading_price',
    'tariff_linear_overweight_price',
    'uuid_id',
]


@pytest.fixture(name='exp_report_settings')
async def _exp_report_settings(lazy_exp_report_settings):
    await lazy_exp_report_settings(field_names=DEFAULT_FIELD_NAMES)


def _tariff_requirements_extractor_config():
    return {
        'macro_transformations': [
            {
                'name': 'double_to_string_comma',
                'transformations': [
                    {'kind': 'to_string'},
                    {'kind': 'replace_in_string', 'old': ',', 'new': '.'},
                ],
            },
            {
                'name': 'extractor_tariff_requirement_price_string',
                'transformations': [
                    {'kind': 'field_by_name', 'field_name': 'max_price'},
                    {'kind': 'double_to_string_comma'},
                ],
            },
        ],
        'macro_sources': [
            {
                'name': 'tariff_requirements',
                'source': 'category_doc',
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'summable_requirements',
                    },
                ],
            },
        ],
        'extractors': {
            'tariff_unloading_price': {
                'source': 'tariff_requirements',
                'transformations': [
                    {
                        'kind': 'find_elem_by_field_value',
                        'field_name': 'type',
                        'field_value': 'unloading',
                    },
                    {'kind': 'extractor_tariff_requirement_price_string'},
                ],
            },
            'tariff_d2d_price': {
                'tanker_key': 'explicit_d2d_tanker_key',
                'source': 'tariff_requirements',
                'transformations': [
                    {
                        'kind': 'find_elem_by_field_value',
                        'field_name': 'type',
                        'field_value': 'door_to_door',
                    },
                    {'kind': 'extractor_tariff_requirement_price_string'},
                ],
            },
            'tariff_linear_overweight_price': {
                'source': 'tariff_requirements',
                'transformations': [
                    {
                        'kind': 'find_elem_by_field_value',
                        'field_name': 'type',
                        'field_value': 'linear_overweight',
                    },
                    {'kind': 'extractor_tariff_requirement_price_string'},
                ],
            },
        },
    }


@pytest.fixture(name='cfg_v2_report_extractors')
async def _cfg_v2_report_extractors(lazy_cfg_v2_report_extractors):
    await lazy_cfg_v2_report_extractors(
        json=_tariff_requirements_extractor_config(),
    )


@pytest.mark.servicetest
async def test_v1_report_v2_bad(
        call_v1_report_v2,
        yt_apply,
        yt_client,
        mock_v1_clients,
        exp_report_settings,
        cfg_v2_report_extractors,
):
    response = await call_v1_report_v2(
        json={'since_date': '2020-10-01'}, corp_client_id='123',
    )
    assert response.status == 400  # wrong X-B2B-Client-Id length

    response = await call_v1_report_v2(json={'since_date': '2020-10-01'})
    assert response.status == 404  # no report table data for CORP_CLIENT_ID


@pytest.mark.servicetest
@pytest.mark.config(CARGO_REPORTS_USING_COUNTRY_FROM_BODY_ENABLED=False)
async def test_v1_report_v2(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        exp_report_settings,
        cfg_v2_report_extractors,
):
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert result == DEFAULT_EXPECTED_RESULT


@pytest.mark.servicetest
@pytest.mark.translations(
    cargo={
        'report.head.uuid_id': {'ru': 'Недекларированный экстрактор'},
        'report.head.tariff_unloading_price': {
            'ru': 'Декларированный экстрактор',
        },
        'report.head.explicit_d2d_tanker_key': {
            'ru': 'Декларированный экстрактор с явным ключем',
        },
    },
)
async def test_v1_report_v2_head_translate(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        exp_report_settings,
        cfg_v2_report_extractors,
):
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result)[0] == [
        'Декларированный экстрактор с явным ключем',
        'Декларированный экстрактор',
        'tariff_linear_overweight_price',
        'Недекларированный экстрактор',
    ]


@pytest.mark.servicetest
@pytest.mark.config(
    CARGO_REPORTS_REPORT_V2_RAW_DATA_OVERRIDE={
        'override_paths': {
            'tables_path': (
                '//home/unittests/unittests/services/cargo-reports/custom/'
            ),
            'raw_report_table_name': 'raw_report_custom',
            'raw_tariffs_table_name': 'raw_tariffs_cuctom',
        },
    },
)
async def test_v1_report_v2_override_paths(
        call_v1_report_v2,
        create_raw_table_with_names,
        mock_v1_clients,
        write_yt_tables_data,
        exp_report_settings,
        cfg_v2_report_extractors,
):
    custom_path = '//home/unittests/unittests/services/cargo-reports/custom/'
    custom_raw_report_table = custom_path + 'raw_report_custom'
    custom_raw_tariffs_table = custom_path + 'raw_tariffs_cuctom'
    create_raw_table_with_names(
        raw_report_table_name=custom_raw_report_table,
        raw_tariffs_table_name=custom_raw_tariffs_table,
    )
    write_yt_tables_data(
        raw_report_table_path=custom_raw_report_table,
        raw_tariffs_table_path=custom_raw_tariffs_table,
    )
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert result == DEFAULT_EXPECTED_RESULT


@pytest.mark.servicetest
@pytest.mark.config(CARGO_REPORTS_USING_COUNTRY_FROM_BODY_ENABLED=True)
async def test_v1_report_v2_country_in_request(
        call_v1_report_v2,
        create_yt_tables_with_data,
        cfg_v2_report_extractors,
        lazy_exp_report_settings,
):
    await lazy_exp_report_settings(
        field_names=DEFAULT_FIELD_NAMES, country='custom_country',
    )
    response = await call_v1_report_v2(
        json={
            'since_date': '2020-10-01',
            'till_date': '2020-12-01',
            'client_country': 'custom_country',
        },
    )
    assert response.status == 200
    result = await response.text()
    assert result == DEFAULT_EXPECTED_RESULT


@pytest.mark.servicetest
async def test_v1_report_v2_ignore_country_in_request(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        exp_report_settings,
        cfg_v2_report_extractors,
):
    response = await call_v1_report_v2(
        json={
            'since_date': '2020-10-01',
            'till_date': '2020-12-01',
            'client_country': 'ignored_by_config_country',
        },
    )
    assert response.status == 200
    result = await response.text()
    assert result == DEFAULT_EXPECTED_RESULT


def _route_parts_extractor(field, subfield):
    pattern = '%(zone)s%(source)s%(separator)s%(destination)s: %(distance)s'
    return {
        'macro_transformations': [
            {
                'name': 'null_to_empty_string',
                'transformations': [
                    {
                        'kind': 'map_values',
                        'leave_unknown_untouched': True,
                        'result_on_null': '',
                        'mapping': {},
                    },
                ],
            },
        ],
        'extractors': {
            'claim_route_part_distance': {
                'source': 'receipt_doc',
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'route_parts_parsed',
                    },
                    {
                        'kind': 'transform_each_elem',
                        'transformations': [
                            {
                                'kind': 'make_object_with_fields',
                                'fields': {
                                    'zone': 'area',
                                    'source': 'area',
                                    'destination': 'area',
                                    'separator': 'area',
                                    'distance': field,
                                },
                            },
                            {
                                'kind': 'transform_object_field',
                                'field_name': 'zone',
                                'transformations': [
                                    {
                                        'kind': 'field_by_name',
                                        'field_name': 'zone',
                                    },
                                    {'kind': 'null_to_empty_string'},
                                ],
                            },
                            {
                                'kind': 'transform_object_field',
                                'field_name': 'source',
                                'transformations': [
                                    {
                                        'kind': 'field_by_name',
                                        'field_name': 'source',
                                    },
                                    {'kind': 'null_to_empty_string'},
                                ],
                            },
                            {
                                'kind': 'transform_object_field',
                                'field_name': 'destination',
                                'transformations': [
                                    {
                                        'kind': 'field_by_name',
                                        'field_name': 'destination',
                                    },
                                    {'kind': 'null_to_empty_string'},
                                ],
                            },
                            {
                                'kind': 'transform_object_field',
                                'field_name': 'separator',
                                'transformations': [
                                    {
                                        'kind': 'field_by_name',
                                        'field_name': 'destination',
                                    },
                                    {
                                        'kind': 'map_values',
                                        'result_on_null': '',
                                        'result_on_no_mapping': '..',
                                        'mapping': {},
                                    },
                                ],
                            },
                            {
                                'kind': 'transform_object_field',
                                'field_name': 'distance',
                                'transformations': [
                                    {
                                        'kind': 'field_by_name',
                                        'field_name': subfield,
                                    },
                                    {'kind': 'round', 'ndigits': 2},
                                ],
                            },
                            {
                                'kind': 'object_to_formated_string',
                                'pattern': pattern,
                            },
                        ],
                    },
                    {'kind': 'join_list_to_string', 'delimiter': '; '},
                ],
            },
        },
    }


@pytest.mark.servicetest
async def test_v1_report_v2_route_parts_distance(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        lazy_exp_report_settings,
        lazy_cfg_v2_report_extractors,
):
    await lazy_exp_report_settings(field_names=['claim_route_part_distance'])
    await lazy_cfg_v2_report_extractors(
        json=_route_parts_extractor('distance', 'meters'),
    )
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result) == [
        ['claim_route_part_distance'],
        [
            (
                'moscow: 834.02; suburb: 138.82; moscow: 35258.87; '
                'suburb: 26570.24; dme: 68345.32; suburb: 10448.13'
            ),
        ],
        ['""'],
        ['moscow..dme: 1851.04'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2_route_parts_priced_distance(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        lazy_exp_report_settings,
        lazy_cfg_v2_report_extractors,
):
    await lazy_exp_report_settings(field_names=['claim_route_part_distance'])
    await lazy_cfg_v2_report_extractors(
        json=_route_parts_extractor('distance', 'priced_meters'),
    )
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result) == [
        ['claim_route_part_distance'],
        [
            (
                'moscow: 0; suburb: 0; moscow: 33231.71; suburb: 26570.24; '
                'dme: 11147.27; suburb: 10448.13'
            ),
        ],
        ['""'],
        ['moscow..dme: 151.04'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2_route_parts_priced_time(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        lazy_exp_report_settings,
        lazy_cfg_v2_report_extractors,
):
    await lazy_exp_report_settings(field_names=['claim_route_part_distance'])
    await lazy_cfg_v2_report_extractors(
        json=_route_parts_extractor('time', 'priced_seconds'),
    )
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result) == [
        ['claim_route_part_distance'],
        [
            (
                'moscow: 300.0; suburb: 100.0; moscow: 25386.0; '
                'suburb: 19129.0; dme: 49208.0; suburb: 7523.0'
            ),
        ],
        ['""'],
        ['moscow..dme: 0'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2_first_city_zonal_prices(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        lazy_exp_report_settings,
        lazy_cfg_v2_report_extractors,
):
    extractors = {
        'macro_sources': [
            {
                'name': 'first_city_time_prices',
                'source': 'receipt_doc',
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'first_city_zonal_time_prices',
                    },
                ],
            },
        ],
        'extractors': {
            'first_threshold': {
                'source': 'first_city_time_prices',
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 0},
                    {'kind': 'field_by_name', 'field_name': 'begin'},
                ],
            },
            'first_price': {
                'source': 'first_city_time_prices',
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 0},
                    {'kind': 'field_by_name', 'field_name': 'price'},
                ],
            },
            'second_threshold': {
                'source': 'first_city_time_prices',
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 1},
                    {'kind': 'field_by_name', 'field_name': 'begin'},
                ],
            },
            'second_price': {
                'source': 'first_city_time_prices',
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 1},
                    {'kind': 'field_by_name', 'field_name': 'price'},
                ],
            },
        },
    }
    await lazy_exp_report_settings(
        field_names=[
            'first_threshold',
            'first_price',
            'second_threshold',
            'second_price',
        ],
    )
    await lazy_cfg_v2_report_extractors(json=extractors)
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result) == [
        ['first_threshold', 'first_price', 'second_threshold', 'second_price'],
        ['5.0', '9.0', '15.0', '19.0'],
        ['', '', '', ''],
        ['77', '6', '', ''],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2_suburb_zonal_prices(
        call_v1_report_v2,
        create_yt_tables_with_data,
        mock_v1_clients,
        lazy_exp_report_settings,
        lazy_cfg_v2_report_extractors,
):
    extractors = {
        'macro_sources': [
            {
                'name': 'suburb_dist_prices',
                'source': 'category_doc',
                'memoization': True,
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'distance_prices_by_zone',
                    },
                    {'kind': 'field_by_name', 'field_name': 'suburb'},
                ],
            },
        ],
        'extractors': {
            'first_threshold': {
                'source': 'suburb_dist_prices',
                'memoization': True,
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 0},
                    {'kind': 'field_by_name', 'field_name': 'begin'},
                ],
            },
            'first_price': {
                'source': 'suburb_dist_prices',
                'memoization': True,
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 0},
                    {'kind': 'field_by_name', 'field_name': 'price'},
                ],
            },
            'second_threshold': {
                'source': 'suburb_dist_prices',
                'memoization': True,
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 1},
                    {'kind': 'field_by_name', 'field_name': 'begin'},
                ],
            },
            'second_price': {
                'source': 'suburb_dist_prices',
                'memoization': True,
                'transformations': [
                    {'kind': 'elem_by_index', 'index': 1},
                    {'kind': 'field_by_name', 'field_name': 'price'},
                ],
            },
        },
    }
    await lazy_exp_report_settings(
        field_names=[
            'first_threshold',
            'first_price',
            'second_threshold',
            'second_price',
        ],
    )
    await lazy_cfg_v2_report_extractors(json=extractors)
    response = await call_v1_report_v2()
    assert response.status == 200
    result = await response.text()
    assert conftest.parse_tsv(result) == [
        ['first_threshold', 'first_price', 'second_threshold', 'second_price'],
        ['33.0', '45.0', '', ''],
        ['', '', '', ''],
        ['33.0', '45.0', '', ''],
    ]
