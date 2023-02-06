import pytest

from tests_coupons import util
from tests_coupons.admin import common


WRONG = ['notexist']

HANDLERS = {
    'basic': 'edit',
    'externalbudget': 'edit_external_budget',
    'firstlimit': 'edit_first_limit',
}

DEPRECATED = {'creditcard_only'}

OPTIONAL_BOOL_FIELDS = [
    'is_volatile',
    'usage_per_promocode',
    'first_usage_by_classes',
    'first_usage_by_payment_methods',
    'percent_limit_per_trip',
    'creditcard_only',
    'for_support',
    'clear_text',
    'external_budget',
]

COUPONS_EDITABLE_FIELDS = {
    'default': [*common.BASIC_CHANGES.keys()],
    'external_budget_coupon': [*common.EXTERNAL_BUDGET_CHANGES.keys()],
    'first_limit_coupon': [*common.FIRST_LIMIT_CHANGES.keys(), 'currency'],
}


def data_for_series(series_id, extra_data=None, without=None):
    data = dict(common.GOOD_CHANGES[series_id], **{'series_id': series_id})
    data = dict(data, **(extra_data or {}))
    if without:
        data.pop(without, None)
    return data


def get_request_params(handler, data):
    """
    Process tech keys in data: {'data', 'extra', 'headers', 'without'}
    """
    headers = common.HEADERS
    if 'extra' in data:
        extra_field = data['extra']
        data = {extra_field: data_for_series('firstlimit')[extra_field]}
    if 'data' in data:
        data = data['data']
    elif 'without' in data:
        data = data_for_series(handler, data, without=data['without'])
    elif 'headers' in data:
        headers = data['headers']
        data = data_for_series(handler)
    else:
        data = data_for_series(handler, data)
    return data, HANDLERS[handler], headers


