import pytest

from tests_fleet_financial_statements.common import errors
from tests_fleet_financial_statements.common import jsonx


NOW = '2020-01-10T00:00:00+00:00'


def pd_id_set(request):
    return {item['id'] for item in request['items']}


@pytest.mark.now(NOW)
async def test_default(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        statement_view,
        statement_view_response,
):
    response = await statement_view()
    assert response.status_code == 200, response.text
    assert response.json() == statement_view_response

    assert retrieve_driver_profiles.times_called == 1
    assert retrieve_driver_balances.times_called == 1
    assert retrieve_personal_emails.times_called == 1
    assert retrieve_personal_phones.times_called == 1

    request = retrieve_driver_profiles.next_call()['request']
    assert request.query == {'consumer': 'fleet-financial-statements'}
    json = jsonx.sort(request.json, 'id_in_set')
    json = jsonx.sort(json, 'projection')
    assert json == {
        'id_in_set': [
            'PARK-01_DRIVER-01',
            'PARK-01_DRIVER-02',
            'PARK-01_DRIVER-03',
            'PARK-01_DRIVER-04',
            'PARK-01_DRIVER-05',
        ],
        'projection': [
            'data.email_pd_ids',
            'data.full_name',
            'data.phone_pd_ids',
            'data.rule_id',
            'data.work_status',
        ],
    }

    request = retrieve_driver_balances.next_call()['request']
    json = jsonx.sort(request.json, 'query.park.driver_profile.ids')
    assert json == {
        'query': {
            'balance': {'accrued_ats': [NOW]},
            'park': {
                'driver_profile': {
                    'ids': ['DRIVER-01', 'DRIVER-02', 'DRIVER-03'],
                },
                'id': 'PARK-01',
            },
        },
    }

    request = retrieve_personal_emails.next_call()['request']
    json = jsonx.sort(request.json, 'items', key='id')
    assert json == {
        'items': [{'id': 'EMAIL01'}, {'id': 'EMAIL02'}, {'id': 'EMAIL0X'}],
        'primary_replica': False,
    }

    request = retrieve_personal_phones.next_call()['request']
    json = jsonx.sort(request.json, 'items', key='id')
    assert json == {
        'items': [{'id': 'PHONE01'}, {'id': 'PHONE03'}, {'id': 'PHONE0X'}],
        'primary_replica': False,
    }


@pytest.mark.now(NOW)
async def test_without_personal(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        statement_view,
        statement_view_response,
):
    response = await statement_view(
        yandex_uid='9999', user_ticket_provider='yandex_team',
    )
    assert response.status_code == 200, response.text
    assert response.json() == statement_view_response

    assert retrieve_driver_profiles.times_called == 1
    assert retrieve_driver_balances.times_called == 1
    assert retrieve_personal_emails.times_called == 0
    assert retrieve_personal_phones.times_called == 0

    request = retrieve_driver_profiles.next_call()['request']
    assert request.query == {'consumer': 'fleet-financial-statements'}
    json = jsonx.sort(request.json, 'id_in_set')
    json = jsonx.sort(json, 'projection')
    assert json == {
        'id_in_set': [
            'PARK-01_DRIVER-01',
            'PARK-01_DRIVER-02',
            'PARK-01_DRIVER-03',
            'PARK-01_DRIVER-04',
            'PARK-01_DRIVER-05',
        ],
        'projection': ['data.full_name', 'data.rule_id', 'data.work_status'],
    }

    request = retrieve_driver_balances.next_call()['request']
    json = jsonx.sort(request.json, 'query.park.driver_profile.ids')
    assert json == {
        'query': {
            'balance': {'accrued_ats': [NOW]},
            'park': {
                'driver_profile': {
                    'ids': ['DRIVER-01', 'DRIVER-02', 'DRIVER-03'],
                },
                'id': 'PARK-01',
            },
        },
    }


async def test_page1(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        statement_view,
        statement_view_response,
):
    response = await statement_view(page_size=3, page_number=1)
    assert response.status_code == 200, response.text
    assert response.json() == statement_view_response


async def test_page2(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        statement_view,
        statement_view_response,
):
    response = await statement_view(page_size=3, page_number=2)
    assert response.status_code == 200, response.text
    assert response.json() == statement_view_response


async def test_does_not_exist(statement_view):
    response = await statement_view(id='ffffffff-ffff-ffff-ffff-ffffffffffff')
    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': errors.EC_DOES_NOT_EXIST,
        'message': errors.EM_DOES_NOT_EXIST,
    }


async def test_has_been_deleted(statement_view):
    response = await statement_view(id='00000000-0000-0000-0000-000000000002')
    assert response.status_code == 410, response.text
    assert response.json() == {
        'code': errors.EC_HAS_BEEN_DELETED,
        'message': errors.EM_HAS_BEEN_DELETED,
    }


async def test_pg_primary(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        testpoint,
        statement_view,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_view()
    assert response.status_code == 200, response.text

    assert host.times_called == 1
    assert host.next_call() == {'data': {'host': 'master'}}


async def test_pg_secondary(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        testpoint,
        statement_view,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_view(revision=9)
    assert response.status_code == 200, response.text

    assert host.times_called == 1
    assert host.next_call() == {'data': {'host': 'slave|nearest'}}


async def test_pg_fallback(
        dispatcher_access_control,
        retrieve_driver_profiles,
        retrieve_driver_balances,
        retrieve_personal_emails,
        retrieve_personal_phones,
        testpoint,
        statement_view,
):
    @testpoint('postgres-host')
    def host(data):
        pass

    response = await statement_view(revision=10)
    assert response.status_code == 200, response.text

    assert host.times_called == 2
    assert host.next_call() == {'data': {'host': 'slave|nearest'}}
    assert host.next_call() == {'data': {'host': 'master'}}
