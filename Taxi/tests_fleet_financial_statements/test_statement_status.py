from tests_fleet_financial_statements.common import errors


async def test_pg_primary(
        testpoint, statement_status, statement_status_responses,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_status()
    assert response.status_code == 200, response.text
    assert response.json() == statement_status_responses['DEFAULT']

    assert host.times_called == 1
    assert host.next_call() == {'data': {'host': 'master'}}


async def test_pg_secondary(
        testpoint, statement_status, statement_status_responses,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_status(revision=2)
    assert response.status_code == 200, response.text
    assert response.json() == statement_status_responses['DEFAULT']

    assert host.times_called == 1
    assert host.next_call() == {'data': {'host': 'slave|nearest'}}


async def test_pg_fallback(
        testpoint, statement_status, statement_status_responses,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_status(revision=3)
    assert response.status_code == 200, response.text
    assert response.json() == statement_status_responses['DEFAULT']

    assert host.times_called == 2
    assert host.next_call() == {'data': {'host': 'slave|nearest'}}
    assert host.next_call() == {'data': {'host': 'master'}}


async def test_does_not_exist(statement_status):
    response = await statement_status(
        id='ffffffff-ffff-ffff-ffff-ffffffffffff',
    )
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': errors.EC_DOES_NOT_EXIST,
        'message': errors.EM_DOES_NOT_EXIST,
    }


async def test_has_been_deleted(statement_status):
    response = await statement_status(
        id='00000000-0000-0000-0000-000000000002',
    )
    assert response.status_code == 410, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_DELETED,
        'message': errors.EM_HAS_BEEN_DELETED,
    }
