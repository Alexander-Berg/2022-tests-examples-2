import pytest


@pytest.fixture(name='eats_regions_cache', autouse=True)
def eats_regions_cache(mockserver, request, load_json):
    marker = request.node.get_closest_marker('eats_regions_cache')

    regions = []

    if marker:
        if 'file' in marker.kwargs:
            regions = load_json(marker.kwargs['file'])
        elif marker.args:
            regions = marker.args[0]

    @mockserver.json_handler('/eats-core/v1/export/regions')
    def _eats_core(request):
        return {'payload': regions}
