from dateutil import parser
import pytest

from eats_catalog import storage


@pytest.mark.now('2021-03-17T16:51:00+00:00')
@pytest.mark.parametrize(
    'x_app_version',
    [
        pytest.param('0.0.0'),
        pytest.param('1.2.3'),
        pytest.param('1.2'),
        pytest.param('1.2-dev'),
        pytest.param('23.22.1211-stable'),
        pytest.param('hello world'),
        pytest.param(''),
        pytest.param(None),
    ],
)
async def test_x_app_version(
        taxi_eats_catalog, eats_catalog_storage, x_app_version,
):
    """
    EDACAT-703: тестирует, что при передаче навалидного значения в заголовке
    x-app-version ручка по-прежнему отдает код ответа 200, а не 400.
    """

    eats_catalog_storage.add_place(storage.Place())
    eats_catalog_storage.add_zone(
        storage.Zone(
            working_intervals=[
                storage.WorkingInterval(
                    start=parser.parse('2021-03-17T10:00:00+00:00'),
                    end=parser.parse('2021-03-17T18:41:00+00:00'),
                ),
            ],
        ),
    )

    headers = {'x-device-id': 'test_simple', 'x-platform': 'desktop_web'}
    if x_app_version is not None:
        headers['x-app-version'] = x_app_version

    response = await taxi_eats_catalog.get(
        '/eats-catalog/v1/slug/coffee_boy_novodmitrovskaya_2k6',
        params={'latitude': 55.802998, 'longitude': 37.591503},
        headers=headers,
    )

    assert response.status_code == 200
