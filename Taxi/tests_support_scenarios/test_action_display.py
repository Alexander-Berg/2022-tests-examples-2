import json

import pytest


SUPPORT_SCENARIOS_KEYSET = {'text1': {'ru': 'текст'}}


@pytest.mark.translations(support_scenarios=SUPPORT_SCENARIOS_KEYSET)
@pytest.mark.parametrize(
    ['query_params', 'expected_code', 'expected_result'],
    [
        (
            {'action_id': 'action_1', 'locale': 'ru'},
            200,
            {'id': 'action_1', 'text': 'текст'},
        ),
        (
            {'action_id': 'action_11234', 'locale': 'ru'},
            404,
            {'code': 'not_found', 'message': 'Action was not found'},
        ),
    ],
)
async def test_display_action(
        taxi_support_scenarios, query_params, expected_code, expected_result,
):
    response = await taxi_support_scenarios.get(
        'v1/actions/display', params=query_params,
    )
    assert response.status_code == expected_code
    assert json.loads(response.content) == expected_result
