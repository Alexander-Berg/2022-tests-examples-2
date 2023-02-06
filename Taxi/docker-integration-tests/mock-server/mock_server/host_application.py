from aiohttp import web
from aiohttp import web_urldispatcher


class HostSubAppResource(web_urldispatcher.AbstractResource):

    def __init__(self, host, app):
        super().__init__()
        self._host = host
        self._app = app

    @property
    def canonical(self) -> str:
        return self._host

    def raw_match(self, path: str) -> bool:
        return path.startswith(self._host)

    def url_for(self, **kwargs):
        raise RuntimeError('.url_for() is not supported '
                           'by sub-application root')

    @staticmethod
    def url(**kwargs):
        """Construct url for route with additional params."""
        raise RuntimeError('.url() is not supported '
                           'by sub-application root')

    def get_info(self):
        return {'app': self._app,
                'host': self._host}

    def add_prefix(self, prefix):
        for resource in self._app.router.resources():
            resource.add_prefix(prefix)

    async def resolve(self, request):
        if request.host.split(':')[0] != self._host:
            return None, set()
        match_info = await self._app.router.resolve(request)
        match_info.add_app(self._app)
        if isinstance(match_info.http_exception, web.HTTPMethodNotAllowed):
            methods = match_info.http_exception.allowed_methods
        else:
            methods = set()
        return match_info, methods

    def __len__(self):
        return len(self._app.router.routes())

    def __iter__(self):
        return iter(self._app.router.routes())


class HostApplication(web.Application):

    def add_host_app(self, host, subapp):
        if self.frozen:
            raise RuntimeError(
                'Cannot add sub application to frozen application')
        if subapp.frozen:
            raise RuntimeError('Cannot add frozen application')

        resource = HostSubAppResource(host, subapp)
        self.router.register_resource(resource)
        self._reg_subapp_signals(subapp)
        self._subapps.append(subapp)
        if self._loop is not None:
            subapp._set_loop(self._loop)  # pylint: disable=protected-access
        return resource
