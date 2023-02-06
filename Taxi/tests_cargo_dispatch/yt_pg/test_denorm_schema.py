import typing

import pytest


NEW_TABLE_ERROR_MESSAGE = """
В базу добавленны новые таблицы: {}
О том как добавлять новые таблицы описано:
https://wiki.yandex-team.ru/taxi/backend/logistics/dokumentacija/replikacija-i-arxivirovanie/#dobavlenienovojjtablicy
"""  # noqa: E501  # pylint: disable=line-too-long


NEW_FIELDS_IN_TABLE_ERROR_MESSAGE = """
В таблицу {} добавлены новые поля: {}
О том как добавлять новые поля описано:
https://wiki.yandex-team.ru/taxi/backend/logistics/dokumentacija/replikacija-i-arxivirovanie/#dobavleniepoljavsushhestvujushhujutablicu
"""  # noqa: E501  # pylint: disable=line-too-long


DENORM_TABLE_ERROR = """
Таблицы: {} не относятся ни к одному denorm и не указаны в NO_NEED_IN_DENORM
"""  # noqa: E501  # pylint: disable=line-too-long


TEMPORARY_SKIP_FIELDS: typing.Dict[str, typing.Set[str]] = {
    # 'table_name': {'field_1_name', 'field_2_name'},
}


async def test_all_tables_in_some_denorm(
        denorm_required_tables,
        segment_required_tables,
        waybill_required_tables,
):
    tables_without_denorm = (
        denorm_required_tables
        - segment_required_tables
        - waybill_required_tables
    )
    assert tables_without_denorm == set(), DENORM_TABLE_ERROR.format(
        tables_without_denorm,
    )


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {
            'enabled': True,
            'pg-use': True,
            'yt-use': False,
            'ttl-days': 3650,
        },
    },
)
async def test_all_tables_in_segment_response(
        taxi_cargo_dispatch, segment_required_tables, waybill_required_tables,
):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/segments/full',
        params={'segment_id': 'abe645fc-14d2-4cda-ba58-af5e55ff1459'},
    )
    assert response.status == 200

    response_tables = set(response.json()['segment']) - {'segment_id'}
    assert (
        response_tables == segment_required_tables
    ), NEW_TABLE_ERROR_MESSAGE.format(
        segment_required_tables - response_tables,
    )
    response_tables = set(response.json()['waybills'][0]) - {'external_ref'}
    assert (
        response_tables == waybill_required_tables
    ), NEW_TABLE_ERROR_MESSAGE.format(
        waybill_required_tables - response_tables,
    )


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {
            'enabled': True,
            'pg-use': True,
            'yt-use': False,
            'ttl-days': 3650,
        },
    },
)
async def test_all_tables_in_waybill_response(
        taxi_cargo_dispatch, segment_required_tables, waybill_required_tables,
):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/waybills/full',
        params={
            'external_ref': (
                'logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7'
            ),
        },
    )
    assert response.status == 200

    response_tables = set(response.json()['waybill']) - {'external_ref'}
    assert (
        response_tables == waybill_required_tables
    ), NEW_TABLE_ERROR_MESSAGE.format(
        waybill_required_tables - response_tables,
    )
    response_tables = set(response.json()['segments'][0]) - {'segment_id'}
    assert (
        response_tables == segment_required_tables
    ), NEW_TABLE_ERROR_MESSAGE.format(
        segment_required_tables - response_tables,
    )


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {
            'enabled': True,
            'pg-use': True,
            'yt-use': False,
            'ttl-days': 3650,
        },
    },
)
async def test_all_fields_in_segment_response(
        taxi_cargo_dispatch, get_denorm_table_fields, pgsql,
):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/segments/full',
        params={'segment_id': 'abe645fc-14d2-4cda-ba58-af5e55ff1459'},
    )
    assert response.status == 200
    cursor = pgsql['cargo_dispatch'].cursor()
    for table_name, fields in response.json()['segment'].items():
        if table_name == 'segment_id':
            continue
        if isinstance(fields, list):
            response_fields = set(fields[0])
        else:
            response_fields = set(fields)
        required_table_fields = get_denorm_table_fields(cursor, table_name)
        required_table_fields -= TEMPORARY_SKIP_FIELDS.get(table_name, set())
        assert response_fields == required_table_fields, (
            NEW_FIELDS_IN_TABLE_ERROR_MESSAGE.format(
                table_name, required_table_fields - response_fields,
            )
        )


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {
            'enabled': True,
            'pg-use': True,
            'yt-use': False,
            'ttl-days': 3650,
        },
    },
)
async def test_all_fields_in_waybill_response(
        taxi_cargo_dispatch, get_denorm_table_fields, pgsql,
):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/waybills/full',
        params={
            'external_ref': (
                'logistic-dispatch/954bdd28-1029-4770-9907-b4a8ed8b0aa7'
            ),
        },
    )
    assert response.status == 200
    cursor = pgsql['cargo_dispatch'].cursor()
    for table_name, fields in response.json()['waybill'].items():
        if table_name == 'external_ref':
            continue
        if isinstance(fields, list):
            response_fields = set(fields[0])
        else:
            response_fields = set(fields)
        required_table_fields = get_denorm_table_fields(cursor, table_name)
        required_table_fields -= TEMPORARY_SKIP_FIELDS.get(table_name, set())
        assert response_fields == required_table_fields, (
            NEW_FIELDS_IN_TABLE_ERROR_MESSAGE.format(
                table_name, required_table_fields - response_fields,
            )
        )
