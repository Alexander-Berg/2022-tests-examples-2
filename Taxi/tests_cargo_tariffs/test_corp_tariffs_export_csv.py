import pytest


def _get_default_ndd_client_tariff():
    return {
        'p': {
            'type': 'ndd_client_base_prices',
            'delivery': {'intake': '100', 'return_price_pct': '10.5'},
            'parcels': {
                'add_declared_value_pct': '5',
                'weight_prices': [
                    {'begin': '0', 'price_per_kilogram': '5.5'},
                    {'begin': '2.5', 'price_per_kilogram': '2.5'},
                ],
                'included_weight_price': '13',
            },
        },
        'tariff_status': 'active',
    }


def _get_default_ndd_client_tariff_for_create():
    return {
        'type': 'ndd_client_base_prices',
        'delivery': {'intake': '100', 'return_price_pct': '10.5'},
        'parcels': {
            'add_declared_value_pct': '5',
            'weight_prices': [
                {'begin': '0', 'price_per_kilogram': '5.5'},
                {'begin': '2.5', 'price_per_kilogram': '2.5'},
            ],
            'included_weight_price': '13',
        },
    }


def _get_default_create_tariffs():
    default_tariff = _get_default_ndd_client_tariff_for_create()
    none_default_tariff = _get_default_ndd_client_tariff_for_create()
    none_default_tariff['delivery']['intake'] = '35'
    none_default_tariff['parcels']['weight_prices'][0][
        'price_per_kilogram'
    ] = '7.3'
    return [
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'value': 'employer_code_1',
                    'sign': 'equal',
                },
                {
                    'field_name': 'source_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'destination_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'tariff_category',
                    'value': 'interval_with_fees',
                    'sign': 'equal',
                },
            ],
            'document': default_tariff,
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'value': 'employer_code_1',
                    'sign': 'equal',
                },
                {
                    'field_name': 'source_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'destination_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'tariff_category',
                    'value': 'interval_strict',
                    'sign': 'equal',
                },
            ],
            'document': none_default_tariff,
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'value': 'employer_code_1',
                    'sign': 'equal',
                },
                {
                    'field_name': 'source_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'destination_zone',
                    'value': 'SPB_KAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'tariff_category',
                    'value': 'interval_with_fees',
                    'sign': 'equal',
                },
            ],
            'document': default_tariff,
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'value': 'wrong_employer',
                    'sign': 'equal',
                },
                {
                    'field_name': 'source_zone',
                    'value': 'Moscow_CKAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'destination_zone',
                    'value': 'SPB_KAD',
                    'sign': 'equal',
                },
                {
                    'field_name': 'tariff_category',
                    'value': 'interval_strict',
                    'sign': 'equal',
                },
            ],
            'document': default_tariff,
        },
    ]


def _get_imported_tariff_with_no_employer():
    return {
        'conditions': [
            {
                'field_name': 'source_zone',
                'value': 'Moscow_CKAD',
                'sign': 'equal',
            },
            {
                'field_name': 'destination_zone',
                'value': 'SPB_KAD',
                'sign': 'equal',
            },
            {
                'field_name': 'tariff_category',
                'value': 'interval_with_fees',
                'sign': 'equal',
            },
        ],
        'document': _get_default_ndd_client_tariff_for_create(),
    }


def _row(columns, delimeter=None):
    if delimeter is None:
        delimeter = ';'
    return delimeter.join(columns)


def _get_default_csv_headers(delimeter=None):
    return _row(
        [
            'c.destination_zone.equal',
            'c.employer_id.equal',
            'c.source_zone.equal',
            'c.tariff_category.equal',
            't.delivery.intake',
            't.delivery.return_price_pct',
            't.parcels.add_declared_value_pct',
            't.parcels.included_weight_price',
            't.parcels.weight_prices.0.begin',
            't.parcels.weight_prices.0.price_per_kilogram',
            't.parcels.weight_prices.1.begin',
            't.parcels.weight_prices.1.price_per_kilogram',
            't.type',
        ],
        delimeter,
    )


