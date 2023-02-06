import os
import sys
import pytest
import requests_mock

import metrika.pylib.bishop as bp
import metrika.pylib.http as http
import metrika.pylib.qloud as muq
import metrika.pylib.utils as mutils
import metrika.pylib.mtapi.cluster as mtapi_cluster


@pytest.fixture
def m():
    with requests_mock.Mocker() as m:
        yield m


class BishopTestError(Exception):
    pass


def test_bishop_init():
    bishop = bp.Bishop(token='')
    assert bishop.url == bp.API_URL


def test_get_oauth_token_is_called_if_no_token_provided(monkeypatch):
    def mock_get_robot_oauth_token(*args, **kwargs):
        raise BishopTestError("Test Error")

    monkeypatch.setattr(bp, 'get_robot_oauth_token', mock_get_robot_oauth_token)

    with pytest.raises(BishopTestError):
        bp.Bishop()


def test_bishop_error_on_invalid_json(m):
    url = bp.API_URL + '/v2/config/superd/superd.environment'
    m.get(url, text='{invalid Jsoon lol')

    bishop = bp.Bishop(token='')
    with pytest.raises(bp.BishopError):
        bishop.get_config('superd', 'superd.environment')


def test_bishop_error_on_unhandled_exceptioon(monkeypatch):
    def mock_http_request(*args, **kwargs):
        raise BishopTestError("Test Error")

    monkeypatch.setattr(http, 'request', mock_http_request)

    bishop = bp.Bishop(token='')
    with pytest.raises(bp.BishopError):
        bishop.get_config('superd', 'superd.environment')


def test_get_version_error_if_version_header_is_missing(m):
    url = bp.API_URL + '/v2/version/superd/superd.environment'
    m.head(url)

    bishop = bp.Bishop(token='')
    with pytest.raises(bp.BishopError):
        bishop.get_version('superd', 'superd.environment')


def test_get_version_by_str(m):
    url = bp.API_URL + '/v2/version/superd/superd.environment'
    headers = {
        'bishop-config-version': '65',
        'bishop-config-format': 'plaintext',
    }
    m.head(url, headers=headers)
    bishop = bp.Bishop(token='')
    assert 65 == bishop.get_version('superd', 'superd.environment')


def test_get_config_error_if_version_header_is_missing(m):
    url = bp.API_URL + '/v2/config/superd/superd.environment'
    headers = {
        'bishop-config-format': 'plaintext',
    }
    m.get(url, headers=headers, text='some config text')

    bishop = bp.Bishop(token='')
    with pytest.raises(bp.BishopError):
        bishop.get_config('superd', 'superd.environment')


def test_get_config_error_if_format_header_is_missing(m):
    url = bp.API_URL + '/v2/config/superd/superd.environment'
    headers = {
        'bishop-config-version': '1',
    }
    m.get(url, headers=headers, text='some config text')

    bishop = bp.Bishop(token='')
    with pytest.raises(bp.BishopError):
        bishop.get_config('superd', 'superd.environment')


def test_get_config_by_str(m):
    url = bp.API_URL + '/v2/config/superd/superd.environment'
    text = '{"a": "10"}'
    headers = {
        'bishop-config-version': '1',
        'bishop-config-format': 'plaintext',
    }
    m.get(url, text=text, headers=headers)
    bishop = bp.Bishop(token='')
    assert (1, 'plaintext', text) == bishop.get_config('superd', 'superd.environment')


def test_get_config_by_list(m):
    url = bp.API_URL + '/v2/config/superd/superd.environment'
    text = '{"a": "10"}'
    headers = {
        'bishop-config-version': '1',
        'bishop-config-format': 'xml',
    }
    m.get(url, text=text, headers=headers)
    bishop = bp.Bishop(token='')
    assert (1, 'xml', text) == bishop.get_config('superd', ['superd.environment'])


def test_get_config_by_multi_list_one_existing_element(m):
    first_url = bp.API_URL + '/v2/config/superd/superd.environment.subenvironment'
    second_url = bp.API_URL + '/v2/config/superd/superd.environment'
    headers = {
        'bishop-config-version': '1',
        'bishop-config-format': 'json',
    }
    m.register_uri('GET', first_url, text='', headers=headers, status_code=404)
    m.register_uri('GET', second_url, text='{"a": "10"}', headers=headers, status_code=200)
    bishop = bp.Bishop(token='')
    assert (1, 'json', '{"a": "10"}') == bishop.get_config('superd', ['superd.environment.subenvironment', 'superd.environment'])


