# pylint: disable=redefined-outer-name
import pytest

import hiring_task_creator.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_task_creator.generated.service.pytest_plugins']


@pytest.fixture  # noqa: F405
def geobase(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/geobase/v1/region_by_id')
    async def region_by_id(request):  # pylint: disable=unused-variable
        data = load_json('geobase_response.json')
        return data


@pytest.fixture  # noqa: F405
def hiring_sf_loader(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/hiring-sf-loader/v1/documents-for-call')
    async def handler(request):  # pylint: disable=unused-variable
        data = load_json('hiring_sf_loader_response.json')
        return data


@pytest.fixture  # noqa: F405
# pylint: disable=invalid-name
def hiring_telephony_oktell_callback(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler(
        '/hiring-telephony-oktell-callback/v1/tasks/create',
    )
    async def handler(request):  # pylint: disable=unused-variable
        request_payload = request.json
        expected_intervals = load_json('expected_call_intervals.json')
        assert (
            expected_intervals == request_payload['tasks'][0]['call_intervals']
        )
        data = load_json('hiring_telephony_oktell_callback_response.json')
        return data

    return handler
