import pytest

TRANSLATIONS = {
    'sites': {'ru': 'Сайты'},
    'partner': {'ru': 'Партнеры'},
    'CommercialHiringType.owner': {'ru': 'частник'},
    'CommercialHiringType.rent': {'ru': 'арендник'},
}
SETTINGS = [
    {'type_code': 'sites', 'tanker_code': 'sites'},
    {'type_code': 'partner', 'tanker_code': 'partner'},
]


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_simple(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={},
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 3},
        'summaries': stub['result'],
    }


@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_park_not_exist(web_app_client, headers, load_json):
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '123'},
        json={},
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 0},
        'summaries': [],
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_limit(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'limit': 2},
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 2, 'offset': 0, 'total': 3},
        'summaries': stub['result'][:2],
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_limit_and_page(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'limit': 2, 'offset': 2},
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 2, 'offset': 2, 'total': 3},
        'summaries': stub['result'][2:],
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_driver_type(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'query': {'driver_type': 'rent'}},
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 1},
        'summaries': [stub['result'][1]],
    }


@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_acquisition_source(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'query': {'acquisition_source': 'partner'}},
    )
    result = [stub['result'][0], stub['result'][2]]
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 2},
        'summaries': result,
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
async def test_acquisition_source_invalid(web_app_client, headers, load_json):
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'query': {'acquisition_source': 'parter'}},
    )
    assert response.status == 400
    assert await response.json() == {
        'code': 'invalid_acquisition_type',
        'message': 'acquisition type does not exist',
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_date_from(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={
            'query': {'date_from': {'from': '2020-02-01', 'to': '2021-02-10'}},
        },
    )
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 2},
        'summaries': stub['result'][1:],
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_sort_driver_type(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'sort': {'field': 'driver_type', 'direction': 'asc'}},
    )
    result = [stub['result'][2], stub['result'][0], stub['result'][1]]
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 3},
        'summaries': result,
    }


@pytest.mark.config(FLEET_REPORTS_COMMERCIAL_HIRING_TYPES=SETTINGS)
@pytest.mark.translations(fleet_enums=TRANSLATIONS)
@pytest.mark.pgsql(
    'fleet_reports', files=['commercial_hiring_summary_data.sql'],
)
async def test_sort_acquisition_type(web_app_client, headers, load_json):
    stub = load_json('success.json')
    response = await web_app_client.post(
        '/reports-api/v1/summary/commercial-hiring/list',
        headers={**headers, 'X-Park-Id': '7ad36bc7560449998acbe2c57a75c293'},
        json={'sort': {'field': 'acquisition_source', 'direction': 'asc'}},
    )
    result = [stub['result'][2], stub['result'][0], stub['result'][1]]
    assert response.status == 200
    assert await response.json() == {
        'pagination': {'limit': 25, 'offset': 0, 'total': 3},
        'summaries': result,
    }
