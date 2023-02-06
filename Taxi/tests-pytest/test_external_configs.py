import json
import os
import time

import pytest

from taxi import config
from taxi.conf import settings
from taxi.config import params
from taxi.config import service
from taxi.config import validator
from taxi.core import async
from taxi.external import configs


SNAPSHOT_PATH = settings.CONFIGS_SNAPSHOT_PATH


def _make_param(name):
    setattr(config, name, params.Param(
        group='test',
        description='test',
        default='default_test_value',
        validators=[validator.string]
    ))
    attr = getattr(config, name)
    attr.set_name(name)
    params.Param.all_names.remove(name)
    return attr


def _change_update_time(date):
    mod_time = time.mktime(date.timetuple())
    os.utime(SNAPSHOT_PATH, (mod_time, mod_time))


@pytest.fixture(autouse=True)
def use_configs_api(monkeypatch):
    monkeypatch.setattr(settings, 'USE_CONFIGS_API', True)


@pytest.mark.parametrize('code, response_body, expected_value', [
    (200, {'configs': {'TEST': True}}, True),
    (200, {
        'configs': {
            'TEST': [{'a': 1, 'b': 0.5}],
            'OTHER': 123,
        }}, [{'a': 1, 'b': 0.5}]),
])
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_values(code, response_body, expected_value, areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(code, body=json.dumps(response_body))

    service._cache._reset()
    value = yield configs.get('TEST')
    assert value == expected_value


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_configs_service(areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        return areq_request.response(
            200, body='{"configs": {"TEST_PARAM": "value"}}'
        )

    service._cache._reset()
    _make_param('TEST_PARAM')
    value = yield config.TEST_PARAM.get()
    assert value == 'value'


def test_update():
    service._cache._save_to_file('A', 1)
    service._cache._save_to_file('B', [1, 2, 3])
    assert os.path.isfile(os.path.join(SNAPSHOT_PATH, 'A.json'))
    assert os.path.isfile(os.path.join(SNAPSHOT_PATH, 'B.json'))


@pytest.inline_callbacks
def test_get(patch):
    values = {
        'A': 1,
        'B': [1, 2, 3],
        'C': True,
        'D': 'test'
    }

    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return values

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        return values[args[0]]

    @patch('taxi.external.configs.get_by_ids')
    def several(*args, **kwargs):
        return {'configs':
            {key: values[key] for key in args[0]},
            'updated_at': None}

    service._cache._reset()
    assert not service._cache._is_valid

    value = yield service._cache.get('A')
    assert not service._cache._is_empty
    assert value == 1

    service._cache._cache = {'A': 'new_value'}
    if async.is_async_env():
        service._cache._update()
    value = yield service._cache.get('A')
    assert value == 1

    service._cache._cache = {'A': 'new_value'}
    value = yield service._cache.get('A')
    assert value == 'new_value'
    assert len(one.calls) == 1
    assert len(several.calls) == 1
    assert not all.calls


@pytest.inline_callbacks
def test_without_update(patch):
    @patch('taxi.config.service._file_lock')
    def file_lock(*args, **kwargs):
        raise service.ResourceBusyError

    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return {}

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        return 123

    service._cache._reset()
    value = yield service._cache.get('A')
    assert not os.path.isfile(SNAPSHOT_PATH)
    assert service._cache._last_updated == 0
    assert value == 123
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.inline_callbacks
def test_default_get_one(patch):
    @patch('taxi.config.service._file_lock')
    def file_lock(*args, **kwargs):
        raise service.ResourceBusyError

    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return {}

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.NoValueError('TEST not found')

    service._cache._reset()
    assert service._cache._is_empty
    assert not os.path.isfile(SNAPSHOT_PATH)
    _make_param('TEST')
    value = yield config.TEST.get()
    assert value == 'default_test_value'
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.inline_callbacks
def test_default_get_all(patch):
    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return {}

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.NoValueError('TEST not found')

    service._cache._reset()
    _make_param('TEST')
    value = yield config.TEST.get()
    assert value == 'default_test_value'
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.mark.now('2018-11-19 13:00:00+03')
@pytest.inline_callbacks
def test_not_found(patch):
    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return {}

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.NoValueError('A not found')

    @patch('taxi.config.service.ConfigsCache._get_from_file')
    def file_read(*args, **kwargs):
        raise configs.NoValueError('A not found')

    service._cache._reset()
    _make_param('A')
    value = yield config.A.get()
    assert value == 'default_test_value'
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.mark.now('2018-11-19 13:00:00+03')
@pytest.inline_callbacks
def test_none_value(patch):
    @patch('taxi.config.service._file_lock')
    def file_lock(*args, **kwargs):
        raise service.ResourceBusyError

    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        return {}

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        return None

    service._cache._reset()
    _make_param('A')
    value = yield config.A.get()
    assert value is None
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.mark.now('2018-11-19 13:00:00+03')
@pytest.inline_callbacks
def test_get_from_file(patch):
    @patch('taxi.external.configs.get_all')
    def all(*args, **kwargs):
        raise configs.ServerError('Service downtime')

    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.ServerError('Service downtime')

    service._cache._reset()
    service._cache._save_to_file('A', 12345)
    _make_param('A')
    value = yield config.A.get()
    assert value == 12345
    assert len(one.calls) == 1
    assert len(all.calls) == 0


@pytest.mark.now('2018-11-19 13:00:00+03')
@pytest.inline_callbacks
def test_get_from_file_cache(patch):
    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.ServerError('Service downtime')

    @patch('taxi.external.configs.get_by_ids')
    def several(*args, **kwargs):
        raise configs.ServerError()

    service._cache._reset()
    service._cache._save_to_file('A', 12345)
    _make_param('A')
    value = yield config.A.get()
    assert value == 12345
    file_path = os.path.join(service._cache._snapshot_path, 'A.json')

    with open(file_path, 'w') as file:
        json.dump('test', file)
        file.flush()
    file_stat = os.stat(file_path)
    os.utime(file_path, (file_stat.st_atime - 9, file_stat.st_mtime - 9))
    value = yield config.A.get()
    assert value == 12345

    file_path = os.path.join(service._cache._snapshot_path, 'A.json')
    service._cache._files_last_read_time[file_path] = 1
    value = yield config.A.get()
    assert value == 'test'

    service._cache._last_updated = 0
    value = yield config.A.get()
    assert value == 'test'

    assert len(one.calls) == 1


@pytest.inline_callbacks
def test_service_bad_response_with_file(patch):
    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.ServerError()

    @patch('taxi.external.configs.get_by_ids')
    def several(*args, **kwargs):
        raise configs.ServerError()

    @patch('taxi.config.service.ConfigsCache._get_from_file')
    def file_read(*args, **kwargs):
        return 1

    _make_param('TEST_P')

    value = yield config.TEST_P.get()
    assert 1 == value


@pytest.inline_callbacks
def test_service_bad_response_without_file(patch):
    @patch('taxi.external.configs.get')
    def one(*args, **kwargs):
        raise configs.ServerError()

    @patch('taxi.external.configs.get_by_ids')
    def several(*args, **kwargs):
        raise configs.ServerError()

    _make_param('TEST_P_WO_F')

    with pytest.raises(config.service.ConfigFileError):
        yield config.TEST_P_WO_F.get()
