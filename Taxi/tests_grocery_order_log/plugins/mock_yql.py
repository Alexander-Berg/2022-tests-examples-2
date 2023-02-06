import http.client

import pytest


@pytest.fixture(name='yql')
def _yql(mockserver):
    class Yql:
        token = None

        def __init__(self):
            self.connection = http.client.HTTPSConnection('yql.yandex.net')

        def __del__(self):
            self.connection.close()

        @mockserver.json_handler('/yql/api/v2/', prefix=True)
        @staticmethod
        def proxy_handlers(request):
            assert yql.token
            headers = {
                'Authorization': f'OAuth {yql.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
            }
            yql.connection.request(
                request.method,
                request.path_qs[len('/yql') :],
                headers=headers,
                body=request.get_data(),
            )
            response = yql.connection.getresponse()
            return mockserver.make_response(
                response=response.read(), status=response.status,
            )

    yql = Yql()
    return yql
