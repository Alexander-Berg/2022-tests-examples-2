import copy

import pytest

from . import conftest


DOUBLE_TO_STR_COMMA_TRANSFORM = {
    'name': 'double_to_string_comma',
    'transformations': [
        {'kind': 'to_string'},
        {'kind': 'replace_in_string', 'old': ',', 'new': '.'},
    ],
}


@pytest.fixture(name='call_v1_report_v2_with_configs')
def _call_v1_report_v2_with_configs(
        create_yt_tables_with_data,
        mock_v1_clients,
        call_v1_report_v2,
        lazy_cfg_v2_report_extractors,
        lazy_exp_report_settings,
):
    async def _call(extractors, field_names):
        await lazy_cfg_v2_report_extractors(json=extractors)
        await lazy_exp_report_settings(field_names=field_names)
        response = await call_v1_report_v2()
        assert response.status == 200
        text_result = await response.text()
        return conftest.parse_tsv(text_result)

    return _call


def _claim_requirements_extractor_config():
    return {
        'macro_transformations': [DOUBLE_TO_STR_COMMA_TRANSFORM],
        'macro_sources': [
            {
                'name': 'claim_requirements',
                'source': 'receipt_doc',
                'memoization': True,
                'transformations': [
                    {'field_name': 'requirements', 'kind': 'field_by_name'},
                    {'kind': 'parse'},
                ],
            },
            {
                'name': 'd2d_price_double',
                'source': 'claim_requirements',
                'memoization': True,
                'transformations': [
                    {
                        'field_name': 'name',
                        'field_value': 'door_to_door',
                        'kind': 'find_elem_by_field_value',
                    },
                    {'field_name': 'total_price', 'kind': 'field_by_name'},
                    {'kind': 'to_double'},
                ],
            },
            {
                'name': 'pro_courier_price_double',
                'memoization': True,
                'source': 'claim_requirements',
                'transformations': [
                    {
                        'field_name': 'name',
                        'field_value': 'pro_courier',
                        'kind': 'find_elem_by_field_value',
                    },
                    {'field_name': 'total_price', 'kind': 'field_by_name'},
                    {'kind': 'to_double'},
                ],
            },
        ],
        'extractors': {
            'd2d_price': {
                'source': 'd2d_price_double',
                'transformations': [{'kind': 'double_to_string_comma'}],
            },
        },
    }


@pytest.mark.servicetest
async def test_v1_report_v2__parse__memoized_src(
        call_v1_report_v2_with_configs,
):
    table = await call_v1_report_v2_with_configs(
        extractors=_claim_requirements_extractor_config(),
        field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__null_to_value(call_v1_report_v2_with_configs):
    extractors = _claim_requirements_extractor_config()
    extractors['extractors']['d2d_price']['transformations'].insert(
        0, {'kind': 'null_to_value', 'value': 0},
    )
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['0'], ['0']]


