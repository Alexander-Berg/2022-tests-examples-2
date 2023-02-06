import pytest


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v2/driver_licenses/bulk_store')
    @mockserver.json_handler('/personal/v2/phones/bulk_store')
    def _bulk_store(request):
        response = []
        for item in request.json['items']:
            value = item['value']
            if value == 'error':
                response.append(
                    {'error': 'unexpected error', 'value': 'error'},
                )
            else:
                response.append(
                    {'id': personalize_item(value), 'value': 'no guarantee'},
                )
        return mockserver.make_response(status=200, json={'items': response})


def personalize_item(item: str):
    return item[::-1]
