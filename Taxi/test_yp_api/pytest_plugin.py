import pytest


@pytest.fixture
def yp_mockserver(
        mockserver, relative_load_json,
):  # pylint: disable=W0621,R1710
    def _build_mockserver():
        pod_stat_data = relative_load_json(f'yp_pod_stat.json')

        @mockserver.json_handler('/yp-api/', prefix=True)
        def handler(request):
            if request.path == '/yp-api/ObjectService/GetObject':
                return pod_stat_data
            return {}

        return handler

    return _build_mockserver