def _get_default_csv_content(delimeter=None):
    result = sorted(
        [
            (
                'Moscow_CKAD;employer_code_1;Moscow_CKAD;interval_with_fees;'
                '100;10.5;5;13;0;5.5;2.5;2.5;ndd_client_base_prices'
            ),
            (
                'SPB_KAD;employer_code_1;Moscow_CKAD;interval_with_fees;'
                '100;10.5;5;13;0;5.5;2.5;2.5;ndd_client_base_prices'
            ),
            (
                'Moscow_CKAD;employer_code_1;Moscow_CKAD;interval_strict;'
                '35;10.5;5;13;0;7.3;2.5;2.5;ndd_client_base_prices'
            ),
        ],
    )
    if delimeter is None:
        return result
    result_replaced = []
    for x in result:
        result_replaced.append(x.replace(';', delimeter))
    return result_replaced


_DEFAULT_CORP_CLIENT_ID = '0123456789012345678901234567890a'


@pytest.fixture(name='export_corp_tariffs_csv')
def _export_corp_tariffs_csv(taxi_cargo_tariffs):
    async def _call(corp_client_id=None):
        if corp_client_id is None:
            corp_client_id = _DEFAULT_CORP_CLIENT_ID
        response = await taxi_cargo_tariffs.post(
            '/api/b2b/cargo-tariffs/v1/corp_tariffs/export/csv',
            params={'service': 'ndd_client'},
            headers={
                'X-B2B-Client-Id': corp_client_id,
                'Accept-Language': 'ru',
            },
        )
        return response

    return _call


def _get_default_comissions_config(corp_client_id=None):
    if corp_client_id is None:
        corp_client_id = _DEFAULT_CORP_CLIENT_ID
    return {
        corp_client_id: [
            {
                'comission_card': '0.018',
                'comission_cash': '0.011',
                'comission_link': '0.000',
            },
        ],
    }


@pytest.fixture(name='reset_comissions_config')
def _reset_comissions_config(taxi_config, taxi_cargo_tariffs):
    class Reseter:
        async def reset(self, body):
            taxi_config.set_values({'CARGO_PAYMENTS_COMISSIONS': body})
            await taxi_cargo_tariffs.invalidate_caches()

        async def reset_with_default_value(self, corp_client_id=None):
            await self.reset(
                body=_get_default_comissions_config(corp_client_id),
            )

    return Reseter()


