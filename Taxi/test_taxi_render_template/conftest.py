# pylint: disable=redefined-outer-name
import pytest
import weasyprint

import taxi_render_template.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_render_template.generated.service.pytest_plugins']


@pytest.fixture
def taxi_render_template_app(web_app):
    return web_app


@pytest.fixture
def taxi_render_template_client(
        aiohttp_client, taxi_render_template_app, loop,
):
    return loop.run_until_complete(aiohttp_client(taxi_render_template_app))


@pytest.fixture
def mock_default_weasyprint_fetcher(monkeypatch, mock):
    @mock
    def _mock_url_fetcher(*args, **kwargs):
        return {'string': b'some image'}

    monkeypatch.setattr(weasyprint, 'default_url_fetcher', _mock_url_fetcher)

    return _mock_url_fetcher
