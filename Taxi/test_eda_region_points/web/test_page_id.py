import json

import pytest

LINKHEAD = 'https://an.yandex.ru/count/'


@pytest.mark.parametrize(
    'additional_banners, expected_banners',
    [
        pytest.param(
            [],
            None,
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 1.0,
                        'banners_amount': 100,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='empty_additional_banners',
        ),
        pytest.param(
            [{'banner_id': 1, 'value_coefs': {'A': 1, 'B': 2, 'C': 3}}],
            {
                'direct_premium': [
                    {
                        'bid': '1',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                ],
                'stat': [{'link_head': LINKHEAD}],
            },
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 1.0,
                        'banners_amount': 100,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='additional_banners_with_ABC',
        ),
        pytest.param(
            [{'banner_id': 1234}],
            {
                'direct_premium': [
                    {
                        'bid': '1234',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                ],
                'stat': [{'link_head': LINKHEAD}],
            },
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 1.0,
                        'banners_amount': 100,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='additional_banners_without_ABC',
        ),
        pytest.param(
            [
                {'banner_id': 1},
                {'banner_id': 1234, 'value_coefs': {'A': 10, 'B': 2, 'C': 3}},
            ],
            {
                'direct_premium': [
                    {
                        'bid': '1234',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                    {
                        'bid': '1',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                ],
                'stat': [{'link_head': LINKHEAD}],
            },
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 0.0,
                        'banners_amount': 100,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='banner_sorting_depending_on_coefs',
        ),
        pytest.param(
            [{'banner_id': 1}, {'banner_id': 1234}],
            {
                'direct_premium': [
                    {
                        'bid': '1234',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxMjM0LCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                    {
                        'bid': '1',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': (
                            'eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJ2aWV3In0='
                        ),
                    },
                ],
                'stat': [{'link_head': LINKHEAD}],
            },
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 0.0,
                        'banners_amount': 100,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='banner_sorting_depending_on_bid',
        ),
        pytest.param(
            [{'banner_id': 1}, {'banner_id': 1000000}],
            {
                'direct_premium': [
                    {
                        'bid': '1000000',
                        'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxMDAwMDAwLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                        'link_tail': 'eyJiYW5uZXJfaWQiOiAxMDAwMDAwLCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
                    },
                ],
                'stat': [{'link_head': LINKHEAD}],
            },
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 0.0,
                        'banners_amount': 50,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='banner_cropping',
        ),
    ],
)
async def test_page_id(
        taxi_eda_region_points_web, additional_banners, expected_banners,
):
    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    mobile_ifa = 'testsuite_mobile_ifa'
    device_id = 'testsuite_device_id'
    appmetrica_uuid = 'testsuite_appmetrica_uuid'
    useragent = 'testsuite-agent'
    xrealip = '127.0.0.1'
    target_ref = 'testsuite_target-refs'
    charset = 'testsuite_charset'

    response = await taxi_eda_region_points_web.get(
        f'/page/1?target-ref={target_ref}&charset={charset}&reqid={request_id}'
        f'&mobile-ifa={mobile_ifa}&device-id={device_id}&uuid={appmetrica_uuid}&'  # noqa: E501
        f'additional-banners-only=1&text=testsuite&'
        f'additional-banners={json.dumps(additional_banners)}',
        headers={
            'user-agent': useragent,
            'Cookie': cookie,
            'X-Real-Ip': xrealip,
        },
    )
    assert response.status == 200
    if expected_banners is not None:
        content = await response.text()
        assert json.loads(content) == expected_banners
