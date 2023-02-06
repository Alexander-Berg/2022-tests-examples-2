import pytest

from taxi_antifraud.yavtocod import consts


def _extract_request_data(calls):
    return [
        {
            'url': x.get('url'),
            'params': x.get('params'),
            'data': x.get('data'),
            'json': x.get('json'),
            'headers': x.get('headers'),
            'proxy': x.get('proxy'),
        }
        for x in calls
    ]


def _mock_externals(patch_aiohttp_session, response_mock):
    @patch_aiohttp_session(consts.VIN01_URL, 'POST')
    def _vin01_api(_, url, params, data, headers, json, proxy, **kwargs):
        return response_mock(
            text=r'{"success":true,"code":200,'
            r'"data":{"vin":"XTA219010K0624765"}}',
        )

    return _vin01_api


@pytest.mark.parametrize(
    'request_data,expected_response_json,expected_vin01_requests',
    [
        (
            {'car_number': 'А001АА777'},
            {
                'sources': [
                    {
                        'data': [
                            {'name': 'vin', 'value': 'XTA219010K0624765'},
                        ],
                        'name': 'vin01',
                    },
                ],
            },
            [
                {
                    'data': None,
                    'headers': {
                        'Accept': '*/*',
                        'Accept-Language': 'ru,en-US;q=0.9,en;q=0.8',
                        'Cookie': (
                            'PHPSESSID=fe96120b2c3752e841f15e5654db324e; '
                            '_ym_uid=1626364763177957718; _ym_d=1626364763; '
                            '_ga=GA1.2.1897130778.1626364763; '
                            '_gid=GA1.2.1910473691.1626364763; _ym_isad=2; '
                            '__gads=ID=789583dc6e2b9a57-2297cc547cc80069:'
                            'T=1626364763:RT=1626364763:S=ALNI_MZuTXMPwpVTHbv'
                            '-GM6kfJYK4cC1AQ; TNoty=true'
                        ),
                        'Referer': 'https://vin01.ru/',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/90.0.4430.212 Safari/537.36'
                        ),
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    'json': None,
                    'params': {
                        'gosNumber': 'А001АА777',
                        'key': '03AGdBq25xPS7B1hMTaARShOJNimT9dYZQzaXTL4zS-YmPa585fZBJDUGw_UR-ciH4rnmeli_XxNaQNyhFMIJc-Mg352cPogsWD6kRCMWi55PdWW5ifOyP5zpxYz3U3Rcp0HzutIpb50XOrnyyP8aY66_mygAzj9w5uGpYNZEoHkP_jXMztMgRnMNm2uTuuJDH89orHU7c8mM-ezKFVfYLT-3fK4envYgM-eiQUsx38mBG8CbvjBsMRCnLHFEJKgsTzZERUFf112UaJO9M00wcaBM0PujcrqYFPygi2Bjg42_mPE-HOkOJcDywT5nKw5yfzr2_sQ-mw_DwUyhE1W7V5SS0TOK8zSj96l9DPzH1lCnvP-XS0QUyyf_P9UkH4cJuRKhvjh-5wkMrg1IjaVD-Ap8PViaWGu5IZ8HXv4ZIvQJTVn2YUCRR_EH2ZN_h-7fRZCtt1mW1TJUoLxQP2bPbmRIHInfX0204NmJ9jcGBUNVG4E9oM_duyBE',  # noqa: E501 pylint: disable=line-too-long
                        'site': '1',
                    },
                    'proxy': 'http://taxi_afraud:pass@animals.search.yandex.net:4004',  # noqa: E501 pylint: disable=line-too-long
                    'url': 'https://vin01.ru/v2/getVin.php',
                },
            ],
        ),
    ],
)
async def test_basic(
        web_app_client,
        patch_aiohttp_session,
        response_mock,
        request_data,
        expected_response_json,
        expected_vin01_requests,
):
    _vin01_api = _mock_externals(patch_aiohttp_session, response_mock)

    response = await web_app_client.post(
        '/yavtocod/v1/get_info_by_car_number', json=request_data,
    )

    assert await response.json() == expected_response_json

    assert _extract_request_data(_vin01_api.calls) == expected_vin01_requests
