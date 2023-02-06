async def get(taxi_access_control, url, params, expected_status_code):
    response = await taxi_access_control.get(
        url,
        params=params,
        headers={'X-Yandex-Login': 'userx', 'X-Yandex-Uid': '100'},
    )
    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response.json(),
    )
    return response.json()


async def post(
        taxi_access_control, url, data, expected_status_code, params=None,
):
    params = params or {}
    response = await taxi_access_control.post(
        url,
        data,
        params=params,
        headers={'X-Yandex-Login': 'userx', 'X-Yandex-Uid': '100'},
    )
    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response.json(),
    )
    return response.json()


async def put(taxi_access_control, url, data, expected_status_code):
    response = await taxi_access_control.put(
        url, data, headers={'X-Yandex-Login': 'userx', 'X-Yandex-Uid': '100'},
    )
    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response.json(),
    )
    return response.json()
