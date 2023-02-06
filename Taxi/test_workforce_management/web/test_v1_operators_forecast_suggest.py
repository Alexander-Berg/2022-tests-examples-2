import pytest

from test_workforce_management.web import util as test_util


URI = 'v1/operators/forecast/suggest'
START_DATE = '27-02-2020'
HEADERS = {'X-WFM-Domain': 'taxi'}


@pytest.mark.parametrize(
    'tst_request, expected_status, expected_res',
    [
        ({}, 400, []),
        (
            {
                'entity_target_from': '2020-02-27T04:00:00+03:00',
                'entity_target_to': '2020-02-27T06:00:00+03:00',
                'skill': 'not_a_skill',
            },
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'id': 1,
                    'name': 'Forecast 0',
                    'skill': 'not_a_skill',
                },
            ],
        ),
        (
            {
                'entity_target_from': '2020-02-27T03:00:00+03:00',
                'entity_target_to': '2020-02-27T12:00:00+03:00',
                'skill': 'not_a_skill',
            },
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'id': 1,
                    'name': 'Forecast 0',
                    'skill': 'not_a_skill',
                },
            ],
        ),
        (
            {
                'entity_target_from': '2020-02-27T02:00:00+03:00',
                'entity_target_to': '2020-02-27T06:00:00+03:00',
                'skill': 'not_a_skill',
            },
            200,
            [
                {
                    'entity_target': '2020-02-27T03:00:00+03:00',
                    'id': 1,
                    'name': 'Forecast 0',
                    'skill': 'not_a_skill',
                },
            ],
        ),
        (
            {
                'entity_target_from': '2020-02-28T05:00:00+03:00',
                'entity_target_to': '2020-02-28T06:00:00+03:00',
                'skill': 'skill',
            },
            200,
            [
                {
                    'entity_target': '2020-02-28T03:00:00+03:00',
                    'id': 2,
                    'name': 'Forecast 1',
                    'skill': 'skill',
                },
            ],
        ),
        (
            {
                'name': 'cast 2',
                'entity_target_from': '2020-02-28T03:00:00+03:00',
                'entity_target_to': '2020-05-29T03:00:00+03:00',
                'skill': 'skill',
            },
            200,
            [],
        ),
        (
            {
                'skill': 'not_a_skill_2',
                'entity_target_from': '2020-02-28T03:00:00+03:00',
                'entity_target_to': '2020-02-29T03:00:00+03:00',
            },
            200,
            [],
        ),
    ],
)
async def test_forecast_suggest_base(
        taxi_workforce_management_web,
        web_context,
        fill_forecast_values,
        tst_request,
        expected_status,
        expected_res,
):
    await fill_forecast_values(5)
    res = await taxi_workforce_management_web.post(
        URI, json=tst_request, headers=HEADERS,
    )
    assert res.status == expected_status

    if expected_status > 200:
        return
    data = await res.json()

    assert test_util.exclude_revision(data['forecasts']) == expected_res