def _split_csv_rows(response):
    return response.content[2:].decode('utf_16').split('\n')


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_check_unicode(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    res_csv = response.content
    # check BOM
    assert bytes(res_csv)[:2] == b'\xFF\xFE'
    # second BOM (frontend requirement)
    assert bytes(res_csv)[2:4] == b'\xFF\xFE'
    assert res_csv[2:].decode('utf_16') == res_csv[4:].decode('utf_16_le')
    assert res_csv[2:].decode('utf_16').encode('utf_16_le') == res_csv[4:]


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv(add_tariffs, export_corp_tariffs_csv):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _get_default_csv_headers()
    assert sorted(rows[1:]) == _get_default_csv_content()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_empty_values(
        add_tariffs, export_corp_tariffs_csv,
):
    tariff = _get_default_ndd_client_tariff_for_create()
    tariff['parcels']['weight_prices'].pop(0)

    imported_tariffs = [
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'sign': 'equal',
                    'value': 'employer_code_1',
                },
                {
                    'field_name': 'destination_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'tariff_category',
                    'sign': 'equal',
                    'value': 'interval_with_fees',
                },
            ],
            'document': _get_default_ndd_client_tariff_for_create(),
        },
        {
            'conditions': [
                {
                    'field_name': 'employer_id',
                    'sign': 'equal',
                    'value': 'employer_code_1',
                },
                {
                    'field_name': 'source_zone',
                    'sign': 'equal',
                    'value': 'Moscow_CKAD',
                },
                {
                    'field_name': 'destination_zone',
                    'sign': 'equal',
                    'value': 'SPB_KAD',
                },
                {
                    'field_name': 'tariff_category',
                    'sign': 'equal',
                    'value': 'interval_strict',
                },
            ],
            'document': tariff,
        },
    ]

    await add_tariffs(imported_tariffs)
    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 3

    assert rows[0] == _get_default_csv_headers()
    assert sorted(rows[1:]) == sorted(
        [
            (
                'SPB_KAD;employer_code_1;Moscow_CKAD;interval_strict;'
                '100;10.5;5;13;2.5;2.5;;;ndd_client_base_prices'
            ),
            (
                'Moscow_CKAD;employer_code_1;;interval_with_fees;'
                '100;10.5;5;13;0;5.5;2.5;2.5;ndd_client_base_prices'
            ),
        ],
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_default_tariff(
        add_tariffs, export_corp_tariffs_csv,
):
    imported_tariffs = [_get_imported_tariff_with_no_employer()]

    await add_tariffs(tariffs=imported_tariffs)

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 2

    assert rows[0] == _row(
        [
            'c.destination_zone.equal',
            'c.source_zone.equal',
            'c.tariff_category.equal',
            't.delivery.intake',
            't.delivery.return_price_pct',
            't.parcels.add_declared_value_pct',
            't.parcels.included_weight_price',
            't.parcels.weight_prices.0.begin',
            't.parcels.weight_prices.0.price_per_kilogram',
            't.parcels.weight_prices.1.begin',
            't.parcels.weight_prices.1.price_per_kilogram',
            't.type',
        ],
    )
    assert sorted(rows[1:]) == sorted(
        [
            (
                'SPB_KAD;Moscow_CKAD;interval_with_fees;'
                '100;10.5;5;13;0;5.5;2.5;2.5;ndd_client_base_prices'
            ),
        ],
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_default_and_none_default_tariff(
        add_tariffs, export_corp_tariffs_csv,
):
    imported_tariffs = _get_default_create_tariffs()
    imported_tariffs.append(_get_imported_tariff_with_no_employer())

    await add_tariffs(tariffs=imported_tariffs)

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4

    assert rows[0] == _get_default_csv_headers()
    assert sorted(rows[1:]) == _get_default_csv_content()


@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'headers_translations': [],
        'data_translations': [],
        'remove_columns': [
            # condition column
            {'field_pattern': 'c\\.employer_id\\.equal'},
            # condition column with checking values
            {
                'field_pattern': 'c\\.source_zone\\.equal',
                'remove_if': {'all_values_are': 'Moscow_CKAD'},
            },
            # tariff column with checking values
            {
                'field_pattern': 't\\.parcels\\.weight_prices\\.(\\d)\\.begin',
                'remove_if': {'all_values_are': '0'},
            },
            # tariff column
            {'field_pattern': 't\\.delivery\\.(.*)'},
        ],
    },
)
async def test_corptariffs_export_csv_with_removed_columns(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _row(
        [
            'c.destination_zone.equal',
            'c.tariff_category.equal',
            't.parcels.add_declared_value_pct',
            't.parcels.included_weight_price',
            't.parcels.weight_prices.0.price_per_kilogram',
            't.parcels.weight_prices.1.begin',
            't.parcels.weight_prices.1.price_per_kilogram',
            't.type',
        ],
    )
    assert sorted(rows[1:]) == sorted(
        [
            (
                'Moscow_CKAD;interval_with_fees;'
                '5;13;5.5;2.5;2.5;ndd_client_base_prices'
            ),
            (
                'SPB_KAD;interval_with_fees;'
                '5;13;5.5;2.5;2.5;ndd_client_base_prices'
            ),
            (
                'Moscow_CKAD;interval_strict;'
                '5;13;7.3;2.5;2.5;ndd_client_base_prices'
            ),
        ],
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(
    typed_geoareas={
        'next_day_delivery_tariffs__Moscow_CKAD': {'ru': 'Москва'},
    },
    corp_client={
        'ndd.delivery-policy.interval_with_fees': {'ru': 'Почти интервал'},
        'ndd.delivery-policy.interval_strict': {'ru': 'В интервал'},
    },
    cargo={'text.type': {'ru': 'X'}},
)
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'headers_translations': [],
        'data_translations': [
            {
                'field_pattern': 'c\\.destination_zone\\..*',
                'tanker_key_pattern': 'next_day_delivery_tariffs__{}',
                'keyset': 'typed_geoareas',
            },
            {
                'field_pattern': 'c\\.tariff_category\\.equal',
                'tanker_key_pattern': 'ndd.delivery-policy.{}',
                'keyset': 'corp_client',
            },
            {
                'field_pattern': 't\\.type',
                'tanker_key_pattern': 'text.type',
                'keyset': 'cargo',
            },
        ],
    },
)
async def test_corptariffs_export_csv_content_translation(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert sorted(rows[1:]) == sorted(
        [
            (
                'Москва;employer_code_1;Moscow_CKAD;Почти интервал;'
                '100;10.5;5;13;0;5.5;2.5;2.5;X'
            ),
            (
                'SPB_KAD;employer_code_1;Moscow_CKAD;Почти интервал;'
                '100;10.5;5;13;0;5.5;2.5;2.5;X'
            ),
            (
                'Москва;employer_code_1;Moscow_CKAD;В интервал;'
                '35;10.5;5;13;0;7.3;2.5;2.5;X'
            ),
        ],
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(cargo={'text.type': {'ru': 'X'}})
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'headers_translations': [],
        'data_translations': [
            # unexisting tanker key
            {
                'field_pattern': 'c\\.source_zone\\..*',
                'tanker_key_pattern': 'unexisting_key',
                'keyset': 'cargo',
            },
            # unexisting keyset
            {
                'field_pattern': 'c\\.source_zone\\..*',
                'tanker_key_pattern': 'unexisting_key',
                'keyset': 'unexisting_keyset',
            },
        ],
    },
)
async def test_corptariffs_export_csv_content_wrong_translation(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _get_default_csv_headers()
    assert sorted(rows[1:]) == _get_default_csv_content()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(
    cargo={
        'cargo_tariff_column__destination_zone': {'ru': 'Назначение'},
        'cargo_tariff_column__weight': {'ru': 'Порог %(number)s'},
        'text.type': {'ru': 'Тип'},
    },
)
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'data_translations': [],
        'headers_translations': [
            {
                'field_pattern': 'c\\.destination_zone\\..*',
                'tanker_key': 'cargo_tariff_column__destination_zone',
                'keyset': 'cargo',
            },
            {
                'field_pattern': (
                    't\\.parcels\\.weight_prices\\.(\\d*)\\.begin'
                ),
                'tanker_key': 'cargo_tariff_column__weight',
                'submatch_names': ['number'],
                'keyset': 'cargo',
            },
            {
                'field_pattern': 't\\.type',
                'tanker_key': 'text.type',
                'keyset': 'cargo',
            },
        ],
    },
)
async def test_corptariffs_export_csv_headers_translation(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _row(
        [
            'Назначение',
            'c.employer_id.equal',
            'c.source_zone.equal',
            'c.tariff_category.equal',
            't.delivery.intake',
            't.delivery.return_price_pct',
            't.parcels.add_declared_value_pct',
            't.parcels.included_weight_price',
            'Порог 0',
            't.parcels.weight_prices.0.price_per_kilogram',
            'Порог 1',
            't.parcels.weight_prices.1.price_per_kilogram',
            'Тип',
        ],
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(
    cargo={
        'cargo_tariff_column__destination_zone': {'ru': 'Назначение'},
        'cargo_tariff_column__weight': {'ru': 'Порог %(number)s'},
    },
)
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'data_translations': [],
        'headers_translations': [
            # unexisting tanker key
            {
                'field_pattern': 'c\\.source_zone\\..*',
                'tanker_key': 'unexisting_key',
                'keyset': 'cargo',
            },
            # unexisting keyset
            {
                'field_pattern': 'c\\.source_zone\\..*',
                'tanker_key': 'unexisting_key',
                'keyset': 'unexisting_keyset',
            },
            # wrong number of submatch_names
            {
                'field_pattern': (
                    't\\.(.*)\\.weight_prices\\.(\\d*)\\.price_per_kilogram'
                ),
                'tanker_key': 'cargo_tariff_column__weight',
                'submatch_names': ['number'],
                'keyset': 'cargo',
            },
            # wrong number of submatch_names
            {
                'field_pattern': 'c\\.source_zone\\..*',
                'tanker_key': 'cargo_tariff_column__destination_zone',
                'submatch_names': ['number'],
                'keyset': 'cargo',
            },
        ],
    },
)
async def test_corptariffs_export_csv_headers_wrong_translation(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _get_default_csv_headers()
    assert sorted(rows[1:]) == _get_default_csv_content()


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_no_employer(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    unexisting_corp_client_id = '01234567891239827394879283749824'
    response = await export_corp_tariffs_csv(
        corp_client_id=unexisting_corp_client_id,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'no employer code',
        'message': (
            'no employer with corp_client_id 01234567891239827394879283749824'
        ),
    }


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_no_employer_code(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv(
        corp_client_id='09812340981239827394879283749824',
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 'no employer code',
        'message': (
            'no employer_code for employer with corp_client_id '
            '09812340981239827394879283749824'
        ),
    }


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'data_translations': [],
        'headers_translations': [],
        'line_separator': '!\n',
        'values_delimeter': '  ',
    },
)
async def test_corptariffs_export_csv_custom_delimeters(
        add_tariffs, export_corp_tariffs_csv,
):
    await add_tariffs(_get_default_create_tariffs())

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    for i in range(3):
        assert rows[i][-1:] == '!'
        rows[i] = rows[i][:-1]

    assert rows[0] == _get_default_csv_headers('  ')
    assert sorted(rows[1:]) == _get_default_csv_content('  ')


def _default_csv_headers_with_end(end):
    return _get_default_csv_headers() + end


def _default_csv_content_with_end(end):
    content = _get_default_csv_content()
    result = []
    for x in content:
        result.append(x + end)
    return result


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_with_comissions(
        add_tariffs, export_corp_tariffs_csv, reset_comissions_config,
):
    await add_tariffs(_get_default_create_tariffs())
    await reset_comissions_config.reset_with_default_value()

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    comissions_headers = (
        ';s.comission.comission_card;s.comission.comission_link;'
        's.comission.comission_cash'
    )
    assert rows[0] == _default_csv_headers_with_end(comissions_headers)
    assert sorted(rows[1:]) == _default_csv_content_with_end(
        ';0.018;0.000;0.011',
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
async def test_corptariffs_export_csv_with_comissions_default_config(
        add_tariffs, export_corp_tariffs_csv, reset_comissions_config,
):
    await add_tariffs(_get_default_create_tariffs())
    await reset_comissions_config.reset_with_default_value(
        corp_client_id='default_NDD',
    )

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    comissions_headers = (
        ';s.comission.comission_card;s.comission.comission_link;'
        's.comission.comission_cash'
    )
    assert rows[0] == _default_csv_headers_with_end(comissions_headers)
    assert sorted(rows[1:]) == _default_csv_content_with_end(
        ';0.018;0.000;0.011',
    )


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'headers_translations': [],
        'data_translations': [],
        'remove_columns': [
            {'field_pattern': 's\\.comission\\.comission_card'},
            {'field_pattern': 's\\.comission\\.comission_link'},
        ],
    },
)
async def test_corptariffs_export_csv_with_comissions_and_removed_columns(
        add_tariffs, export_corp_tariffs_csv, reset_comissions_config,
):
    await add_tariffs(_get_default_create_tariffs())
    await reset_comissions_config.reset_with_default_value()

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    assert rows[0] == _default_csv_headers_with_end(
        ';s.comission.comission_cash',
    )
    assert sorted(rows[1:]) == _default_csv_content_with_end(';0.011')


@pytest.mark.geoareas(tg_filename='typed_geoareas_base.json')
@pytest.mark.translations(cargo={'comission_cash_key': {'ru': 'Нал'}})
@pytest.mark.config(
    CARGO_TARIFFS_CSV_TARIFF_EXPORT_SETTINGS={
        'data_translations': [],
        'headers_translations': [
            {
                'field_pattern': 's\\.comission\\.comission_cash',
                'tanker_key': 'comission_cash_key',
                'keyset': 'cargo',
            },
        ],
    },
)
async def test_corptariffs_export_csv_with_comissions_header_translation(
        add_tariffs, export_corp_tariffs_csv, reset_comissions_config,
):
    await add_tariffs(_get_default_create_tariffs())
    await reset_comissions_config.reset_with_default_value()

    response = await export_corp_tariffs_csv()
    assert response.status_code == 200

    rows = _split_csv_rows(response)
    assert len(rows) == 4
    commissions_headers = (
        ';s.comission.comission_card;s.comission.comission_link;Нал'
    )
    assert rows[0] == _default_csv_headers_with_end(commissions_headers)
