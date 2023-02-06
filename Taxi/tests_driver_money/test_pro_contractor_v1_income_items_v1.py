from unittest import mock
import pytest

URL = '/pro-contractor/v1/income/items/search/v1'
NOW = '2022-06-01T00:00:00+03'


@pytest.fixture(name='do_post')
def _do_post(taxi_driver_money, load_json, mockserver):
    async def _impl(fta_response, expected):
        @mockserver.json_handler(
            '/fleet-transactions-api/internal/pro-platform/income/events/search/v1',
        )
        def _mock_fta(request):
            return load_json(fta_response)

        response = await taxi_driver_money.post(
            URL,
            json={'tz': 'Europe/Moscow', 'group_by': 'day'},
            headers={
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': 'park_id_0',
                'X-YaTaxi-Driver-Profile-Id': 'driver',
            },
        )

        assert response.status_code == 200
        assert response.json() == load_json(expected)
        return response.json()

    return _impl


@pytest.fixture(name='do_get')
def _do_get(taxi_driver_money, load_json, mockserver):
    async def _impl(cursor, fta_response, expected):
        @mockserver.json_handler(
            '/fleet-transactions-api/internal/pro-platform/income/events/search/v1',
        )
        def _mock_fta(request):
            return load_json(fta_response)

        response = await taxi_driver_money.get(
            URL,
            params={'tz': 'Europe/Moscow', 'cursor': cursor},
            headers={
                'Accept-Language': 'ru',
                'X-Request-Application-Version': '8.90',
                'X-YaTaxi-Park-Id': 'park_id_0',
                'X-YaTaxi-Driver-Profile-Id': 'driver',
            },
        )

        assert response.status_code == 200
        assert response.json() == load_json(expected)
        return response.json()

    return _impl


@pytest.mark.now(NOW)
async def test_items_search_chain(do_post, do_get):

    page1 = await do_post('fta_response_1.json', 'expected_response_1.json')
    assert 'cursor' in page1
    page2 = await do_get(
        page1['cursor'], 'fta_response_2.json', 'expected_response_2.json',
    )
    assert 'cursor' in page2
    page3 = await do_get(
        page2['cursor'], 'fta_response_3.json', 'expected_response_3.json',
    )
    assert 'cursor' not in page3
