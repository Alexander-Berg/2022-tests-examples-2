import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.renderers import client_tariff_description
from taxi.util import useragent


@pytest.mark.filldb(_fill=False)
@pytest.mark.translations([
    ('client_messages', 'mainscreen.description_econom', 'en', 'Renault'),
    ('tariff', 'name.econom', 'en', 'Economy'),
])
def test_wrapper_object():
    settings_obj = dbh.tariff_settings.Doc()
    settings_obj.home_zone = 'moscow'
    settings_obj.categories = []
    first_obj = settings_obj.categories.new()
    first_obj.service_levels = [50]
    first_obj.category_name = 'econom'
    first_obj.tanker_key = 'name.econom'

    csw = client_tariff_description.CategorySettingsView(settings_obj, 'en')
    wrapped_objects = list(csw.all_categories())
    assert 1 == len(wrapped_objects)
    assert 'Economy' == wrapped_objects[0].name()
    assert 'Renault' == wrapped_objects[0].cars()
    assert ['Renault'] == wrapped_objects[0].cars_list()
    assert [50] == wrapped_objects[0].service_levels

    csw_only_econom = client_tariff_description.CategorySettingsView(
        settings_obj, 'en', allowed_categories=["econom"])
    wrapped_objects_2 = list(csw_only_econom.all_categories())
    assert 1 == len(wrapped_objects_2)

    csw_only_vip = client_tariff_description.CategorySettingsView(
        settings_obj, 'en', allowed_categories=["vip"])
    wrapped_objects_3 = list(csw_only_vip.all_categories())
    assert 0 == len(wrapped_objects_3)


@pytest.mark.parametrize(
    'can_be_default,view_kwargs,expected_result', [
        (False, {}, False),
        (True, {}, True),
        (True, {'express_can_be_default': False}, False),
        (False, {'express_can_be_default': False}, False),
        (False, {'express_can_be_default': True}, False),
        (True, {'express_can_be_default': True}, True),
    ]
)
@pytest.mark.filldb(_fill=False)
def test_view_express_can_be_default(
        can_be_default, view_kwargs, expected_result):
    settings_obj = dbh.tariff_settings.Doc()
    settings_obj.home_zone = 'moscow'
    settings_obj.categories = []
    first_obj = settings_obj.categories.new()
    first_obj.category_name = 'express'
    first_obj.tanker_key = 'name.econom'
    first_obj.can_be_default = can_be_default

    csw = client_tariff_description.CategorySettingsView(
        settings_obj, 'en', **view_kwargs
    )
    wrapped_objects = list(csw.all_categories())
    assert 1 == len(wrapped_objects)
    assert wrapped_objects[0].can_be_default == expected_result


@pytest.mark.parametrize(
    'client_ua,expected_express_can_be_default',
    [
        ('yandex-taxi/3.15.6 Android/10.11.12', True),
        ('yandex-taxi/3.15.5 Android/10.11.12', True),
        ('yandex-taxi/3.10.1 Android/10.11.12', False),
        ('ru.yandex.ytaxi/3.55.3 (iPhone; iPhone7,1; iOS 9.1; Darwin)', True),
        ('ru.yandex.ytaxi/3.55.2 (iPhone; iPhone7,1; iOS 9.1; Darwin)', True),
        ('ru.yandex.ytaxi/3.50.2 (iPhone; iPhone7,1; iOS 9.1; Darwin)', False),
    ]
)
@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_category_settings_view(
        client_ua, expected_express_can_be_default, patch, monkeypatch):
    @patch('taxi.config.get')
    @async.inline_callbacks
    def config_get(varname):
        assert varname == 'EXPRESS_CAN_BE_DEFAULT_MINVERSION'
        yield
        async.return_value({
            'iphone': {
                'version': (3, 55, 2)
            },
            'android': {
                'version': (3, 15, 5)
            },
        })

    class DummyCSW:
        def __init__(self, tariffs_settings, locale,
                     express_can_be_default=True, categories=()):
            self.express_can_be_default = express_can_be_default

    monkeypatch.setattr(
        client_tariff_description, 'CategorySettingsView', DummyCSW)

    settings_obj = dbh.tariff_settings.Doc()
    settings_obj.home_zone = 'moscow'
    settings_obj.categories = []

    client_app = useragent.ClientApp(client_ua)
    csw = yield client_tariff_description.category_settings_view(
        settings_obj, 'ru', client_app)
    assert csw.express_can_be_default == expected_express_can_be_default