@pytest.mark.parametrize(
    'handler, data, expected_code',
    [
        # no data cases
        *[
            pytest.param(
                handler, {'data': value}, 400, id=f'{handler}: {text}',
            )
            for (value, text) in (
                (None, 'no data'),
                # ({}, 'empty data'),
            )
            for handler in HANDLERS
        ],
        # data with wrong service
        *[
            pytest.param(
                handler, {'services': value}, 400, id=f'{handler}: {text}',
            )
            for (value, text) in (
                ([], 'no service'),
                (WRONG, 'wrong service'),
                (common.GOOD_SERVICES + WRONG, 'good services with wrong one'),
            )
            for handler in HANDLERS
        ],
        # data with wrong class
        *[
            pytest.param(
                handler, {'classes': value}, 400, id=f'{handler}: {text}',
            )
            for (value, text) in (
                (WRONG, 'wrong class'),
                (common.GOOD_CLASSES + WRONG, 'good classes with wrong one'),
            )
            for handler in HANDLERS
        ],
        # data with wrong payment methods
        *[
            pytest.param(
                handler,
                {'payment_methods': value},
                400,
                id=f'{handler}: {text}',
            )
            for (value, text) in (
                (WRONG, 'wrong payment method'),
                (
                    common.GOOD_PAYMENT_METHODS + WRONG,
                    'good payment methods with wrong one',
                ),
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # data with wrong application
        *[
            pytest.param(
                handler, {'applications': value}, 400, id=f'{handler}: {text}',
            )
            for (value, text) in (
                (WRONG, 'wrong application'),
                (
                    common.GOOD_APPLICATIONS + WRONG,
                    'good applications with wrong one',
                ),
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # correct data, but wrong handler
        *[
            pytest.param(
                handler,
                {'series_id': another_handler},
                400,
                id=f'{handler}: wrong handler for {another_handler} series',
            )
            for handler in HANDLERS
            for another_handler in HANDLERS
            if handler != another_handler
        ],
        # series not exist (not found)
        *[
            pytest.param(
                handler,
                {'series_id': f'notexist{handler}'},
                404,
                id=f'{handler}: series not found',
            )
            for handler in HANDLERS
        ],
        # payment_methods & creditcard_only inconsistency
        *[
            pytest.param(handler, data, 400, id=f'{handler}: {text}')
            for (data, text) in (
                (
                    {'creditcard_only': True},
                    'creditcard_only is true, but payment_methods != [card]',
                ),
                (
                    {'payment_methods': ['card']},
                    'creditcard_only is false, but payment_methods == [card]',
                ),
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # first usage flags inconsistency
        *[
            pytest.param(handler, data, 400, id=f'{handler}: {text}')
            for field_name in ('classes', 'payment_methods')
            for (data, text) in (
                (
                    {
                        f'first_usage_by_{field_name}': True,
                        'without': field_name,
                    },
                    f'first usage flag is true, but no {field_name}',
                ),
                (
                    {f'first_usage_by_{field_name}': True, field_name: []},
                    f'first usage flag is true, but empty {field_name}',
                ),
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # bin_range & bank_name inconsistency
        *[
            pytest.param(
                handler, {'without': field_name}, 400, id=f'{handler}: {text}',
            )
            for (field_name, text) in (
                ('bank_name', 'bin_ranges without bank_name'),
                ('bin_ranges', 'bank_name without bin_ranges'),
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # change start date in used series
        *[
            pytest.param(
                handler,
                {},
                400,
                marks=pytest.mark.filldb(promocode_usages='used'),
                id=f'{handler}: edit start date in used series',
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # no ticket header
        pytest.param(
            'basic',
            {'headers': {}},
            {'check': 200, 'apply': 400},
            id='basic: no ticket header',
        ),
        # wrong dates
        *[
            pytest.param(
                handler,
                {field_name: '31-02-2020'},
                400,
                id=f'{handler}: wrong {field_name} date',
            )
            for field_name in ('finish',)
            for handler in HANDLERS
        ],
        *[
            pytest.param(
                handler,
                {field_name: '31-11-2019'},
                400,
                id=f'{handler}: wrong {field_name} date',
            )
            for field_name in ('start',)
            for handler in ('externalbudget', 'firstlimit')
        ],
        pytest.param(
            'firstlimit',
            {'requires_activation_after': '31-06-2019'},
            400,
            id='firstlimit: wrong requires_activation_after date',
        ),
        # wrong country
        pytest.param(
            'firstlimit',
            {'country': 'zzz'},
            400,
            id='firstlimit: wrong country',
        ),
        # ok data, all fields
        *[
            pytest.param(handler, {}, 200, id=f'{handler}: all fields')
            for handler in HANDLERS
        ],
        # ok data, extra fields (ignoring)
        *[
            pytest.param(
                handler,
                {'extra': field_name},
                200,
                id=f'{handler}: extra {field_name}',
            )
            for field_name in (
                'start',
                'descr',
                'user_limit',
                'creditcard_only',
            )
            for handler in ('basic',)
        ],
        pytest.param(
            'basic',
            common.EXTRA_EB_CHANGES,
            200,
            id='basic: extra external budget fields',
        ),
        *[
            pytest.param(
                handler,
                {'extra': field_name},
                200,
                id=f'{handler}: extra {field_name}',
            )
            for field_name in (
                'is_unique',
                'value',
                'country',
                'for_support',
                'is_volatile',
            )
            for handler in ('basic', 'externalbudget')
        ],
        pytest.param(
            'externalbudget',
            common.EXTRA_FL_CHANGES,
            200,
            id='externalbudget: extra first limit fields',
        ),
        *[
            pytest.param(
                handler,
                {'ticket': 'TAXIBACKEND-4'},
                200,
                id=f'{handler}: extra unknown field',
            )
            for handler in HANDLERS
        ],
        # ok data, no optional header
        *[
            pytest.param(
                handler,
                {'headers': {}},
                200,
                id=f'{handler}: no optional tickets header',
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # ok data, with true first usage flags
        *[
            pytest.param(
                handler,
                {field_name: True},
                200,
                id=f'{handler}: {field_name} is true',
            )
            for field_name in (
                'first_usage_by_classes',
                'first_usage_by_payment_methods',
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        # ok data, without some optional field
        *[
            pytest.param(
                handler,
                {'without': field_name},
                200,
                id=f'{handler}: no optional {field_name}',
            )
            for field_name in ('cities', 'classes', 'external_meta')
            for handler in HANDLERS
        ],
        *[
            pytest.param(
                handler,
                {'without': field_name},
                200,
                id=f'{handler}: no optional {field_name}',
            )
            for field_name in (
                'usage_per_promocode',
                'first_usage_by_classes',
                'first_usage_by_payment_methods',
                'applications',
                'payment_methods',
                'creditcard_only',
            )
            for handler in ('externalbudget', 'firstlimit')
        ],
        *[
            pytest.param(
                handler,
                {'without': field_name},
                200,
                id=f'{handler}: no optional {field_name}',
            )
            for field_name in (
                'requires_activation_after',
                'count',
                'percent',
                'percent_limit_per_trip',
            )
            for handler in ('firstlimit',)
        ],
    ],
)
@pytest.mark.parametrize('mode', common.HANDLE_MODES)
@pytest.mark.config(COUPONS_EDITABLE_FIELDS=COUPONS_EDITABLE_FIELDS)
async def test_edit(
        make_admin_request,
        handler,
        data,
        mode,
        expected_code,
        load_json,
        mongodb,
        tariffs,
):
    if isinstance(expected_code, dict):
        expected_code = expected_code[mode]

    overrided_fields = set(data) & set(common.GOOD_CHANGES[handler])
    missing_field = data.get('without', None)
    should_check_json = expected_code == 200 and not (
        missing_field or overrided_fields
    )
    is_apply_ok = expected_code == 200 and mode == 'apply'
    is_tariffs_expected = is_apply_ok and missing_field != 'cities'
    should_check_db = is_apply_ok and not missing_field
    keys_ignored = (set(data) - overrided_fields) | {data.get('extra', 'data')}

    args_find_series = ({'_id': handler}, {'updated_at': 0})
    doc_before = mongodb.promocode_series.find_one(*args_find_series)

    data, url, headers = get_request_params(handler, data)
    response = await make_admin_request(data, mode, url, headers)
    assert response.status_code == expected_code
    assert tariffs.times_called == is_tariffs_expected
    response_json = response.json()

    if should_check_json:
        expected_json = load_json(f'expected_response_{mode}.json')[handler]
        response_json = util.sort_json(response_json, common.PATH_TO_SORT)
        assert response_json == expected_json
    elif (
        is_apply_ok
        and missing_field
        and missing_field not in DEPRECATED
        and missing_field not in OPTIONAL_BOOL_FIELDS
    ):
        unset_in_response = response_json['update'].get('$unset', {})
        assert (missing_field in unset_in_response) == (
            missing_field in doc_before
        )
        assert missing_field not in response_json['update']['$set']

    doc_after = mongodb.promocode_series.find_one(*args_find_series)
    if is_apply_ok:
        assert doc_before != doc_after

        if should_check_db:
            update = common.prepare_update_data(
                data, common.CALCULATED[handler], without=keys_ignored,
            )
            modified_doc = dict(doc_before, **update)

            for opt_field in OPTIONAL_BOOL_FIELDS:
                if opt_field not in doc_after:
                    doc_after[opt_field] = False
                if opt_field not in modified_doc:
                    modified_doc[opt_field] = False

            modified_doc_sorted = util.sort_json(
                modified_doc, common.FIELDS_TO_SORT,
            )
            doc_after_sorted = util.sort_json(doc_after, common.FIELDS_TO_SORT)
            assert modified_doc_sorted == doc_after_sorted

    else:
        assert doc_before == doc_after


@pytest.mark.parametrize(
    'city_ids, expected_zones',
    [
        pytest.param([], [], id='Empty cities list'),
        pytest.param(['Город не существует'], [], id='Non existent city'),
        pytest.param(
            ['Москва'], ['himki', 'shodnya'], id='City with multiple zones',
        ),
        pytest.param(
            ['Уфа', 'Тула', 'Уфа'],
            ['ufa', 'tula'],
            id='Cities with duplicates',
        ),
        pytest.param(
            ['Звенигород', 'Тула', 'Город не существует'],
            ['tula', 'zvenigorod'],
            id='Several cities, one does not exist',
        ),
    ],
)
async def test_edit_apply_zones(
        make_admin_request,
        city_ids,
        expected_zones,
        load_json,
        tariffs,
        mongodb,
):
    """
    Checks that zones are calculated right (apply).
    """
    handler, data = 'basic', {'cities': city_ids}

    data, url, headers = get_request_params(handler, data)
    response = await make_admin_request(data, 'apply', url, headers)
    assert tariffs.times_called == (1 if city_ids else 0)
    assert response.status_code == 200

    response_zones = response.json()['update']['$set']['zones']
    assert sorted(expected_zones) == sorted(response_zones)
