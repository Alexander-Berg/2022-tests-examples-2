# pylint: disable=redefined-outer-name
import copy

import pytest

from taxi import translations
from taxi.pytest_plugins import service


pytest_plugins = ['taxi.pytest_plugins.stq_agent']
DELETE_FIELD = object()


def pytest_configure(config):
    config.addinivalue_line('markers', 'settings: settings')


@pytest.fixture
def config_patcher(monkeypatch):
    def patcher(**kwargs):
        for config_key, value in kwargs.items():
            monkeypatch.setattr(
                'taxi_corp_admin.config.Config.{}'.format(config_key), value,
            )

    return patcher


@pytest.fixture
def settings_patcher(monkeypatch):
    def patcher(**kwargs):
        for config_key, value in kwargs.items():
            monkeypatch.setattr(
                'taxi_corp_admin.settings.{}'.format(config_key), value,
            )

    return patcher


@pytest.fixture(autouse=True)
def _config(request, config_patcher):
    all_kwargs = {}
    markers = request.node.iter_markers('config')
    for marker in markers:
        all_kwargs.update(marker.kwargs)
    if all_kwargs:
        config_patcher(**all_kwargs)


@pytest.fixture(autouse=True)
def _settings(request, settings_patcher):
    all_kwargs = {}
    markers = request.node.iter_markers('settings')
    for marker in markers:
        all_kwargs.update(marker.kwargs)
    if all_kwargs:
        settings_patcher(**all_kwargs)


@pytest.fixture()
def autotranslations(monkeypatch):
    def _get_string(self, key, language, num=None):
        items = [key]
        if language != 'ru':
            items.append(language)
        if language == 'no_translation':
            raise translations.TranslationNotFoundError
        if num is not None:
            items.append(num)
        return ' '.join(items)

    monkeypatch.setattr(
        'taxi.translations.TranslationBlock.get_string', _get_string,
    )


def _patch_doc(base_doc: dict, template: dict) -> dict:
    """
    The function updates the base document in a predetermined pattern.
    The template is a dictionary. The key can be written through the point.
    If the value is specified None, then this field is deleted.

    Example:
        >>> base = {
        ...             'foo': {
        ...                 'bar': {
        ...                     'a': 1,
        ...                     'b': 2
        ...                 }
        ...             }
        ...         }
        >>> _patch_doc(base, {'foo.bar.a': 42, 'foo.bar.b': None})
        {'foo': {'bar': {'a': 42}}}
    """
    result = copy.deepcopy(base_doc)
    for key, value in template.items():
        doc = result
        keys = key.split('.')
        for part in keys[:-1]:
            doc = doc[part]
        if DELETE_FIELD == value:
            del doc[keys[-1]]
        else:
            doc[keys[-1]] = value
    return result


@pytest.fixture
def patch_doc():
    return _patch_doc


@pytest.fixture
async def taxi_corp_admin_app(
        loop, db, simple_secdist, autotranslations, configs_mock,
):
    from taxi_corp_admin import app

    simple_secdist['settings_override']['STARTRACK_API_TOKEN'] = 'TOKEN'

    yield await app.create_app(loop=loop)


@pytest.fixture
async def taxi_corp_admin_client(aiohttp_client, taxi_corp_admin_app):
    from taxi_corp_admin.util import hdrs

    return await aiohttp_client(
        taxi_corp_admin_app,
        headers={
            hdrs.X_YATAXI_API_KEY: 'test_api_key',
            hdrs.X_YANDEX_LOGIN: 'test_login',
            hdrs.X_YANDEX_UID: 'test_uid',
        },
    )


@pytest.fixture(autouse=True)
def mock_handle_error(patch):
    @patch('taxi_corp_admin.api.middlewares.handle_exception')
    def _handle_error(error, request):
        raise error


@pytest.fixture
def trial_base_patch(patch):
    MOCK_ID = 'mock_id'  # pylint: disable=invalid-name

    @patch('taxi.clients.passport.PassportClient.get_info_by_uid')
    async def _get_info_by_uid(*args, **kwargs):
        return {'login': 'company_login'}

    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(*args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi_corp_admin.api.common.clientinfo.create_unique_id')
    def _create_client_id():
        return MOCK_ID

    @patch('taxi_corp_admin.api.common.corp_manager.create_role_id')
    def _create_cabinet_only_role(*args, **quargs):
        return MOCK_ID

    @patch(
        'taxi_corp_admin.api.common.'
        'trial_clients_helper.create_draft_request_id',
    )
    def _create_draft_request_id():
        return MOCK_ID


@pytest.fixture
def drive_patch(patch):
    @patch('taxi.clients.drive.DriveClient.create_organization')
    async def _create_organization(*args, **kwargs):
        return 230

    @patch('taxi.clients.drive.DriveClient.update_description')
    async def _update_description(*args, **kwargs):
        pass

    @patch('taxi.clients.drive.DriveClient.descriptions')
    async def _description(*args, **kwargs):
        return {'accounts': [{'name': 'default', 'meta': {'parent_id': 123}}]}


service.install_service_local_fixtures(__name__)
