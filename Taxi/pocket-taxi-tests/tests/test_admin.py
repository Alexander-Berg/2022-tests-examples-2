import utils


ADMIN_BASE_URL = 'http://localhost:8000/'


def test_admin_opening():
    response = utils.retry_request('get', ADMIN_BASE_URL)
    assert response.status_code == 200
