import requests
import werkzeug

import pymlaas.settings

TEST_URL = pymlaas.settings.MOCKSERVER_URL + '/test'


def test_mockserver_ok(mockserver):
    @mockserver.json_handler('/test')
    def mock_tracker(request):
        return {'status': 'ok'}

    response = requests.get(TEST_URL)
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}


def test_mockserver_echo(mockserver):
    @mockserver.json_handler('/test')
    def mock_tracker(request):
        return request.json

    response = requests.get(TEST_URL, json={'type': 'echo'})
    assert response.status_code == 200
    assert response.json() == {'type': 'echo'}


def test_mockserver_fail(mockserver):
    @mockserver.json_handler('/test')
    def mock_tracker(request):
        return werkzeug.Response('{}', status=400)
    response = requests.get(TEST_URL)
    assert response.status_code == 400
