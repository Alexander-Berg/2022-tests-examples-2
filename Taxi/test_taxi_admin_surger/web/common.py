API_PREFIX = '/admin/v1'
POINT_API_PREFIX = f'{API_PREFIX}/point'
SEARCH_API_PREFIX = f'{POINT_API_PREFIX}/search'


async def make_request_checked(method, *args, **kwargs):
    response = await method(*args, **kwargs)

    if response.status != 200:
        raise Exception(await response.text())  # show error
    if 'json' in response.content_type:
        return await response.json()

    return await response.text()
