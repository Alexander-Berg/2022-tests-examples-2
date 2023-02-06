import json
import pathlib

from aiohttp import web
import pytest


TEST_DATA_PATH = (
    pathlib.Path(__file__).parent / 'static' / 'test_ml_exploration'
)
RESPONSES_PATH = TEST_DATA_PATH / 'responses'
DEFAULT_UMLAAS_DISPATCH_RESPONSE = {
    'verdicts': [
        {
            'tariff_class': 'courier',
            'estimate_distance': 1,
            'estimate_time': 2,
            'order_allowed': True,
        },
    ],
}


def load_json(path):
    with path.open() as handler:
        return json.load(handler)


@pytest.fixture(autouse=True)
def mock_umlaas_dispatch_driver_search_radius_prediction(
        mock_umlaas_dispatch, expected_response,
):  # pylint: disable=invalid-name
    @mock_umlaas_dispatch('/umlaas-dispatch/v1/search-radius-prediction')
    def handler(request):  # pylint: disable=unused-variable
        assert request.json is not None
        if expected_response['status'] == 500:
            return web.json_response(
                expected_response['error_message'], status=500,
            )
        return web.json_response(DEFAULT_UMLAAS_DISPATCH_RESPONSE, status=200)


@pytest.fixture(name='ext_request')
def ext_request_fixture(test_data_json):
    return load_json(test_data_json)


@pytest.fixture(name='expected_response')
def expected_response_fixture(test_data_json):
    expected_response_path = RESPONSES_PATH / test_data_json.name
    assert (
        expected_response_path.exists()
    ), 'Expected response file doesn\'t exist'
    return load_json(expected_response_path)


@pytest.mark.parametrize('test_data_json', TEST_DATA_PATH.glob('*.json'))
async def test_ml_exploration_get_prediction(
        web_app_client, atlas_blackbox_mock, ext_request, expected_response,
) -> None:
    response = await web_app_client.post(
        '/api/v1/ml_exploration/get_prediction', json=ext_request,
    )

    assert response.status == expected_response['status']
    content = await response.json()

    if response.status == 200:
        assert content == expected_response['data']
    else:
        assert content['message'] == expected_response['error_message']
