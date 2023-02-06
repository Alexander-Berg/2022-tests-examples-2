import pytest


def _create_headers(
        driver_dbid,
        driver_uuid,
        user_agent,
        taximeter_version,
        application,
        platform,
):
    result = {
        'User-Agent': user_agent,
        'X-Request-Application-Version': taximeter_version,
        'X-YaTaxi-Park-Id': driver_dbid,
        'X-YaTaxi-Driver-Profile-Id': driver_uuid,
    }
    if application is not None:
        result['X-Request-Application'] = application

    if platform is not None:
        result['X-Request-Platform'] = platform

    return result


class DAFWrapper:
    def __init__(
            self,
            service,
            driver_dbid,
            driver_uuid,
            user_agent,
            taximeter_version,
            application=None,
            platform=None,
    ):
        self.service = service
        self.driver_dbid = driver_dbid
        self.driver_uuid = driver_uuid
        self.user_agent = user_agent
        self.taximeter_version = taximeter_version
        self.application = application
        self.platform = platform

    def _get_headers(self):
        return _create_headers(
            self.driver_dbid,
            self.driver_uuid,
            self.user_agent,
            self.taximeter_version,
            self.application,
            self.platform,
        )

    def _update_request_kwargs(self, request_kwargs):
        if 'headers' in request_kwargs:
            request_kwargs['headers'].update(self._get_headers())

    async def get(self, *args, **kwargs):
        self._update_request_kwargs(kwargs)
        return await self.service.get(*args, **kwargs)

    async def post(self, *args, **kwargs):
        self._update_request_kwargs(kwargs)
        return await self.service.post(*args, **kwargs)

    async def put(self, *args, **kwargs):
        self._update_request_kwargs(kwargs)
        return await self.service.put(*args, **kwargs)

    async def delete(self, *args, **kwargs):
        self._update_request_kwargs(kwargs)
        return await self.service.delete(*args, **kwargs)

    async def patch(self, *args, **kwargs):
        self._update_request_kwargs(kwargs)
        return await self.service.patch(*args, **kwargs)


class DAPFixture:
    def __init__(self):
        pass

    def create_driver_wrapper(
            self,
            service,
            driver_dbid,
            driver_uuid,
            user_agent='Taximeter 8.90 (228)',
            taximeter_version='8.90',
            application=None,
            platform=None,
    ):
        return DAFWrapper(
            service,
            driver_dbid,
            driver_uuid,
            user_agent,
            taximeter_version,
            application,
            platform,
        )


@pytest.fixture(name='dap')
def dap_fixture():
    return DAPFixture()
