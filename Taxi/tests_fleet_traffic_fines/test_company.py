PARK_ID = 'PARK-ID-01'
PARK_ID_03 = 'PARK-ID-03'
PARK_ID_INACTIVE = 'PARK-ID-INACTIVE'
AUTH_HEADERS = {
    'X-Park-Id': PARK_ID,
    'X-Yandex-UID': '999',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Idempotency-Token': 'TOKEN_01',
}


def _make_headers(park_id, **kwargs):
    return {**AUTH_HEADERS, 'X-Park-Id': park_id}


async def test_company_change_company_activity(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'id': '4',
                'company': {
                    'title': 'New title',
                    'requisites': {'inn': '001234567890', 'kpp': ''},
                    'is_active': False,
                },
            },
        },
    )
    assert response.status_code == 204, response.text


async def test_company_change_company_activity_new_inn(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'id': '4',
                'company': {
                    'title': 'Title',
                    'requisites': {'inn': '123456789034', 'kpp': ''},
                    'is_active': False,
                },
            },
        },
    )
    assert response.status_code == 204, response.text


async def test_company_change_company_activity_new_inn_already_exist(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'id': '4',
                'company': {
                    'title': 'Title',
                    'requisites': {'inn': '123456789000', 'kpp': ''},
                    'is_active': False,
                },
            },
        },
    )
    assert response.status_code == 400, response.text


async def test_company_change_company_activity_new_kpp(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'id': '4',
                'company': {
                    'title': 'Title',
                    'requisites': {'inn': '001234567890', 'kpp': '123123123'},
                    'is_active': False,
                },
            },
        },
    )
    assert response.status_code == 204, response.text


async def test_company_change_company_not_exist(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.put(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'id': '9',
                'company': {
                    'title': 'New title',
                    'requisites': {'inn': '9999999999', 'kpp': ''},
                    'is_active': True,
                },
            },
        },
    )
    assert response.status_code == 404, response.text


async def test_company_add(taxi_fleet_traffic_fines, load_json, mock_api):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company',
        headers=AUTH_HEADERS,
        json={
            'company': {
                'requisites': {'inn': '123123123123', 'kpp': '123123123'},
                'title': 'Test',
                'is_active': True,
            },
        },
    )
    assert response.status_code == 204, response.text


async def test_company_add_already_exist(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'requisites': {'inn': '001234567890', 'kpp': '123123123'},
                'title': 'Test',
                'is_active': True,
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'company_already_exist'


async def test_company_add_deleted(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'requisites': {'inn': '123456789000', 'kpp': '123123123'},
                'title': 'Test',
                'is_active': True,
            },
        },
    )
    assert response.status_code == 204, response.text


async def test_company_add_1c_error(
        taxi_fleet_traffic_fines, mockserver, load_json, mock_api,
):
    @mockserver.json_handler('/fines-1c/Company/v1/Add')
    async def _mock_1c(request):
        return [{'error': True, 'errorMessage': 'error'}]

    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company',
        headers=AUTH_HEADERS,
        json={
            'company': {
                'requisites': {'inn': '123123123123', 'kpp': '123123123'},
                'title': 'Test',
                'is_active': True,
            },
        },
    )
    assert response.status_code == 500, response.text


async def test_company_add_inactive(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={
            'company': {
                'requisites': {'inn': '001234567890', 'kpp': '123123123'},
                'title': 'Test',
                'is_active': False,
            },
        },
    )
    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'company_already_exist'


async def test_company_delete(taxi_fleet_traffic_fines, load_json, mock_api):
    response = await taxi_fleet_traffic_fines.delete(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={'id': '4'},
    )
    assert response.status_code == 204, response.text


async def test_company_delete_already_deleted(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.delete(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-03'),
        json={'id': '6'},
    )
    assert response.status_code == 204, response.text


async def test_company_delete_other_park_has_subscription(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.delete(
        'fleet/traffic-fines/v1/company',
        headers=_make_headers('PARK-ID-06'),
        json={'id': '3'},
    )
    assert response.status_code == 204, response.text


async def test_company_delete_not_exist(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.delete(
        'fleet/traffic-fines/v1/company',
        headers=AUTH_HEADERS,
        json={'id': '9999999999'},
    )
    assert response.status_code == 404, response.text


async def test_list_company(taxi_fleet_traffic_fines, load_json, mock_api):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company/list',
        headers=_make_headers('PARK-ID-06'),
        json={},
    )
    companies = load_json('companies.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'companies': [
            companies['COMPANY_1'],
            companies['COMPANY_2'],
            companies['COMPANY_3'],
        ],
    }


async def test_list_company_active(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company/list',
        headers=_make_headers('PARK-ID-06'),
        json={'is_active': True},
    )
    companies = load_json('companies.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'companies': [companies['COMPANY_1'], companies['COMPANY_2']],
    }


async def test_list_company_inactive(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company/list',
        headers=_make_headers('PARK-ID-06'),
        json={'is_active': False},
    )
    companies = load_json('companies.json')
    assert response.status_code == 200, response.text
    assert response.json() == {'companies': [companies['COMPANY_3']]}


async def test_list_company_no_records(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company/list',
        headers=_make_headers('PARK_NO_COMPANY'),
        json={},
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'companies': []}


async def test_list_company_with_company_part_name(
        taxi_fleet_traffic_fines, load_json, mock_api,
):
    response = await taxi_fleet_traffic_fines.post(
        'fleet/traffic-fines/v1/company/list',
        headers=_make_headers('PARK-ID-06'),
        json={'company_title': 'oMe N'},
    )
    companies = load_json('companies.json')
    assert response.status_code == 200, response.text
    assert response.json() == {
        'companies': [companies['COMPANY_1'], companies['COMPANY_2']],
    }
