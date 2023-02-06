import pytest

PARK_ID = 'PARK-ID-01'
PARK_ID_03 = 'PARK-ID-03'
PARK_ID_INACTIVE = 'PARK-ID-INACTIVE'
AUTH_HEADERS = {
    'X-Park-Id': PARK_ID,
    'X-Yandex-UID': '999',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Idempotency-Token': 'TOKEN_01',
    'Accept-Language': 'ru',
}


def _make_headers(park_id, **kwargs):
    return {**AUTH_HEADERS, 'X-Park-Id': park_id}


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve(taxi_fleet_traffic_fines, load_json, mock_api):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01'], fines['FINE_02']],
        'total': {'count': 2, 'sum': '800'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_no_park_car(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers(PARK_ID_03),
        json={'query': {}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_04'], fines['FINE_03']],
        'total': {'count': 2, 'sum': '3500'},
    }


async def test_fines_retrieve_no_discount(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers(PARK_ID_03),
        json={'query': {}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    fines_result = [fines['FINE_04'], fines['FINE_03']]
    for fine in fines_result:
        fine['fine'].pop('discount', None)
    assert response.json() == {
        'fines': fines_result,
        'total': {'count': 2, 'sum': '3500'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_limit(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {}, 'limit': 1},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'cursor': (
            'eyJsb2FkZWRfYXQiOiIyMDIyLTAxLTAxVDAwOjAwOjAwKzAwOjAw'
            'IiwidWluIjoiRklORV9VSU5fMDEiLCJtYXhfbG9hZGVkX2F0Ijoi'
            'MjAyMi0wMS0wMVQwMDowMDowMCswMDowMCJ9'
        ),
        'total': {'count': 2, 'sum': '800'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_cursor(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={
            'query': {},
            'cursor': (
                'eyJsb2FkZWRfYXQiOiIyMDIyLTAxLTAxVDAwOjAwOjAwKzAwOjAw'
                'IiwidWluIjoiRklORV9VSU5fMDEiLCJtYXhfbG9hZGVkX2F0Ijoi'
                'MjAyMi0wMS0wMVQwMDowMDowMCswMDowMCJ9'
            ),
        },
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_02']],
        'total': {'count': 2, 'sum': '800'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_status(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'status': 'issued'}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_02']],
        'total': {'count': 1, 'sum': '500'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_to(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'time_range': {'to': '2021-12-31T00:00:00+00:00'}}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_02']],
        'total': {'count': 1, 'sum': '500'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_from(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'time_range': {'from': '2022-01-01T00:00:00+00:00'}}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'total': {'count': 1, 'sum': '300'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_car(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'car_id': 'CAR_ID_01'}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'total': {'count': 1, 'sum': '300'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_was_loaded(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'was_loaded_bank_client': True}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'total': {'count': 1, 'sum': '300'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_contractor_id(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'contractor_id': 'CONTRACTOR-ID-01'}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'total': {'count': 1, 'sum': '300'},
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fines_retrieve_fine_uin(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'fine_uin': 'FINE_UIN_01'}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'fines': [fines['FINE_01']],
        'total': {'count': 1, 'sum': '300'},
    }


async def test_fines_retrieve_empty(taxi_fleet_traffic_fines, mock_api):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {'car_id': 'CAR_ID_99'}},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'fines': [], 'total': {'count': 0, 'sum': '0'}}


async def test_fines_invalid_cursor(taxi_fleet_traffic_fines, load_json):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=AUTH_HEADERS,
        json={'query': {}, 'cursor': 'aaa'},
    )
    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'invalid_cursor'


async def test_fines_retrieve_inactive_park(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers(PARK_ID_INACTIVE),
        json={'query': {}},
    )
    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'park_fines_retrieving_inactive'


async def test_park_bank_account_get(taxi_fleet_traffic_fines, mock_api):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/bank-account', headers=AUTH_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'bank_account': {
            'BIK': 'BIK_01',
            'INN': 'TIN_01',
            'KPP': 'KPP_01',
            'account_number': 'ACC_01',
            'bank': 'BANK_01',
            'corr_account': 'CORR_01',
            'payment_name': 'NAME_01',
        },
    }


async def test_park_bank_account_get_billing(
        mockserver,
        taxi_fleet_traffic_fines,
        load_json,
        mock_fleet_parks_list,
        mock_api,
):
    @mockserver.json_handler(
        '/parks-replica/v1/parks/billing_client_id/retrieve',
    )
    def _v1_parks_billing_client_id_retrieve(request):
        assert request.query == {
            'consumer': 'fleet-traffic-fines',
            'park_id': '100500',
        }
        return {'billing_client_id': '187701087'}

    @mockserver.json_handler('/billing-replication/contract/')
    def _contract(request):
        stub = load_json('billing_replication_contract.json')
        assert request.query == stub['request']
        return stub['response']

    @mockserver.json_handler('/billing-replication/person/')
    def _person(request):
        stub = load_json('billing_replication_person.json')
        assert request.query == stub['request']
        return stub['response']

    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/bank-account',
        headers=_make_headers('PARK-ID-04'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'bank_account': {
            'BIK': '000',
            'INN': '434546334788',
            'KPP': 'kpp_example',
            'account_number': 'account_example',
            'bank': 'vtb',
            'corr_account': 'corraccount_example',
            'payment_name': 'Абрамов Сергей Николаевич',
        },
    }


@pytest.mark.now('2021-12-31T12:00:00.000000+03:00')
async def test_fine_get(taxi_fleet_traffic_fines, load_json, mock_api):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/fines',
        headers=AUTH_HEADERS,
        params={'uin': 'FINE_UIN_01'},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    assert response.json() == {'fine': fines['FINE_01']}


async def test_fine_get_404(taxi_fleet_traffic_fines, mock_api):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/fines',
        headers=AUTH_HEADERS,
        params={'uin': 'FINE_UIN_99'},
    )
    assert response.status_code == 404, response.text


async def test_report_request(
        taxi_fleet_traffic_fines, mock_api, pg_dump, stq,
):
    pg_initial = pg_dump()

    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/report/bank-client/request',
        headers=AUTH_HEADERS,
        json={
            'query': {},
            'bank_account': {
                'payment_name': 'NAME_02',
                'INN': 'TIN_02',
                'KPP': 'KPP_02',
                'bank': 'BANK_02',
                'BIK': 'BIK_02',
                'account_number': 'ACC_02',
                'corr_account': 'CORR_02',
            },
        },
    )
    assert response.status_code == 204, response.text

    assert stq.fleet_traffic_fines_bank_client_report.times_called == 1
    stq_call = stq.fleet_traffic_fines_bank_client_report.next_call()['kwargs']
    stq_call.pop('log_extra')
    assert stq_call == {
        'initial_payment_number': 1,
        'park_id': PARK_ID,
        'query': {},
    }

    assert (
        mock_api['fleet-reports-storage'][
            '/internal/user/v1/operations/create'
        ]
        .next_call()['request']
        .json
        == {
            'client_type': 'yandex_user',
            'file_name': '1c_to_kl.txt',
            'id': 'TOKEN_01',
            'locale': 'ru',
            'name': 'fines_bank_client',
            'park_id': PARK_ID,
            'passport_uid': '999',
        }
    )

    assert pg_dump() == {
        **pg_initial,
        'park_bank_accounts': {
            **pg_initial['park_bank_accounts'],
            PARK_ID: (
                'NAME_02',
                'TIN_PD_02',
                'KPP_PD_02',
                'BANK_02',
                'BIK_02',
                'ACC_PD_02',
                'CORR_02',
            ),
        },
    }


async def test_report_request_400(taxi_fleet_traffic_fines, stq):

    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/report/bank-client/request',
        headers=AUTH_HEADERS,
        json={
            'query': {},
            'bank_account': {
                'payment_name': 'NAME_02',
                'INN': 'TIN_02',
                'KPP': 'KPP_02',
                'bank': 'BANK_02',
                'BIK': 'BIK_02',
                'account_number': 'ACC_02',
                'corr_account': 'CORR_02',
            },
            'cursor': 'aaa',
        },
    )
    assert response.status_code == 400, response.text


async def test_photo_get(taxi_fleet_traffic_fines, mock_api):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/fines/photo',
        headers=AUTH_HEADERS,
        params={'uin': 'FINE_UIN_01', 'number': 1},
    )
    assert response.status_code == 200, response.text
    assert response.json() == 'BINARY_FOTO'


@pytest.mark.parametrize(
    'uin,number', [('FINE_UIN_01', 2), ('FINE_UIN_99', 1)],
)
async def test_photo_get_404(taxi_fleet_traffic_fines, mock_api, uin, number):
    response = await taxi_fleet_traffic_fines.get(
        'fleet/traffic-fines/v1/fines/photo',
        headers=AUTH_HEADERS,
        params={'uin': 1, 'number': 2},
    )
    assert response.status_code == 404, response.text


async def test_fines_retrieve_overdue(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/fines/retrieve',
        headers=_make_headers('PARK-ID-10'),
        json={'query': {}},
    )
    fines = load_json('fines.json')
    assert response.status_code == 200, response.text
    fine = fines['FINE_06']
    fine['fine'].pop('discount', None)
    assert response.json() == {
        'fines': [fine],
        'total': {'count': 1, 'sum': '500'},
    }
