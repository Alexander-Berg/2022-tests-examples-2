class AssertUtil:
    _USE_VALUE = object()

    def __init__(self, client, url):
        self.client = client
        self.url = url

    async def assert_equal(self, request_data, expected_data=_USE_VALUE):
        expected_data = self._get_optional_value(request_data, expected_data)
        await self._do_request_and_assert(
            request_data=request_data,
            expected_status_code=200,
            expected_data=expected_data,
        )

    async def _do_request_and_assert(
            self, request_data, expected_status_code, expected_data,
    ):
        status_code, data = await self._do_request(request_data)
        assert status_code == expected_status_code, (
            '\n'
            f'Expected status code is "{expected_status_code}"\n'
            f'Response status code is "{status_code}"\n'
            f'Response data is "{data}"'
        )
        assert data == expected_data, (
            '\n'
            f'Expected data is "{expected_data}"\n'
            f'Response data is "{data}"'
        )

    async def _do_request(self, data):
        raise NotImplementedError

    def _get_optional_value(self, value, optional_value):
        if optional_value is self._USE_VALUE:
            return value

        return optional_value


class PostJsonAssertUtil(AssertUtil):
    async def _do_request(self, data):
        response = await self.client.post(self.url, json=data)
        return response.status_code, response.json()


class GetJsonAssertUtil(AssertUtil):
    async def _do_request(self, data):
        response = await self.client.get(self.url, params=data)
        return response.status_code, response.json()
