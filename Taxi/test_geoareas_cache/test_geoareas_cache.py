#  pylint: disable=unused-variable, protected-access
import pytest

from generated.clients import geoareas


async def test_errors(library_context, mockserver, patch):
    @patch('taxi.util.aiohttp_kit.context.FileCacheHandler.save_to_file')
    def save_cache(body):
        assert body == []

    @patch('taxi.util.aiohttp_kit.context.FileCacheHandler.load_from_file')
    def load_from_file(*args, **kwargs):
        return []

    @mockserver.json_handler('/geoareas/geoareas/v1/tariff-areas')
    def _handler(*args, **kwargs):
        return mockserver.make_response('internal error', status=500)

    library_context.geoareas_cache._first_launch = True

    #  on the first launch cache have to be loaded from file
    await library_context.geoareas_cache.refresh_cache()

    #  after first launch should fail refresh
    with pytest.raises(geoareas.NotDefinedResponse):
        await library_context.geoareas_cache.refresh_cache()
