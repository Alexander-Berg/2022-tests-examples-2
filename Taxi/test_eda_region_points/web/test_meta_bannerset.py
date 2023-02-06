import json

import pytest

LINKHEAD = 'https://an.yandex.ru/count/'


@pytest.mark.config(
    EATS_YABS_MOCK_SETTINGS={
        'ctr': 1.0,
        'threshold': 1.0,
        'banners_amount': 100,
    },
)
@pytest.mark.servicetest
@pytest.mark.parametrize(
    'banner_set, expected_banners, expected_code',
    [
        pytest.param(
            '',
            None,
            204,
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
            id='empty banner set',
        ),
        pytest.param(
            '1,2,3',
            {
                'common': {'linkHead': f'{LINKHEAD}'},
                'direct': {
                    'ads': [
                        {
                            'bs_data': {
                                'adId': '3',
                                'count_links': {
                                    'link_tail': 'eyJiYW5uZXJfaWQiOiAzLCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
                                    'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAzLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                                },
                            },
                        },
                        {
                            'bs_data': {
                                'adId': '2',
                                'count_links': {
                                    'link_tail': 'eyJiYW5uZXJfaWQiOiAyLCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
                                    'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAyLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                                },
                            },
                        },
                        {
                            'bs_data': {
                                'adId': '1',
                                'count_links': {
                                    'link_tail': 'eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
                                    'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAxLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                                },
                            },
                        },
                    ],
                },
            },
            200,
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
            id='100% of banners',
        ),
        pytest.param(
            '1,2,3',
            {
                'common': {'linkHead': f'{LINKHEAD}'},
                'direct': {
                    'ads': [
                        {
                            'bs_data': {
                                'adId': '3',
                                'count_links': {
                                    'link_tail': 'eyJiYW5uZXJfaWQiOiAzLCAidHlwZSI6ICJ2aWV3In0=',  # noqa: E501
                                    'url': f'{LINKHEAD}eyJiYW5uZXJfaWQiOiAzLCAidHlwZSI6ICJjb3VudCJ9',  # noqa: E501
                                },
                            },
                        },
                    ],
                },
            },
            200,
            marks=[
                pytest.mark.config(
                    EATS_YABS_MOCK_SETTINGS={
                        'ctr': 1.0,
                        'threshold': 1.0,
                        'banners_amount': 40,
                        'linkhead': LINKHEAD,
                    },
                ),
            ],
            id='40% of banners',
        ),
    ],
)
async def test_meta_bannerset(
        taxi_eda_region_points_web,
        banner_set,
        expected_banners,
        expected_code,
):
    cookie = 'testsuite_cookie'
    request_id = 'testsuite_request_id'
    useragent = 'testsuite-agent'
    xrealip = '127.0.0.1'
    target_ref = 'testsuite_target-refs'
    charset = 'testsuite_charset'

    imp_id = '1'
    force_uniformat = '1'

    response = await taxi_eda_region_points_web.get(
        f'/meta_bannerset/1?target-ref={target_ref}&charset={charset}&reqid={request_id}&'  # noqa: E501
        f'imp-id={imp_id}&'  # required
        f'banner-set={banner_set}&'  # required
        f'force-uniformat={force_uniformat}',  # not required
        headers={
            'user-agent': useragent,
            'Cookie': cookie,
            'X-Real-Ip': xrealip,
        },
    )
    assert response.status == expected_code
    if expected_banners is not None:
        content = await response.text()
        assert json.loads(content) == expected_banners
