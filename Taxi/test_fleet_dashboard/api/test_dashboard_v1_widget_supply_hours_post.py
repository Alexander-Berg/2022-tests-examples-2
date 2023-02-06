import aiohttp.web
import pytest

ENDPOINT = '/dashboard/v1/widget/supply-hours'

PARK_ID = '7ad36bc7560449998acbe2c57a75c293'


@pytest.mark.parametrize(
    ['date_from', 'date_to', 'supply', 'expected', 'aggregate_by'],
    [
        pytest.param(
            '2021-11-30T00:00:00+03:00',
            '2021-11-30T06:00:00+03:00',
            'supply_hours.json',
            'expected_hours.json',
            'hours',
            id='hours',
        ),
        pytest.param(
            '2021-11-28T03:00:00+03:00',
            '2021-11-30T03:00:00+03:00',
            'supply_days.json',
            'expected_days.json',
            'days',
            id='days',
        ),
    ],
)
async def test_success(
        web_app_client,
        headers,
        mock_driver_supply_hours,
        load_json,
        date_from,
        date_to,
        supply,
        expected,
        aggregate_by,
):
    @mock_driver_supply_hours('/v1/parks/supply/retrieve/all-days')
    async def _supply_hours_all_days(request):
        assert request.json == {
            'query': {
                'park': {'id': PARK_ID},
                'supply': {
                    'aggregate_by': aggregate_by,
                    'period': {'from': date_from, 'to': date_to},
                },
            },
        }
        return aiohttp.web.json_response(load_json(supply))

    response = await web_app_client.post(
        ENDPOINT,
        headers=headers,
        json={'date_from': date_from, 'date_to': date_to},
    )

    assert response.status == 200

    data = await response.json()
    assert data == load_json(expected)
