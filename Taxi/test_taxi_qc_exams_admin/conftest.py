# pylint: disable=wildcard-import, unused-wildcard-import, redefined-outer-name
from aiohttp import web
import pytest

import taxi_qc_exams_admin.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['taxi_qc_exams_admin.generated.service.pytest_plugins']


@pytest.fixture(autouse=True)
def mock_parks(mockserver):
    @mockserver.handler('/fleet-parks/v1/parks/list')
    def _mock_parks_list(request):
        ids = request.json['query']['park']['ids']
        return web.json_response(
            dict(
                parks=[
                    dict(
                        id=x,
                        login=x + '_login',
                        name=x,
                        is_active=True,
                        city_id='Москва',
                        locale='ru',
                        is_billing_enabled=False,
                        is_franchising_enabled=False,
                        demo_mode=False,
                        country_id='rus',
                        geodata={'lat': 0, 'lon': 0, 'zoom': 0},
                    )
                    for x in ids
                ],
            ),
        )
