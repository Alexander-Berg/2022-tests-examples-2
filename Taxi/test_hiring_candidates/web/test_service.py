import pytest

from hiring_candidates.generated.cron import run_cron
from test_hiring_candidates import conftest


@pytest.fixture
def taxi_hiring_candidates_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_hiring_candidates_mocks')
@conftest.main_configuration
async def test_ping(taxi_hiring_candidates_web, load_json, eda_core_mock):
    id_ = 'df26389528dd429a903d59f731ccf6b4'
    url = '/eda_core/api/v1/general-information/couriers/catalog/search'
    eda_core_mock[url][id_] = load_json('eda_core.json')
    response = await taxi_hiring_candidates_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.parametrize(
    'driver_license, city, expected_code',
    [
        ('12313123', '\u041c\u043e\u0441\u043a\u0432\u0430', 200),
        ('12313123', '\u041c\u043e\u0441\u043a\u0432', 404),
    ],
)
@pytest.mark.usefixtures('mock_yt_fetch_table', 'mock_yt_search')
@conftest.main_configuration
async def test_get_driver_for_city(
        mock_data_markup_perform,
        driver_license,
        city,
        expected_code,
        web_app_client,
):
    await run_cron.main(
        ['hiring_candidates.crontasks.fetch_driver_communications', '-t', '0'],
    )
    response = await web_app_client.get(
        '/v1/driver-for-city',
        params={'driver_license': driver_license, 'city': city},
    )
    assert response.status == expected_code