def test_get_config_by_multi_list_all_existing_elements(m):
    first_url = bp.API_URL + '/v2/config/superd/superd.environment.subenvironment'
    second_url = bp.API_URL + '/v2/config/superd/superd.environment'
    headers = {
        'bishop-config-version': '1',
        'bishop-config-format': 'json',
    }
    m.register_uri('GET', first_url, text='{"a": "10"}', headers=headers, status_code=200)
    m.register_uri('GET', second_url, text='{"b": "20"}', headers=headers, status_code=200)
    bishop = bp.Bishop(token='')
    assert (1, 'json', '{"a": "10"}') == bishop.get_config('superd', ['superd.environment.subenvironment', 'superd.environment'])


def test_get_bishop_environment_not_in_qloud(monkeypatch):
    def mock_am_i_in_qloud(*args, **kwargs):
        return False

    def mock_mtapi_cluster_get(*args, **kwargs):
        return [{"project": "project", "environment": "environment", "type": "type"}]

    monkeypatch.setattr(muq, 'am_i_in_qloud', mock_am_i_in_qloud)
    monkeypatch.setattr(mtapi_cluster.ClusterAPI, 'get', mock_mtapi_cluster_get, raising=False)

    env = bp.get_bishop_environment()

    if sys.version.startswith('2.'):
        assert env == 'metrika.conductor.type.py2_metrika-pylib-bishop-tests.environment'
    else:
        assert env == 'metrika.conductor.type.metrika-pylib-bishop-tests.environment'


def test_get_bishop_environment_unknown_server(monkeypatch):
    def mock_am_i_in_qloud(*args, **kwargs):
        return False

    def mock_mtapi_cluster_get(*args, **kwargs):
        raise mtapi_cluster.BadRequestException('error')

    monkeypatch.setattr(muq, 'am_i_in_qloud', mock_am_i_in_qloud)
    monkeypatch.setattr(mtapi_cluster.ClusterAPI, 'get', mock_mtapi_cluster_get, raising=False)

    env = bp.get_bishop_environment()

    if sys.version.startswith('2.'):
        assert env == 'metrika.other.junk.py2_metrika-pylib-bishop-tests.development'
    else:
        assert env == 'metrika.other.junk.metrika-pylib-bishop-tests.development'


def test_get_bishop_environment_in_qloud(monkeypatch):
    def mock_am_i_in_qloud(*args, **kwargs):
        return True

    def mock_get_qloud_info(*args, **kwargs):
        return {
            'project': 'project',
            'application': 'application',
            'component': 'component',
            'environment': 'environment',
        }

    monkeypatch.setattr(muq, 'am_i_in_qloud', mock_am_i_in_qloud)
    monkeypatch.setattr(muq, 'get_qloud_info', mock_get_qloud_info)

    env = bp.get_bishop_environment()
    assert env == 'metrika.qloud.application.component.environment'


def test_get_bishop_program_in_qloud(monkeypatch):
    def mock_am_i_in_qloud(*args, **kwargs):
        return True

    def mock_get_qloud_info(*args, **kwargs):
        return {
            'application': 'application',
            'component': 'component',
        }

    monkeypatch.setattr(muq, 'am_i_in_qloud', mock_am_i_in_qloud)
    monkeypatch.setattr(muq, 'get_qloud_info', mock_get_qloud_info)

    program = bp.get_bishop_program()
    assert program == 'application-component'


def test_get_bishop_program_not_in_qloud(monkeypatch):
    def mock_am_i_in_qloud(*args, **kwargs):
        return False

    def mock_get_program_name(*args, **kwargs):
        return 'test-program-name'

    monkeypatch.setattr(muq, 'am_i_in_qloud', mock_am_i_in_qloud)
    monkeypatch.setattr(mutils, 'get_program_name', mock_get_program_name)

    program = bp.get_bishop_program()
    assert program == 'test-program-name'


def test_bishop_env_from_env_var():
    expected_env = 'asd.asd'
    os.environ[bp.BISHOP_ENVIRONMENT_VARIABLE_NAME] = expected_env

    env = bp.get_bishop_environment()
    assert env == expected_env
