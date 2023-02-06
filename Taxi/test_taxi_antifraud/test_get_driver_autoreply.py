from typing import Dict
from typing import List

import pytest

from taxi.clients import personal


async def check_response_code(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
):
    response = await web_app_client.get(
        '/v1/get_autoreply_status_for_driver', params=request_params,
    )

    assert response.status == expected_response_code


async def check_response_code_and_content(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
        expected_response_content: List[Dict[str, str]],
):
    response = await web_app_client.get(
        '/v1/get_autoreply_status_for_driver', params=request_params,
    )

    assert response.status == expected_response_code

    assert await response.json() == expected_response_content


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'driver_license_personal_id': '1111111111', 'date': '2019-04-08'},
            200,
            {'status': 'selforder'},
        ),
        (
            {'driver_license_personal_id': '1111111111', 'date': '2019-06-09'},
            200,
            {'status': 'sgovor'},
        ),
        (
            {'driver_license_personal_id': '2222222222', 'date': '2019-04-09'},
            200,
            {'status': 'selforder'},
        ),
        (
            {'driver_license_personal_id': '3333333333', 'date': '2019-05-11'},
            200,
            {'status': 'unknown'},
        ),
        (
            {'driver_license_personal_id': '4444444444', 'date': '2019-04-08'},
            200,
            {'status': 'unknown'},
        ),
        (
            {'driver_license_personal_id': '5555555555', 'date': '2019-04-30'},
            200,
            {'status': 'selforder'},
        ),
        (
            {'driver_license_personal_id': '5555555555', 'date': '2019-05-01'},
            200,
            {'status': 'sgovor'},
        ),
        (
            {'driver_license_personal_id': '5555555555', 'date': '2019-05-31'},
            200,
            {'status': 'unknown'},
        ),
        (
            {'driver_license_personal_id': '5555555555', 'date': '2019-06-01'},
            200,
            {'status': 'unknown'},
        ),
        (
            {'driver_license_personal_id': '5555555555', 'date': '2020-06-01'},
            200,
            {'status': 'unknown'},
        ),
        (
            {'driver_license_personal_id': '6666666666', 'date': '2019-05-01'},
            200,
            {'status': 'selforder'},
        ),
        (
            {'driver_license_personal_id': '7777777777', 'date': '2019-05-01'},
            200,
            {'status': 'sgovor'},
        ),
    ],
)
async def test_get_autoreply_status_for_driver_success(
        web_app_client,
        patch,
        request_params,
        expected_response_code,
        expected_response_content,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'license': request_params['driver_license_personal_id']}

    await check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [
        ({}, 400),
        ({'driver_license_personal_id': '1111111111'}, 400),
        ({'date': '2019-04-09'}, 400),
        (
            {'driver_license_personal_id': '3333333333', 'date': 'skdjfhskd'},
            400,
        ),
    ],
)
async def test_get_autoreply_status_for_driver_bad_response(
        web_app_client, request_params, expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {
                'driver_license_personal_id': '1111111111',
                'date': '2019-04-08',
                'order_id': 'df02d7bfe30000000000dd98d555f946',
            },
            200,
            {'status': 'selforder'},
        ),
    ],
)
async def test_get_autoreply_status_for_driver_with_order_id(
        web_app_client,
        patch,
        request_params,
        expected_response_code,
        expected_response_content,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        return {'license': request_params['driver_license_personal_id']}

    await check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {
                'driver_license_personal_id': '1111111111',
                'date': '2019-04-08',
                'order_id': 'df02d7bfe30000000000dd98d555f946',
            },
            200,
            {'status': 'unknown'},
        ),
    ],
)
async def test_get_autoreply_status_for_driver_personal_not_found(
        web_app_client,
        patch,
        request_params,
        expected_response_code,
        expected_response_content,
):
    @patch('taxi.clients.personal.PersonalApiClient.retrieve')
    async def _retrieve(*args, **kwargs):
        raise personal.NotFoundError

    await check_response_code_and_content(
        web_app_client,
        request_params,
        expected_response_code,
        expected_response_content,
    )
