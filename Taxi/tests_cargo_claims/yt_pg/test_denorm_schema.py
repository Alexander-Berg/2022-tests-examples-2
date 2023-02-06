import typing

import pytest


NEW_TABLE_ERROR_MESSAGE = """
В базу добавлены новые таблицы: {}
О том как добавлять новые таблицы описано:
https://wiki.yandex-team.ru/taxi/backend/logistics/dokumentacija/replikacija-i-arxivirovanie/#dobavlenienovojjtablicy
"""  # noqa: E501  # pylint: disable=line-too-long


NEW_FIELDS_IN_TABLE_ERROR_MESSAGE = """
В таблицу {} добавлены новые поля: {}
О том как добавлять новые поля описано:
https://wiki.yandex-team.ru/taxi/backend/logistics/dokumentacija/replikacija-i-arxivirovanie/#dobavleniepoljavsushhestvujushhujutablicu
"""  # noqa: E501  # pylint: disable=line-too-long


TEMPORARY_SKIP_FIELDS: typing.Dict[str, typing.Set[str]] = {
    # 'table_name': {'field_1_name', 'field_2_name'},
    'claim_segments': {'route_id'},
}


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_all_tables_in_response(
        taxi_cargo_claims, denorm_required_tables,
):
    response = await taxi_cargo_claims.get(
        '/v1/test/claim/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200

    response_tables = set(response.json()) - {'uuid_id'}
    assert (
        response_tables == denorm_required_tables
    ), NEW_TABLE_ERROR_MESSAGE.format(denorm_required_tables - response_tables)


@pytest.mark.pgsql('cargo_claims', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_CLAIMS_DENORM_READ_SETTINGS_V2={
        '__default__': {
            'enabled': True,
            'yt-use-runtime': False,
            'yt-timeout-ms': 1000,
            'ttl-days': 3650,
        },
    },
)
async def test_all_fields_in_response(
        taxi_cargo_claims, get_denorm_table_fields, pgsql,
):
    response = await taxi_cargo_claims.get(
        '/v1/test/claim/full',
        params={'claim_id': '9756ae927d7b42dc9bbdcbb832924343'},
    )
    assert response.status == 200
    cursor = pgsql['cargo_claims'].cursor()
    for table_name, fields in response.json().items():
        if table_name == 'uuid_id':
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
