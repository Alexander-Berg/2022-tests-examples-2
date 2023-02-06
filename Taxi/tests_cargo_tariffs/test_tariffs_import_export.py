import copy

import pytest


async def test_export_with_filters(
        mock_cargo_reports_json_to_csv, v1_admin_csv,
):
    mock_cargo_reports_json_to_csv.response = 'csv;data'
    resp = await v1_admin_csv.export_csv(
        {'filters': [{'field_name': 'employer_id', 'value': 'corp_id_3'}]},
    )

    assert resp.status_code == 200
    assert mock_cargo_reports_json_to_csv.request == {'table': []}


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(
    cargo={
        't.p.delivery.intake': {'ru': 'Хз что это'},
        't.p.delivery.return_price_pct': {'ru': 'Хз что это'},
        't.p.parcels.add_declared_value_pct': {'ru': 'Хз что это'},
        't.p.parcels.included_weight_price': {'ru': 'Хз что это'},
        't.p.parcels.weight_prices.begin': {'ru': 'Порог %(number)s'},
        't.p.parcels.weight_prices.price_per_kilogram': {
            'ru': 'Цена с %(number)s',
        },
        't.tariff_status': {'ru': 'Статус тарифа'},
        'c.employer_id.equal': {'ru': 'ID работника'},
        'c.destination_zone.equal': {'ru': 'Зона прибытия'},
    },
)
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'data_translations': [],
        'headers_translations': [
            {
                'field_pattern': 't\\.p\\.delivery\\.intake',
                'tanker_key': 't.p.delivery.intake',
                'keyset': 'cargo',
            },
            {
                'field_pattern': 't\\.p\\.delivery\\.return_price_pct',
                'tanker_key': 't.p.delivery.return_price_pct',
                'keyset': 'cargo',
            },
            {
                'field_pattern': 't\\.p\\.parcels\\.add_declared_value_pct',
                'tanker_key': 't.p.parcels.add_declared_value_pct',
                'keyset': 'cargo',
            },
            {
                'field_pattern': 't\\.p\\.parcels\\.included_weight_price',
                'tanker_key': 't.p.parcels.included_weight_price',
                'keyset': 'cargo',
            },
            {
                'field_pattern': (
                    't\\.p\\.parcels\\.weight_prices\\.(\\d*)\\.begin'
                ),
                'tanker_key': 't.p.parcels.weight_prices.begin',
                'submatch_names': ['number'],
                'keyset': 'cargo',
            },
            {
                'field_pattern': (
                    't\\.p\\.parcels\\.weight_prices\\.'
                    '(\\d*)\\.price_per_kilogram'
                ),
                'tanker_key': 't.p.parcels.weight_prices.price_per_kilogram',
                'submatch_names': ['number'],
                'keyset': 'cargo',
            },
            {
                'field_pattern': 't\\.tariff_status',
                'tanker_key': 't.tariff_status',
                'keyset': 'cargo',
            },
            {
                'field_pattern': 'c\\.employer_id\\.equal',
                'tanker_key': 'c.employer_id.equal',
                'keyset': 'cargo',
            },
            {
                'field_pattern': 'c\\.destination_zone\\.equal',
                'tanker_key': 'c.destination_zone.equal',
                'keyset': 'cargo',
            },
        ],
    },
)
async def test_export(
        mock_cargo_reports_json_to_csv,
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
        fill_db,
):
    await fill_db()
    mock_cargo_reports_json_to_csv.response = 'csv;data'
    resp = await v1_admin_csv.export_csv({'filters': []})
    assert resp.status_code == 200
    assert (
        mock_cargo_reports_json_to_csv.request == default_json_to_csv_request
    )
    import_resp = mock_cargo_reports_json_to_csv.request
    import_resp['table'].append(copy.deepcopy(import_resp['table'][1]))
    del import_resp['table'][2]['c']['employer_id']
    import_resp['table'][2]['c']['destination_zone'] = {'equal': 'moscoww'}
    import_resp['table'][0]['c.destination_zone.equal'] = 'Зона прибытия'

    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 200

    await v1_admin_csv.export_csv({'filters': []})

    assert (
        mock_cargo_reports_json_to_csv.request
        == mock_cargo_reports_csv_to_json.response
    )


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_FIELDS={'employer_id': {'type': 'number'}},
)
async def test_bad_condition_type(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['c']['employer_id']['equal'] = 'not a number'
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': (
            'Line 2: Неправильный тип значения у условия employer_id, '
            'по конфигу CARGO_TARIFFS_CONDITIONS_FIELDS ожидался number'
        ),
    }


@pytest.mark.config(
    CARGO_TARIFFS_CONDITIONS_FIELDS={
        'source_geo_id': {'type': 'string'},
        'employer_id': {'type': 'string'},
    },
)
async def test_good_condition_type(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['c']['source_geo_id'] = {}
    import_resp['table'][1]['c']['source_geo_id']['equal'] = '1'
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 200


async def test_status_validation(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['t']['tariff_status'] = 'kek'
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': (
            'Line 2: Value of \'t.tariff_status\' (kek) '
            'is not parseable into enum'
        ),
    }


async def test_empty_condition(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][0]['c'] = {}  # <- empty conditions are ok
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 200


async def test_bad_condition_name(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['c'] = {'bad_cond_name': {'equal': 'corp_id_1'}}
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': (
            'Line 2: Условие bad_cond_name не найдено '
            'в конфиге CARGO_TARIFFS_CONDITIONS_FIELDS'
            ''
        ),
    }


async def test_all_tariff_fields_are_required(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    del import_resp['table'][1]['t']['p']['type']
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': 'Line 2: Field \'t.p.type\' is missing',
    }


async def test_empty_weight_prices(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['t']['p']['parcels']['weight_prices'] = []
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 200


async def test_numbers_with_comma(
        mock_cargo_reports_csv_to_json,
        default_json_to_csv_request,
        v1_admin_csv,
):
    import_resp = default_json_to_csv_request
    import_resp['table'][1]['t']['p']['parcels'][
        'add_declared_value_pct'
    ] = '1,5'
    mock_cargo_reports_csv_to_json.response = import_resp
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400


async def test_empty_json(mock_cargo_reports_csv_to_json, v1_admin_csv):
    mock_cargo_reports_csv_to_json.response = {'table': []}
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': 'csv распарсился в пустой JSON',
    }


async def test_cargo_reports_return_400(
        mock_cargo_reports_csv_to_json,
        default_ndd_client_tariff,
        zero_ndd_client_tariff,
        v1_admin_csv,
):
    mock_cargo_reports_csv_to_json.response_status_code = 400
    mock_cargo_reports_csv_to_json.response = {
        'code': 'validation_error',
        'message': 'some message',
    }
    resp = await v1_admin_csv.import_csv('csv;data')
    assert resp.status_code == 400
    assert resp.json() == {
        'code': 'validation_error',
        'message': 'Не получилось перевести csv в JSON: some message',
    }
