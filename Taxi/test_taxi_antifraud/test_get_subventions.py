from typing import Dict
from typing import List

import pytest

from taxi.clients import personal


@pytest.fixture
def mock_personal(patch):
    @patch('taxi.clients.personal.PersonalApiClient.find')
    async def _find(data_type, driver_license, *args, **kwargs):
        if driver_license == 'nonexistent':
            raise personal.NotFoundError
        return {'id': driver_license + '_pd_id'}


def get_necessary_fields(
        response: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    return [
        {
            'subvention_datetime': subvention['subvention_datetime'],
            'order_id': subvention['order_id'],
            'order_datetime': subvention['order_datetime'],
            'subvention_type': subvention['subvention_type'],
            'billing_id': subvention['billing_id'],
            'antifraud_id': subvention['antifraud_id'],
            'verdicts': subvention['verdicts'],
            'worked_rule': subvention['worked_rule'],
        }
        if 'order_id' in subvention
        else {
            'billing_id': subvention['billing_id'],
            'antifraud_id': subvention['antifraud_id'],
            'subvention_datetime': subvention['subvention_datetime'],
            'subvention_type': subvention['subvention_type'],
        }
        for subvention in response
    ]


async def check_response_code(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
):
    response = await web_app_client.get(
        '/v1/get_subventions', params=request_params,
    )

    assert response.status == expected_response_code


async def check_response_code_and_content(
        web_app_client,
        request_params: Dict[str, str],
        expected_response_code: int,
        expected_response_content: List[Dict[str, str]],
):
    response = await web_app_client.get(
        '/v1/get_subventions', params=request_params,
    )

    assert response.status == expected_response_code

    subventions = get_necessary_fields(await response.json())

    assert subventions == expected_response_content


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'limit': 100, 'driver_license': '1111111111'},
            200,
            [
                {
                    'subvention_datetime': '2020-01-10 15:56:12',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
                    'order_datetime': '2020-01-10T15:52:00.000000+00:00',
                    'subvention_type': 'order',
                    'billing_id': '1',
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba1',
                            'billing_id': '1',
                            'comment': 'Some\nlong\ncomment',
                            'ticket': 'TRACKER-1231',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'created': '2019-01-01T03:00:00+03:00',
                        },
                    ],
                },
                {
                    'billing_id': '6',
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'subvention_datetime': '2020-01-08 15:56:12',
                    'subvention_type': 'daily_guarantee',
                },
                {
                    'subvention_datetime': '2020-01-06 15:56:12',
                    'order_id': '6841e55d0fa8a7b5adceaeb45143f219',
                    'order_datetime': '2020-01-06T15:52:00.000000+00:00',
                    'subvention_type': 'driver_fix',
                    'billing_id': '5',
                    'antifraud_id': 'b29a1cfc9deccb6454deee0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba5',
                            'billing_id': '5',
                            'created': '2019-05-07T03:00:00+03:00',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'comment': 'Some\nanother\nlong\ncomment',
                            'ticket': 'TRACKER-3434',
                        },
                    ],
                },
            ],
        ),
        (
            {'limit': 100, 'driver_license': ' 1111111111\t'},
            200,
            [
                {
                    'subvention_datetime': '2020-01-10 15:56:12',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
                    'order_datetime': '2020-01-10T15:52:00.000000+00:00',
                    'subvention_type': 'order',
                    'billing_id': '1',
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba1',
                            'billing_id': '1',
                            'comment': 'Some\nlong\ncomment',
                            'ticket': 'TRACKER-1231',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'created': '2019-01-01T03:00:00+03:00',
                        },
                    ],
                },
                {
                    'billing_id': '6',
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'subvention_datetime': '2020-01-08 15:56:12',
                    'subvention_type': 'daily_guarantee',
                },
                {
                    'subvention_datetime': '2020-01-06 15:56:12',
                    'order_id': '6841e55d0fa8a7b5adceaeb45143f219',
                    'order_datetime': '2020-01-06T15:52:00.000000+00:00',
                    'subvention_type': 'driver_fix',
                    'billing_id': '5',
                    'antifraud_id': 'b29a1cfc9deccb6454deee0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba5',
                            'billing_id': '5',
                            'created': '2019-05-07T03:00:00+03:00',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'comment': 'Some\nanother\nlong\ncomment',
                            'ticket': 'TRACKER-3434',
                        },
                    ],
                },
            ],
        ),
        (
            {'limit': 100, 'driver_license': '1212121212'},
            200,
            [
                {
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ad',
                    'billing_id': '16',
                    'order_datetime': '2020-01-09T15:52:00.000000+00:00',
                    'order_id': 'same_old_same_old',
                    'subvention_datetime': '2020-02-21 15:56:12',
                    'subvention_type': 'order',
                    'verdicts': [],
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v10'
                    ),
                },
            ],
        ),
    ],
)
async def test_get_subventions_by_license(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'limit': 2, 'driver_license': '1111111111'},
            200,
            [
                {
                    'subvention_datetime': '2020-01-10 15:56:12',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
                    'order_datetime': '2020-01-10T15:52:00.000000+00:00',
                    'subvention_type': 'order',
                    'billing_id': '1',
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba1',
                            'billing_id': '1',
                            'comment': 'Some\nlong\ncomment',
                            'ticket': 'TRACKER-1231',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'created': '2019-01-01T03:00:00+03:00',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_get_subventions_with_limit(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'limit': 1, 'offset': 4, 'driver_license': '1111111111'},
            200,
            [
                {
                    'subvention_datetime': '2020-01-06 15:56:12',
                    'order_id': '6841e55d0fa8a7b5adceaeb45143f219',
                    'order_datetime': '2020-01-06T15:52:00.000000+00:00',
                    'subvention_type': 'driver_fix',
                    'billing_id': '5',
                    'antifraud_id': 'b29a1cfc9deccb6454deee0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba5',
                            'billing_id': '5',
                            'created': '2019-05-07T03:00:00+03:00',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'comment': 'Some\nanother\nlong\ncomment',
                            'ticket': 'TRACKER-3434',
                        },
                    ],
                },
            ],
        ),
    ],
)
async def test_get_subventions_with_limit_and_offset(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {'limit': 100, 'order_id': '0a3d432ddbc9641602facac52da84f5f'},
            200,
            [
                {
                    'subvention_datetime': '2020-01-07 15:56:12',
                    'order_id': '0a3d432ddbc9641602facac52da84f5f',
                    'order_datetime': '2020-01-07T15:52:00.000000+00:00',
                    'subvention_type': 'geo_booking',
                    'billing_id': '4',
                    'antifraud_id': 'b29a1cfc9deccddd54db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba4',
                            'billing_id': '4',
                            'created': '2019-02-03T03:00:00+03:00',
                            'user_login': 'robot-taxi',
                            'type': 'refund',
                            'comment': 'Some\nother\nlong\ncomment',
                            'ticket': 'TRACKER-2345',
                        },
                    ],
                },
            ],
        ),
        (
            {'limit': 100, 'order_id': 'same_old_same_old'},
            200,
            [
                {
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ad',
                    'billing_id': '16',
                    'order_datetime': '2020-01-09T15:52:00.000000+00:00',
                    'order_id': 'same_old_same_old',
                    'subvention_datetime': '2020-02-21 15:56:12',
                    'subvention_type': 'order',
                    'verdicts': [],
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v10'
                    ),
                },
            ],
        ),
    ],
)
async def test_get_subventions_by_order_id(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {
                'limit': 100,
                'driver_license': '1111111111',
                'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
            },
            200,
            [
                {
                    'subvention_datetime': '2020-01-10 15:56:12',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
                    'order_datetime': '2020-01-10T15:52:00.000000+00:00',
                    'subvention_type': 'order',
                    'billing_id': '1',
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba1',
                            'billing_id': '1',
                            'comment': 'Some\nlong\ncomment',
                            'ticket': 'TRACKER-1231',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'created': '2019-01-01T03:00:00+03:00',
                        },
                    ],
                },
                {
                    'billing_id': '6',
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'subvention_datetime': '2020-01-08 15:56:12',
                    'subvention_type': 'daily_guarantee',
                },
            ],
        ),
    ],
)
async def test_get_subventions_by_license_and_order_id(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code,expected_response_content',
    [
        (
            {
                'limit': 100,
                'driver_license': '1111111111',
                'date_from': '2020-01-07',
                'date_to': '2020-01-10',
            },
            200,
            [
                {
                    'subvention_datetime': '2020-01-10 15:56:12',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72be',
                    'order_datetime': '2020-01-10T15:52:00.000000+00:00',
                    'subvention_type': 'order',
                    'billing_id': '1',
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                    'verdicts': [
                        {
                            'id': '5e592f7f9a6c49d671e6fba1',
                            'billing_id': '1',
                            'comment': 'Some\nlong\ncomment',
                            'ticket': 'TRACKER-1231',
                            'user_login': 'robot-taxi',
                            'type': 'discard',
                            'created': '2019-01-01T03:00:00+03:00',
                        },
                    ],
                },
                {
                    'billing_id': '6',
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'subvention_datetime': '2020-01-08 15:56:12',
                    'subvention_type': 'daily_guarantee',
                },
            ],
        ),
        (
            {
                'limit': 100,
                'driver_license': '777777777',
                'date_from': '2020-01-07',
                'date_to': '2020-01-10',
            },
            200,
            [],
        ),
        (
            {
                'limit': 100,
                'driver_license': '777777777',
                'date_from': '2020-02-20',
                'date_to': '2020-02-20',
            },
            200,
            [
                {
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'billing_id': '11',
                    'order_datetime': '2020-01-09T15:52:00.000000+00:00',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72de',
                    'subvention_datetime': '2020-02-20 15:56:12',
                    'subvention_type': 'order',
                    'verdicts': [],
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                },
            ],
        ),
        (
            {
                'limit': 100,
                'driver_license': '8888888888',
                'date_from': '2020-01-01',
                'date_to': '2020-03-10',
            },
            200,
            [
                {
                    'antifraud_id': 'b29a1cfc9deaaa6454db7d0800efc3ae',
                    'billing_id': '12',
                    'order_datetime': '2020-01-09T15:52:00.000000+00:00',
                    'order_id': 'f1d937ab7dd71c0c96bf1a84376f72de',
                    'subvention_datetime': '2020-02-20 15:56:12',
                    'subvention_type': 'order',
                    'verdicts': [],
                    'worked_rule': (
                        'black_license_custom_datamarts_ban_rule_v9'
                    ),
                },
                {
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'billing_id': '13',
                    'subvention_datetime': '2020-01-06 15:56:12',
                    'subvention_type': 'daily_guarantee',
                },
            ],
        ),
        (
            {
                'limit': 100,
                'driver_license': '9999999999',
                'date_from': '2020-01-07',
                'date_to': '2020-01-07',
            },
            200,
            [
                {
                    'antifraud_id': 'b29a1cfc000ccb6454db7d0800efc3ae',
                    'billing_id': '14',
                    'subvention_datetime': '2020-01-06 22:56:12',
                    'subvention_type': 'daily_guarantee',
                },
            ],
        ),
        (
            {
                'limit': 100,
                'driver_license': 'nonexistent',
                'date_from': '2020-01-01',
                'date_to': '2020-03-10',
            },
            200,
            [],
        ),
    ],
)
async def test_get_subventions_by_license_and_date(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
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


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [({'limit': 0, 'driver_license': '1111111111'}, 400)],
)
async def test_get_subventions_with_zero_limit(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
        request_params,
        expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [({'driver_license': '1111111111'}, 400)],
)
async def test_get_subventions_without_limit(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
        request_params,
        expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code', [({'limit': '100'}, 400)],
)
async def test_get_subventions_without_license_and_order_id(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
        request_params,
        expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )


@pytest.mark.parametrize(
    'request_params,expected_response_code',
    [
        (
            {'limit': '100', 'driver_license': '1111111111', 'date_from': ''},
            400,
        ),
        (
            {
                'limit': '100',
                'driver_license': '1111111111',
                'date_from': 'NO DATE',
            },
            400,
        ),
        (
            {
                'limit': '100',
                'driver_license': '1111111111',
                'date_from': '2019-0101',
            },
            400,
        ),
        ({'limit': '100', 'driver_license': '1111111111', 'date_to': ''}, 400),
        (
            {
                'limit': '100',
                'driver_license': '1111111111',
                'date_to': 'NO DATE',
            },
            400,
        ),
        (
            {
                'limit': '100',
                'driver_license': '1111111111',
                'date_to': '2019-0101',
            },
            400,
        ),
    ],
)
async def test_get_subventions_wrong_date_format(
        db,
        web_app_client,
        mock_personal,  # pylint: disable=redefined-outer-name
        request_params,
        expected_response_code,
):
    await check_response_code(
        web_app_client, request_params, expected_response_code,
    )
