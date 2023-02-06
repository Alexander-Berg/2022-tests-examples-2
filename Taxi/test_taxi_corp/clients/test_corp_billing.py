# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import config
from taxi.clients import http_client
from taxi.clients import tvm

from taxi_corp.clients import corp_billing


@pytest.fixture
async def client(loop, db, simple_secdist):
    async with http_client.HTTPClient(loop=loop) as session:
        config_ = config.Config(db)
        yield corp_billing.CorpBillingClient(
            config=config_,
            session=session,
            tvm_client=tvm.TVMClient(
                service_name='corp-billing',
                secdist=simple_secdist,
                config=config_,
                session=session,
            ),
        )


@pytest.mark.parametrize(
    ['external_ref', 'name', 'expected_body'],
    [
        pytest.param(
            'corp_client_id',
            'corp_client_name',
            {
                'external_ref': 'corp_client_id',
                'payment_method_name': 'corp_client_name',
            },
            id='simple create',
        ),
    ],
)
async def test_create_client(patch, client, external_ref, name, expected_body):
    expected_location = '/v1/clients/create'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']

    await client.create_client(external_ref, name)
    assert _request.calls


@pytest.mark.parametrize(
    [
        'external_ref',
        'name',
        'revision',
        'suspended',
        'yandex_uid',
        'services',
        'expected_body',
    ],
    [
        pytest.param(
            'corp_client_id',
            'corp_client_name',
            1,
            False,
            'yandex_uid1',
            [{'service_type': 'eats/rus', 'suspended': False}],
            {
                'external_ref': 'corp_client_id',
                'payment_method_name': 'corp_client_name',
                'revision': 1,
                'all_services_suspended': False,
                'yandex_uid': 'yandex_uid1',
                'services': [{'service_type': 'eats/rus', 'suspended': False}],
            },
            id='simple update',
        ),
        pytest.param(
            'corp_client_id',
            'corp_client_name',
            1,
            False,
            'yandex_uid1',
            None,
            {
                'external_ref': 'corp_client_id',
                'payment_method_name': 'corp_client_name',
                'revision': 1,
                'all_services_suspended': False,
                'yandex_uid': 'yandex_uid1',
                'services': [],
            },
            id='simple update null services',
        ),
    ],
)
async def test_update_client(
        patch,
        client,
        external_ref,
        name,
        revision,
        suspended,
        yandex_uid,
        services,
        expected_body,
):
    expected_location = '/v1/clients/update'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']

    await client.update_client(
        external_ref, name, revision, suspended, yandex_uid, services,
    )
    assert _request.calls


@pytest.mark.parametrize(
    ['external_ref', 'expected_body'],
    [
        pytest.param(
            'client_to_find',
            {'clients': [{'external_ref': 'client_to_find'}]},
            id='simple get',
        ),
    ],
)
async def test_find_client(patch, client, external_ref, expected_body):
    expected_location = '/v1/clients/find'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']
        return {'clients': []}

    await client.find_client(external_ref)
    assert _request.calls


@pytest.mark.parametrize(
    ['employee_external_ref', 'client_external_ref', 'expected_body'],
    [
        pytest.param(
            'user_id1',
            'client_id1',
            {'external_ref': 'user_id1', 'client_external_ref': 'client_id1'},
            id='simple create employee',
        ),
    ],
)
async def test_create_emloyee(
        patch,
        client,
        employee_external_ref,
        client_external_ref,
        expected_body,
):
    expected_location = '/v1/employees/create'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']

    await client.create_employee(employee_external_ref, client_external_ref)
    assert _request.calls


@pytest.mark.parametrize(
    ['employee_external_ref', 'group_external_ref', 'expected_body'],
    [
        pytest.param(
            'user_id1',
            None,
            {'employee_external_ref': 'user_id1'},
            id='simple upsert employee group without group',
        ),
        pytest.param(
            'user_id1',
            'role_id1',
            {
                'employee_external_ref': 'user_id1',
                'group_external_ref': 'role_id1',
            },
            id='simple upsert employee group with group',
        ),
    ],
)
async def test_upsert_employee_group(
        patch,
        client,
        employee_external_ref,
        group_external_ref,
        expected_body,
):
    expected_location = '/v1/employee-group/upsert'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']

    await client.upsert_employee_group(
        employee_external_ref, group_external_ref,
    )
    assert _request.calls


@pytest.mark.parametrize(
    [
        'client_external_ref',
        'external_ref',
        'revision',
        'all_services_suspended',
        'services',
        'service_limits',
        'expected_body',
    ],
    [
        pytest.param(
            'client_id',
            'user_id',
            1,
            False,
            [{'type': 'eats/rus', 'suspended': False}],
            [
                {
                    'service_type': 'eats/rus',
                    'monthly': {'currency': 'RUB', 'amount': '102.03'},
                },
            ],
            {
                'external_ref': 'user_id',
                'client_external_ref': 'client_id',
                'revision': 1,
                'all_services_suspended': False,
                'services': [{'type': 'eats/rus', 'suspended': False}],
                'service_limits': [
                    {
                        'service_type': 'eats/rus',
                        'monthly': {'currency': 'RUB', 'amount': '102.03'},
                    },
                ],
            },
            id='simple update employee',
        ),
    ],
)
async def test_update_employee(
        patch,
        client,
        client_external_ref,
        external_ref,
        revision,
        all_services_suspended,
        services,
        service_limits,
        expected_body,
):
    expected_location = '/v1/employees/update'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']

    await client.update_employee(
        external_ref,
        client_external_ref,
        revision,
        all_services_suspended,
        services,
        service_limits,
    )
    assert _request.calls


@pytest.mark.parametrize(
    ['user_id', 'expected_body'],
    [
        pytest.param(
            'user_id',
            {'employees': [{'external_ref': 'user_id'}]},
            id='simple find employee',
        ),
    ],
)
async def test_find_employee(patch, client, user_id, expected_body):
    expected_location = '/v1/employees/find'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']
        return {'employees': []}

    await client.find_employee(user_id)
    assert _request.calls


@pytest.mark.parametrize(
    ['expected_body'],
    [
        pytest.param(
            {'employees': [{'external_ref': 'user_id'}]},
            id='simple find employee',
        ),
    ],
)
async def test_find_employees(patch, client, expected_body):
    expected_location = '/v1/employees/find'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert expected_body == kwargs['data']
        return {'employees': []}

    await client.find_employees(expected_body)
    assert _request.calls


@pytest.mark.parametrize(
    ['employees', 'service_type', 'currency', 'expected'],
    [
        pytest.param(
            [{'external_ref': 'user_id'}],
            'eats/rus',
            'RUB',
            {
                'employees': [
                    {
                        'external_ref': 'user_id',
                        'suspended': False,
                        'limit': '1000.0000',
                        'spent': '300.0000',
                    },
                ],
            },
            id='simple find employee',
        ),
    ],
)
async def test_find_employees_spendings(
        patch, client, expected, employees, service_type, currency,
):
    expected_location = '/v1/employees-spendings/find'

    @patch('taxi_corp.clients.corp_billing.CorpBillingClient._request')
    async def _request(method, location, *args, **kwargs):
        assert location == expected_location
        assert kwargs['data'] == {
            'employees': employees,
            'service_type': service_type,
            'currency': currency,
            'from_dt': None,
        }
        return expected

    response = await client.find_employees_spendings(
        employees, service_type, currency,
    )
    assert response == expected['employees']
    assert _request.calls
