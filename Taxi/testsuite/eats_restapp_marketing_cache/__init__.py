import typing

import pytest

from eats_restapp_marketing_cache import models


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_restapp_marketing_cache: per-test configuration of '
        'lib-eats-restapp-marketing cache',
    )


@pytest.fixture(name='eats_restapp_marketing_cache_mock', autouse=True)
def _eats_restapp_marketing_cache(request, mockserver):
    class Context:
        def __init__(self):
            self.place_banners = []

        def add_banner(self, place_banner: models.PlaceBanner):
            self.place_banners.append(place_banner)

        def add_banners(self, place_banners: typing.List[models.PlaceBanner]):
            self.place_banners.extend(place_banners)

        def add_banners_from_marker(self, marker):
            if not marker.kwargs:
                return

            place_banners = marker.kwargs.get('place_banners', [])
            self.add_banners(place_banners)

        @property
        def times_called(self) -> int:
            return _campaigns.times_called

    ctx = Context()

    @mockserver.json_handler(
        '/eats-restapp-marketing/internal/marketing/v1/ad/campaigns',
    )
    def _campaigns(request):
        campaigns = []
        for place_banner in ctx.place_banners:
            campaigns.append(place_banner.as_dict())

        return {'cursor': '', 'campaigns': campaigns}

    for marker in request.node.iter_markers('eats_restapp_marketing_cache'):
        ctx.add_banners_from_marker(marker)

    return ctx