@pytest.mark.servicetest
async def test_v1_report_v2__macro_null_in_null_out(
        call_v1_report_v2_with_configs,
):
    new_double_to_str = copy.deepcopy(DOUBLE_TO_STR_COMMA_TRANSFORM)
    new_double_to_str['null_in_null_out'] = True
    # нужно, чтоб увидеть изменение результата.
    # Это преобразование не отработает
    new_double_to_str['transformations'].insert(
        0, {'kind': 'null_to_value', 'value': 0},
    )
    extractors = _claim_requirements_extractor_config()
    extractors['macro_transformations'][0] = new_double_to_str
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__in_place_null_in_null_out(
        call_v1_report_v2_with_configs,
):
    new_double_to_str = copy.deepcopy(DOUBLE_TO_STR_COMMA_TRANSFORM)
    # null_in_null_out здесь отменяет само преобразование,
    # без декоратора был бы 0
    new_double_to_str['transformations'].insert(
        0, {'null_in_null_out': True, 'kind': 'null_to_value', 'value': 0},
    )
    extractors = _claim_requirements_extractor_config()
    extractors['macro_transformations'][0] = new_double_to_str
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__macro_vs_in_place_null_in_null_out(
        call_v1_report_v2_with_configs,
):
    new_double_to_str = copy.deepcopy(DOUBLE_TO_STR_COMMA_TRANSFORM)
    # явное включение по месту приоритетнее отключения в макросе
    new_double_to_str['null_in_null_out'] = False
    new_double_to_str['transformations'].insert(
        0, {'kind': 'null_to_value', 'value': 0},
    )
    extractors = _claim_requirements_extractor_config()
    extractors['macro_transformations'][0] = new_double_to_str
    extractors['extractors']['d2d_price']['transformations'][0][
        'null_in_null_out'
    ] = True
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__in_place_vs_macro_null_in_null_out(
        call_v1_report_v2_with_configs,
):
    new_double_to_str = copy.deepcopy(DOUBLE_TO_STR_COMMA_TRANSFORM)
    # явное включение в макросе приоритетнее отключения по месту
    new_double_to_str['null_in_null_out'] = True
    new_double_to_str['transformations'].insert(
        0, {'kind': 'null_to_value', 'value': 0},
    )
    extractors = _claim_requirements_extractor_config()
    extractors['macro_transformations'][0] = new_double_to_str
    extractors['extractors']['d2d_price']['transformations'][0][
        'null_in_null_out'
    ] = False
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['d2d_price'],
    )
    assert table == [['d2d_price'], ['150.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__find_starts_with(call_v1_report_v2_with_configs):
    extractors = _claim_requirements_extractor_config()
    extractors['extractors']['pro_courier_price'] = {
        'source': 'claim_requirements',
        'transformations': [
            {
                'field_name': 'name',
                'field_value_starts_with': 'pro_',
                'kind': 'find_elem_by_field_value_starts_with',
            },
            {'field_name': 'total_price', 'kind': 'field_by_name'},
        ],
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['pro_courier_price'],
    )
    assert table == [['pro_courier_price'], ['250'], ['""'], ['37']]


@pytest.mark.servicetest
@pytest.mark.translations(cargo={'phoenix_web_key': {'ru': 'Феникс'}})
async def test_v1_report_v2__map_with_translation(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'api_kind': {
                'raw_claim_field': 'claim_doc',
                'transformations': [
                    {'kind': 'parse'},
                    {'kind': 'field_by_name', 'field_name': 'api_kind'},
                    {
                        'kind': 'map_values',
                        'mapping': [
                            {
                                'old': 'phoenix_web',
                                'new': {
                                    'tanker_key': 'phoenix_web_key',
                                    'keyset': 'cargo',
                                },
                            },
                            {
                                'old': 'api',
                                'new': {
                                    'tanker_key': 'api_key',
                                    'keyset': 'cargo',
                                    'default': 'api_default',
                                },
                            },
                        ],
                        'result_on_null': {
                            'tanker_key': 'unknown_key',
                            'keyset': 'cargo',
                        },
                    },
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['api_kind'],
    )
    assert table == [
        ['api_kind'],
        ['Феникс'],
        ['unknown_key'],
        ['api_default'],
    ]


@pytest.mark.servicetest
@pytest.mark.translations(
    cargo={
        'report.has_payment': {'ru': 'Да'},
        'report.no_payment': {'ru': 'Нет'},
    },
)
async def test_v1_report_v2__split__traslate__join__for_each(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'macro_transformations': [
            {
                'name': 'translate_has_payment',
                'memoization': True,
                'null_in_null_out': True,
                'transformations': [
                    {
                        'kind': 'map_values',
                        'mapping': [
                            {'old': 'false', 'new': 'no'},
                            {'old': 'true', 'new': 'has'},
                        ],
                    },
                    {
                        'kind': 'translate',
                        'keyset': 'cargo',
                        'tanker_key_pattern': 'report.{}_payment',
                    },
                ],
            },
        ],
        'extractors': {
            'has_payment': {
                'raw_claim_field': 'has_payment',
                'transformations': [
                    {'kind': 'split_string', 'separator': ';'},
                    {
                        'kind': 'transform_each_elem',
                        'transformations': [{'kind': 'translate_has_payment'}],
                    },
                    {'kind': 'join_list_to_string', 'delimiter': ';'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['has_payment'],
    )
    assert table == [['has_payment'], ['Нет;Да;Нет;Нет'], ['Нет'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__join_with_null_skipping__map_with_null(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'has_payment': {
                'raw_claim_field': 'has_payment',
                'transformations': [
                    {'kind': 'split_string', 'separator': ';'},
                    {
                        'kind': 'transform_each_elem',
                        'transformations': [
                            {
                                'kind': 'map_values',
                                'mapping': [
                                    {'old': 'false', 'new': None},
                                    {'old': 'true', 'new': 'has'},
                                ],
                            },
                        ],
                    },
                    {
                        'kind': 'join_list_to_string',
                        'skip_nulls': True,
                        'delimiter': ';',
                    },
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['has_payment'],
    )
    assert table == [['has_payment'], ['has'], ['""'], ['""']]


def _claim_reqs_sum_extractor_config():
    extractors = _claim_requirements_extractor_config()
    extractors['extractors']['sum_req_prices'] = {
        'aggregate': {
            'kind': 'sum',
            'sources': [
                {'source': 'd2d_price_double'},
                {'source': 'pro_courier_price_double'},
            ],
        },
        'transformations': [{'kind': 'double_to_string_comma'}],
    }
    return extractors


@pytest.mark.servicetest
async def test_v1_report_v2__sum_aggregation(call_v1_report_v2_with_configs):
    extractors = _claim_reqs_sum_extractor_config()
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['400.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__sum_aggregation_skip_nulls(
        call_v1_report_v2_with_configs,
):
    extractors = _claim_reqs_sum_extractor_config()
    extractors['extractors']['sum_req_prices']['aggregate'][
        'skip_nulls'
    ] = True
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['400.0'], ['0'], ['37.0']]


@pytest.mark.servicetest
async def test_v1_report_v2__mul_aggregation_skip_nulls(
        call_v1_report_v2_with_configs,
):
    extractors = _claim_reqs_sum_extractor_config()
    extractors['extractors']['sum_req_prices']['aggregate'][
        'kind'
    ] = 'multiplication'
    extractors['extractors']['sum_req_prices']['aggregate'][
        'skip_nulls'
    ] = True
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['37500.0'], ['1'], ['37.0']]


@pytest.mark.servicetest
async def test_v1_report_v2__to_list_aggregation__sum(
        call_v1_report_v2_with_configs,
):
    extractors = _claim_reqs_sum_extractor_config()
    extractors['extractors']['sum_req_prices']['aggregate'][
        'kind'
    ] = 'make_list'
    extractors['extractors']['sum_req_prices']['transformations'].insert(
        0, {'kind': 'sum_list'},
    )
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['400.0'], ['""'], ['""']]


@pytest.mark.servicetest
async def test_v1_report_v2__to_list_aggregation__mul(
        call_v1_report_v2_with_configs,
):
    extractors = _claim_reqs_sum_extractor_config()
    extractors['extractors']['sum_req_prices']['aggregate'][
        'kind'
    ] = 'make_list'
    extractors['extractors']['sum_req_prices']['transformations'].insert(
        0, {'kind': 'mul_list', 'skip_nulls': True},
    )
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['37500.0'], ['1'], ['37.0']]


@pytest.mark.servicetest
async def test_v1_report_v2__first_not_null_aggregation(
        call_v1_report_v2_with_configs,
):
    extractors = _claim_reqs_sum_extractor_config()
    extractors['extractors']['sum_req_prices']['aggregate'][
        'kind'
    ] = 'first_not_null'
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['sum_req_prices'],
    )
    assert table == [['sum_req_prices'], ['150.0'], ['""'], ['37.0']]


def _claim_reqs_extractor_with_src_templates_config():
    return {
        'source_templates': {
            'claim_requirement_price': {
                'source': 'claim_requirements',
                'memoization': True,
                'transformations': [
                    {
                        'field_name': 'name',
                        'field_value': '##req_name',
                        'kind': 'find_elem_by_field_value',
                    },
                    {'field_name': 'total_price', 'kind': 'field_by_name'},
                ],
            },
        },
        'macro_sources': [
            {
                'name': 'claim_requirements',
                'source': 'receipt_doc',
                'memoization': True,
                'transformations': [
                    {'field_name': 'requirements', 'kind': 'field_by_name'},
                    {'kind': 'parse'},
                ],
            },
            {
                'template': 'claim_requirement_price',
                'name': 'd2d_price',
                'template_params': {'##req_name': 'door_to_door'},
            },
            {
                'template': 'claim_requirement_price',
                'name': 'pro_courier_price',
                'template_params': {'##req_name': 'pro_courier'},
            },
        ],
        'extractors': {
            'd2d_price': {'source': 'd2d_price'},
            'pro_courier_price': {'source': 'pro_courier_price'},
        },
    }


@pytest.mark.servicetest
async def test_v1_report_v2_macro_source_template(
        call_v1_report_v2_with_configs,
):
    table = await call_v1_report_v2_with_configs(
        extractors=_claim_reqs_extractor_with_src_templates_config(),
        field_names=['d2d_price', 'pro_courier_price'],
    )
    assert table == [
        ['d2d_price', 'pro_courier_price'],
        ['150', '250'],
        ['', ''],
        ['', '37'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2_source_template(call_v1_report_v2_with_configs):
    extractors = _claim_reqs_extractor_with_src_templates_config()
    extractors['extractors']['pro_courier_price_on_template'] = {
        'template': 'claim_requirement_price',
        'tanker_key': 'pro_courier_key',
        'template_params': {'##req_name': 'pro_courier'},
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['pro_courier_price_on_template'],
    )
    assert table == [['pro_courier_key'], ['250'], ['""'], ['37']]


@pytest.mark.servicetest
async def test_v1_report_v2_transform_template(call_v1_report_v2_with_configs):
    extractors = {
        'transformation_templates': {
            'get_with_name': {
                'field_name': 'name',
                'field_value': '##name',
                'kind': 'find_elem_by_field_value',
            },
        },
        'macro_sources': [
            {
                'name': 'pro_courier_price',
                'source': 'receipt_doc',
                'transformations': [
                    {'field_name': 'requirements', 'kind': 'field_by_name'},
                    {'kind': 'parse'},
                    {
                        'template': 'get_with_name',
                        'template_params': {'##name': 'pro_courier'},
                    },
                    {'field_name': 'total_price', 'kind': 'field_by_name'},
                ],
            },
        ],
        'extractors': {'pro_courier_price': {'source': 'pro_courier_price'}},
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['pro_courier_price'],
    )
    assert table == [['pro_courier_price'], ['250'], ['""'], ['37']]


@pytest.mark.servicetest
async def test_v1_report_v2_macro_transform_template(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'macro_transformation_templates': {
            'get_req_value': {
                'transformations': [
                    {'field_name': 'requirements', 'kind': 'field_by_name'},
                    {'kind': 'parse'},
                    {
                        'field_name': 'name',
                        'field_value': '##req_name',
                        'kind': 'find_elem_by_field_value',
                    },
                    {'field_name': 'total_price', 'kind': 'field_by_name'},
                ],
            },
        },
        'macro_transformations': [
            {
                'template': 'get_req_value',
                'name': 'get_pro_courier',
                'template_params': {'##req_name': 'pro_courier'},
            },
        ],
        'extractors': {
            'pro_courier_price': {
                'source': 'receipt_doc',
                'transformations': [{'kind': 'get_pro_courier'}],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['pro_courier_price'],
    )
    assert table == [['pro_courier_price'], ['250'], ['""'], ['37']]


@pytest.mark.servicetest
async def test_v1_report_v2__mul_coef(call_v1_report_v2_with_configs):
    extractors = {
        'extractors': {
            'price': {
                'raw_claim_field': 'final_price_without_vat',
                'transformations': [{'kind': 'mul_coef', 'coef': 0.000001}],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['price'],
    )
    assert table == [['price'], ['2353.0'], ['2210.0'], ['2353.0']]


@pytest.mark.servicetest
async def test_v1_report_v2__add_value(call_v1_report_v2_with_configs):
    extractors = {
        'extractors': {
            'price': {
                'raw_claim_field': 'final_price_without_vat',
                'transformations': [{'kind': 'add_value', 'value': 667}],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['price'],
    )
    assert table == [['price'], ['2353000667'], ['2210000667'], ['2353000667']]


@pytest.mark.servicetest
async def test_v1_report_v2__negative_to_zero(call_v1_report_v2_with_configs):
    extractors = {
        'extractors': {
            'price': {
                'raw_claim_field': 'final_price_without_vat',
                'transformations': [
                    {'kind': 'mul_coef', 'coef': -1},
                    {'kind': 'negative_to_zero'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['price'],
    )
    assert table == [['price'], ['0'], ['0'], ['0']]


@pytest.mark.servicetest
async def test_v1_report_v2__datetime(call_v1_report_v2_with_configs):
    extractors = {
        'macro_sources': [
            {
                'name': 'created_ts',
                'raw_claim_field': 'claim_doc',
                'transformations': [
                    {'kind': 'parse'},
                    {'kind': 'field_by_name', 'field_name': 'created_ts'},
                    {'kind': 'field_by_name', 'field_name': 'value'},
                    {'kind': 'datetime_from_isoformat'},
                ],
            },
        ],
        'extractors': {
            'raw': {'source': 'created_ts'},
            'weekday': {
                'source': 'created_ts',
                'transformations': [{'kind': 'datetime_to_day_of_week'}],
            },
            'to_utc': {
                'source': 'created_ts',
                'transformations': [
                    {'kind': 'datetime_replace_timezone_info_utc'},
                ],
            },
            'to_moscow': {
                'source': 'created_ts',
                'transformations': [{'kind': 'datetime_as_timezone'}],
            },
            'date': {
                'source': 'created_ts',
                'transformations': [
                    {'kind': 'datetime_to_string', 'format': '%Y-%m-%d'},
                ],
            },
            'time': {
                'source': 'created_ts',
                'transformations': [
                    {'kind': 'datetime_to_string', 'format': '%H:%M:%S'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors,
        field_names=['raw', 'weekday', 'to_utc', 'to_moscow', 'date', 'time'],
    )
    assert table == [
        ['raw', 'weekday', 'to_utc', 'to_moscow', 'date', 'time'],
        [
            '2022-06-27 10:12:11.472169',
            '0',
            '2022-06-27 10:12:11.472169+00:00',
            '2022-06-27 10:12:11.472169+03:00',
            '2022-06-27',
            '10:12:11',
        ],
        ['', '', '', '', '', ''],
        [
            '2022-07-28 14:10:15.412169',
            '3',
            '2022-07-28 14:10:15.412169+00:00',
            '2022-07-28 14:10:15.412169+03:00',
            '2022-07-28',
            '14:10:15',
        ],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2__datetime_from_timestamp(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'updated_ts': {
                'raw_claim_field': 'updated_ts',
                'transformations': [{'kind': 'datetime_from_timestamp'}],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['updated_ts'],
    )
    assert table == [
        ['updated_ts'],
        ['2020-10-19 12:10:27.691193'],
        ['2020-12-01 17:45:58.111000'],
        ['2020-12-01 17:45:58.111000'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2__insert_string_into_pattern(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'departure_time_with_date': {
                'raw_claim_field': 'departure_time',
                'transformations': [
                    {
                        'kind': 'insert_string_into_pattern',
                        'pattern': '2022-01-01T{}',
                    },
                    {'kind': 'datetime_from_isoformat'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['departure_time_with_date'],
    )
    assert table == [
        ['departure_time_with_date'],
        ['2022-01-01 12:10:27'],
        ['2022-01-01 22:45:58'],
        ['2022-01-01 12:10:27'],
    ]


@pytest.mark.servicetest
async def test_v1_report_v2__round(call_v1_report_v2_with_configs):
    extractors = {
        'extractors': {
            'price': {
                'raw_claim_field': 'final_price_without_vat',
                'transformations': [
                    {'kind': 'mul_coef', 'coef': 0.000000001},
                    {'kind': 'round', 'ndigits': 2},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['price'],
    )
    assert table == [['price'], ['2.35'], ['2.21'], ['2.35']]


@pytest.mark.servicetest
@pytest.mark.translations(
    cargo={'report.min_sec_interval': {'ru': '%(min)s минут %(sec)s секунд'}},
)
async def test_v1_report_v2__min_inteval(call_v1_report_v2_with_configs):
    extractors = {
        'extractors': {
            'total_time': {
                'source': 'receipt_doc',
                'transformations': [
                    {'field_name': 'total_time', 'kind': 'field_by_name'},
                    {'kind': 'to_double'},
                    {'kind': 'mul_coef', 'coef': 0.01},
                    {'kind': 'min_interval_to_pretty_string'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['total_time'],
    )
    assert table == [
        ['total_time'],
        ['2 минут 20 секунд'],
        ['""'],
        ['13 минут 19 секунд'],
    ]


@pytest.mark.servicetest
@pytest.mark.translations(
    geoareas={'moscow': {'ru': 'Москва'}, 'spb': {'ru': 'Санкт-Петербург'}},
)
async def test_v1_report_v2__geoareas_translate(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'homezone': {
                'raw_claim_field': 'claim_doc',
                'transformations': [
                    {'kind': 'parse'},
                    {'field_name': 'zone_id', 'kind': 'field_by_name'},
                    {
                        'kind': 'translate',
                        'keyset': 'geoareas',
                        'tanker_key_pattern': '{}',
                    },
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['homezone'],
    )
    assert table == [['homezone'], ['Москва'], ['""'], ['Санкт-Петербург']]


@pytest.mark.servicetest
async def test_v1_report_v2__make_object__process_field__obj_to_str(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'prices': {
                'raw_claim_field': 'claim_doc',
                'transformations': [
                    {'kind': 'parse'},
                    {
                        'kind': 'make_object_with_fields',
                        'fields': {
                            'homezone': 'zone_id',
                            'price': 'cargo_pricing_price',
                        },
                    },
                    {
                        'kind': 'transform_object_field',
                        'field_name': 'price',
                        'transformations': [
                            {'field_name': 'value', 'kind': 'field_by_name'},
                            {'kind': 'to_double'},
                            {'kind': 'mul_coef', 'coef': 3},
                        ],
                    },
                    {
                        'kind': 'object_to_formated_string',
                        'pattern': '%(homezone)s: %(price)s$',
                    },
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['prices'],
    )
    assert table == [['prices'], ['moscow: 1053.0$'], ['""'], ['spb: 933.0$']]


@pytest.mark.servicetest
@pytest.mark.translations(
    cargo={'homezone_title': {'ru': 'Зона - %(homezone)s'}},
)
async def test_v1_report_v2__obj_to_str_with_translation(
        call_v1_report_v2_with_configs,
):
    extractors = {
        'extractors': {
            'zone+text': {
                'raw_claim_field': 'claim_doc',
                'transformations': [
                    {'kind': 'parse'},
                    {
                        'kind': 'make_object_with_fields',
                        'fields': {'homezone': 'zone_id'},
                    },
                    {
                        'kind': 'object_to_formated_string',
                        'pattern': {
                            'tanker_key': 'homezone_title',
                            'keyset': 'cargo',
                            'default': 'Zone %(homezone)s',
                        },
                    },
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors, field_names=['zone+text'],
    )
    assert table == [['zone+text'], ['Зона - moscow'], ['""'], ['Зона - spb']]


@pytest.mark.servicetest
async def test_v1_report_v2__filter_list(call_v1_report_v2_with_configs):
    extractors = {
        'macro_transformations': [
            {
                'name': 'extract_meters_from_route_parts',
                'transformations': [
                    {
                        'kind': 'transform_each_elem',
                        'transformations': [
                            {
                                'kind': 'field_by_name',
                                'field_name': 'distance',
                            },
                            {'kind': 'field_by_name', 'field_name': 'meters'},
                            {'kind': 'round', 'ndigits': 1},
                            {'kind': 'to_string'},
                        ],
                    },
                ],
            },
        ],
        'extractors': {
            'city_distance': {
                'source': 'receipt_doc',
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'route_parts_parsed',
                    },
                    {
                        'kind': 'filter_list',
                        'filter': {
                            'kind': 'field_value_not_equals_to',
                            'field_name': 'full_zone_name',
                            'field_value_not_equals_to': 'suburb',
                        },
                    },
                    {'kind': 'extract_meters_from_route_parts'},
                    {'kind': 'join_list_to_string', 'delimiter': ';'},
                ],
            },
            'suburb_distance': {
                'source': 'receipt_doc',
                'transformations': [
                    {
                        'kind': 'field_by_name',
                        'field_name': 'route_parts_parsed',
                    },
                    {
                        'kind': 'filter_list',
                        'filter': {
                            'kind': 'field_value_equals_to',
                            'field_name': 'full_zone_name',
                            'field_value_equals_to': 'suburb',
                        },
                    },
                    {'kind': 'extract_meters_from_route_parts'},
                    {'kind': 'join_list_to_string', 'delimiter': ';'},
                ],
            },
        },
    }
    table = await call_v1_report_v2_with_configs(
        extractors=extractors,
        field_names=['city_distance', 'suburb_distance'],
    )
    assert table == [
        ['city_distance', 'suburb_distance'],
        ['834.0;35258.9;68345.3', '138.8;26570.2;10448.1'],
        ['', ''],
        ['1851.0', ''],
    ]
