import pytest

from taxi_antifraud.yavtocod import consts


def _extract_request_data(calls):
    return [
        {
            'url': x.get('url'),
            'data': x.get('data'),
            'headers': x.get('headers'),
        }
        for x in calls
    ]


@pytest.mark.parametrize(
    'request_data,gibdd_response,expected_response_json,'
    'expected_gibdd_requests',
    [
        (
            {'vin': '123456'},
            {
                'RequestResult': {
                    'vehicle': {
                        'color': 'Синий',
                        'bodyNumber': '123',
                        'year': '2007',
                        'model': 'тесла модел икс',
                    },
                },
            },
            {
                'body_number': '123',
                'color': 'Синий',
                'model': 'тесла модел икс',
                'year': '2007',
            },
            [
                {
                    'data': {
                        'captchaWord': '',
                        'checkType': 'history',
                        'reCaptchaToken': '03AGdBq247jOVStX1fz52UbQ2G6P6UGNiGqJvOo4zLPcHOvQ7GsjXx05EJbZouqoozN1hpuMYRIEEu2C8I0Hy9QXExJUaSQ96QIYDcgUNOig-ekMUzaSAOzy14ayEW6DIycFiCR2sgFwFcY95mUxkilLUYrQvidkwZACbndprfiezQTR2lDC0x3yJubFo3n6GD93o959Vzw3GmVr3C75KAphSSSML73Q6QQUbOe5acGy9MEgC3LfdAEyvurTPTrhLqHaUftbVwGJ6-jch4waquxHIF76FAqSCUw9cfinwJBdeQpCHsBp63RF9LQifq1csVQ6kPezBykVhAv7pkUr0MqYmh4Y5gpw2Tz9LhCOl6t_5HC2VlSkZ0N0sVH9Yr1cLwIbQXWjtSym2MCrZGtvEs5HamFkMJV4LFahnAjE0pPBoXBOOV4EXUeg3tvObGNVOWjKt53D91SlQtJPaEkJr6VWZbd_b8rsth2YaQGN6iOzXmees051Ot-SsQA_i4_hPFHVgIyafUI5sjBxcfyNKHyYSwOl96TIMmmA',  # noqa: E501 pylint: disable=line-too-long
                        'vin': '123456',
                    },
                    'headers': {
                        'Accept': (
                            'application/json, text/javascript, */*; q=0.01'
                        ),
                        'Accept-Language': 'ru,en;q=0.9',
                        'Content-Type': (
                            'application/x-www-form-urlencoded; '
                            'charset=UTF-8'
                        ),
                        'Origin': 'https://xn--90adear.xn--p1ai',
                        'Referer': 'https://xn--90adear.xn--p1ai/check/auto',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/90.0.4430.212 Safari/537.36'
                        ),
                    },
                    'url': 'https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/history',  # noqa: E501 pylint: disable=line-too-long
                },
            ],
        ),
        (
            {'vin': '123456'},
            {
                'requestTime': '08.12.2021 21:49',
                'RequestResult': '',
                'hostname': 'check.gibdd.ru',
                'vin': '123456',
                'regnum': '',
                'message': 'Ошибка исполнения запроса:Ошибка исполнения запроса сервером: java.lang.Exception: No results found',  # noqa: E501 pylint: disable=line-too-long
                'status': 500,
            },
            {},
            [
                {
                    'data': {
                        'captchaWord': '',
                        'checkType': 'history',
                        'reCaptchaToken': '03AGdBq247jOVStX1fz52UbQ2G6P6UGNiGqJvOo4zLPcHOvQ7GsjXx05EJbZouqoozN1hpuMYRIEEu2C8I0Hy9QXExJUaSQ96QIYDcgUNOig-ekMUzaSAOzy14ayEW6DIycFiCR2sgFwFcY95mUxkilLUYrQvidkwZACbndprfiezQTR2lDC0x3yJubFo3n6GD93o959Vzw3GmVr3C75KAphSSSML73Q6QQUbOe5acGy9MEgC3LfdAEyvurTPTrhLqHaUftbVwGJ6-jch4waquxHIF76FAqSCUw9cfinwJBdeQpCHsBp63RF9LQifq1csVQ6kPezBykVhAv7pkUr0MqYmh4Y5gpw2Tz9LhCOl6t_5HC2VlSkZ0N0sVH9Yr1cLwIbQXWjtSym2MCrZGtvEs5HamFkMJV4LFahnAjE0pPBoXBOOV4EXUeg3tvObGNVOWjKt53D91SlQtJPaEkJr6VWZbd_b8rsth2YaQGN6iOzXmees051Ot-SsQA_i4_hPFHVgIyafUI5sjBxcfyNKHyYSwOl96TIMmmA',  # noqa: E501 pylint: disable=line-too-long
                        'vin': '123456',
                    },
                    'headers': {
                        'Accept': (
                            'application/json, text/javascript, */*; q=0.01'
                        ),
                        'Accept-Language': 'ru,en;q=0.9',
                        'Content-Type': (
                            'application/x-www-form-urlencoded; '
                            'charset=UTF-8'
                        ),
                        'Origin': 'https://xn--90adear.xn--p1ai',
                        'Referer': 'https://xn--90adear.xn--p1ai/check/auto',
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-site',
                        'User-Agent': (
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                            'AppleWebKit/537.36 (KHTML, like Gecko) '
                            'Chrome/90.0.4430.212 Safari/537.36'
                        ),
                    },
                    'url': 'https://xn--b1afk4ade.xn--90adear.xn--p1ai/proxy/check/auto/history',  # noqa: E501 pylint: disable=line-too-long
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
        gibdd_response,
        expected_response_json,
        expected_gibdd_requests,
):
    @patch_aiohttp_session(consts.GIBDD_URL, 'POST')
    def _gibdd_api(_, url, params, data, headers, json, **kwargs):
        return response_mock(json=gibdd_response)

    response = await web_app_client.post(
        '/yavtocod/v1/get_info_by_vin', json=request_data,
    )

    assert await response.json() == expected_response_json

    assert _extract_request_data(_gibdd_api.calls) == expected_gibdd_requests
