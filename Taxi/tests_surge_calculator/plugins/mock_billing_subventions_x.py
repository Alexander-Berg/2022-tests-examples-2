import pytest

FILENAME = 'subventions.json'


@pytest.fixture(autouse=True)
def billing_subventions_x(mockserver, load_json):
    @mockserver.json_handler('/billing-subventions-x/v2/rules/select')
    def _point_employ(request):
        return mockserver.make_response(json=load_json(FILENAME))
