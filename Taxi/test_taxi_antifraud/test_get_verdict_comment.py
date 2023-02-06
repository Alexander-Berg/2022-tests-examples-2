import json
from typing import Dict
from typing import List

import pytest


async def check_response_code(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
):
    response = await web_app_client.get(
        '/v1/get_verdict_comment', params=request_params,
    )

    assert response.status == expected_response_code


async def check_response_code_and_content(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
        expected_response_content: List[Dict[str, str]],
):
    response = await web_app_client.get(
        '/v1/get_verdict_comment', params=request_params,
    )

    assert response.status == expected_response_code

    assert await response.json() == expected_response_content


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [
        ({'verdict_id': ''}, 404),
        ({'verdict_id': 'bad-id'}, 404),
        ({'verdict_id': '4e593f7f9a7c49a672e6fbf8'}, 404),
    ],
)
async def test_verdict_not_found(
        web_app_client, request_params, expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize('request_params,expected_response_code', [({}, 400)])
async def test_bad_request_no_args(
        web_app_client, request_params, expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'verdict_id': '5e592f7f9a6c49d671e6fbf9'},
            200,
            {'text': 'He\'s good'},
        ),
    ],
)
async def test_get_verdict_comment_200_static(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
):
    await check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


async def add_new_verdict(web_app_client, add_verdict_request_params):
    response = await web_app_client.post(
        '/v1/add_subvention_refund_verdict',
        data=json.dumps({**add_verdict_request_params, 'billing_id': '1'}),
    )

    assert response.status == 200

    response = await web_app_client.get(
        '/v1/get_subventions',
        params={'limit': 100, 'order_id': 'first_billing_id_order'},
    )

    assert response.status == 200

    response_as_dict = await response.json()

    assert len(response_as_dict) == 1

    verdicts = response_as_dict[0]['verdicts']

    assert verdicts

    return verdicts[-1]['id']


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {
                'user_login': 'vasya',
                'type': 'discard',
                'comment': 'Too bad',
                'ticket': 'TRACKER-1231',
            },
            200,
            {'text': 'Too bad'},
        ),
    ],
)
async def test_get_verdict_comment_200_dynamic(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
):
    verdict_id = await add_new_verdict(web_app_client, request_params)

    await check_response_code_and_content(
        web_app_client,
        {'verdict_id': verdict_id},
        expected_response_code,
        expected_response_content,
    )
