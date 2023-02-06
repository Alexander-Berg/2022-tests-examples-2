import pytest


@pytest.mark.ydb(files=['fill_data.sql'])
async def test_yql(taxi_cargo_corp_reports, ydb):
    cursor = ydb.execute('SELECT * FROM data')
    assert len(cursor) == 1
    assert len(cursor[0].rows) == 1

    row = cursor[0].rows[0]
    assert row == {
        'corp_client_id': b'corp_id_12345',
        'claim_id': b'321',
        'created_ts': 123.321,
        'claim_yson': b'{}',
        'pricing_yson': None,
        'order_proc_yson': None,
    }


@pytest.mark.ydb(files=['fill_data.sql'])
async def test_get_report(taxi_cargo_corp_reports, ydb):
    response = await taxi_cargo_corp_reports.get(
        'v1/report/find',
        headers={'X-B2B-Client-Id': '99999999829e48cca458b5feb161d5d6'},
        params={'claim_id': 'tmp', 'corp_client_id': 'tmp'},
    )

    assert response.json()['corps'][0] == {
        'corp_client_id': 'corp_id_12345',
        'claim_id': '321',
        'created_ts': 123.321,
        'claim_yson': '{}',
    }


async def test_add_report(taxi_cargo_corp_reports, ydb):
    claim_row = {
        'corp_client_id': '99999999829e48cca458b5feb1617777',
        'claim_id': '32111',
        'created_ts': 333.111,
        'claim_yson': '{"key": 999}',
        # 'pricing_yson': None,
        # 'order_proc_yson': None,
    }
    response = await taxi_cargo_corp_reports.post(
        'v1/report/insert', json=claim_row,
    )
    assert response.status_code == 200
    assert response.json() == {}

    response = await taxi_cargo_corp_reports.get(
        'v1/report/find',
        headers={'X-B2B-Client-Id': '99999999829e48cca458b5feb1617777'},
        params={'claim_id': '32111', 'corp_client_id': 'tmp'},
    )
    assert response.json()['corps'][0] == {
        'corp_client_id': '99999999829e48cca458b5feb1617777',
        'claim_id': '32111',
        'created_ts': 333.111,
        'claim_yson': '\x01\x18{"key": 999}',
    }
