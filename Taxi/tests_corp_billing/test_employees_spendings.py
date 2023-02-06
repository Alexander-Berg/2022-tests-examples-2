import dataclasses

import pytest

CURRENCY = 'RUB'
DEFAULT_FROM_DT = '2019-11-01T00:00:00+00:00'


@pytest.mark.parametrize(
    ['service_type', 'from_dt'],
    [
        pytest.param('eats/rus', DEFAULT_FROM_DT),
        pytest.param('eats', DEFAULT_FROM_DT),
        pytest.param('taxi', DEFAULT_FROM_DT),
    ],
)
@pytest.mark.now('2019-11-22T00:00:00Z')
async def test_employees_spendings(
        # pylint: disable=W0621
        request_find_spendings,
        _fill_ya_team,
        spend_money,
        service_type,
        from_dt,
):
    yateam = await _fill_ya_team()
    external_refs = [emp['external_ref'] for emp in yateam.employees.values()]

    spend_money(
        'yataxi_team',
        'yataxi_team/dmkurilov',
        '570.0000',
        'RUB',
        service_type,
        from_dt,
    )

    response = await request_find_spendings(
        external_refs, service_type, CURRENCY, from_dt,
    )
    assert response.status_code == 200
    assert response.json() == {
        'employees': [
            {
                'external_ref': 'yataxi_team/dmkurilov',
                'suspended': False,
                'spent': '570.0000',
            },
            {
                'external_ref': 'yataxi_team/rkarlash',
                'suspended': False,
                'spent': '0.0000',
            },
        ],
    }


@pytest.mark.parametrize(
    ['service_type', 'from_dt'],
    [
        pytest.param('eats/rus', DEFAULT_FROM_DT),
        pytest.param('eats', DEFAULT_FROM_DT),
        pytest.param('taxi', DEFAULT_FROM_DT),
    ],
)
@pytest.mark.now('2019-11-22T00:00:00Z')
async def test_v2_employees_spendings(
        # pylint: disable=W0621
        request_v2_find_spendings,
        _fill_ya_team,
        spend_money,
        service_type,
        from_dt,
):
    yateam = await _fill_ya_team()
    external_refs = [emp['external_ref'] for emp in yateam.employees.values()]

    spend_money(
        'yataxi_team',
        'yataxi_team/dmkurilov',
        '570.0000',
        'RUB',
        service_type,
        from_dt,
    )

    response = await request_v2_find_spendings(
        'yataxi_team', external_refs, service_type, CURRENCY, from_dt,
    )
    assert response.status_code == 200
    assert response.json() == {
        'employees': [
            {'external_ref': 'yataxi_team/dmkurilov', 'spent': '570.0000'},
            {'external_ref': 'yataxi_team/rkarlash', 'spent': '0.0000'},
        ],
    }


@pytest.fixture
def request_find_spendings(taxi_corp_billing, balances_handler):
    async def _wrapper(external_refs, service_type, currency, from_dt):
        body = {
            'employees': [{'external_ref': ref} for ref in external_refs],
            'service_type': service_type,
            'currency': currency,
            'from_dt': from_dt,
        }
        response = await taxi_corp_billing.post(
            '/v1/employees-spendings/find', json=body,
        )
        return response

    return _wrapper


@pytest.fixture
def request_v2_find_spendings(taxi_corp_billing, balances_handler):
    async def _wrapper(
            client_external_ref,
            external_refs,
            service_type,
            currency,
            from_dt,
    ):
        body = {
            'client_external_ref': client_external_ref,
            'employees': [{'external_ref': ref} for ref in external_refs],
            'service_type': service_type,
            'currency': currency,
            'from_dt': from_dt,
        }
        response = await taxi_corp_billing.post(
            '/v2/employees-spendings/find', json=body,
        )
        return response

    return _wrapper


@pytest.fixture
def _fill_ya_team(
        request_create_employee,
        request_update_employee,
        request_find_employees,
        add_client_with_services,
        load_json,
):
    async def _wrapper():
        client = load_json('client_with_services_ya_taxi_team.json')
        await add_client_with_services(client)

        employees_dict = {}
        employees = load_json('employees_ya_taxi_team.json')
        for obj in employees:
            response = await request_create_employee(obj)
            assert response.status_code == 200

            obj['revision'] = response.json()['revision']
            response = await request_update_employee(obj)
            assert response.status_code == 200

            employee = response.json()
            employees_dict[employee['external_ref']] = employee

        @dataclasses.dataclass
        class Result:
            client: dict
            employees: dict

        return Result(client, employees_dict)

    return _wrapper
