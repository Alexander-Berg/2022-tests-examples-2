"""
Этот модуль содержит примеры и рекомендации, касающиеся работы с настройками в тестах.

В ходе выполнения тестов получение настроек, как и обычно, происходит через функцию init_py_env.settings(...).

Отличие состоит в том, что значения настроек могут неявно подменяться в зависимости от контекста.
Кроме того, в тестах имеется возможность явно переопределять некоторые настройки.
"""
import contextlib

import pytest
import mock

from dmp_suite.py_env.settings_setup import (
    SecdistPathsCollectingProxy,
    _add_intermediate_keys,
    _make_flat_with_intermediate_keys,
)
from init_py_env import settings


def unit_test_settings_enabled():
    return settings("yt.default_cluster", default=None) == "dummy"


def assert_settings_patchable():
    assert "answer_to_everything" not in settings
    with settings.patch(answer_to_everything=42):
        assert "answer_to_everything" in settings
    assert "answer_to_everything" not in settings


def test_unit_test():
    """
    При выполнении unit-теста почти все настройки удаляются; остаётся фиксированный набор.

    Значения можно добавлять/подменять с помощью init_py_env.settings.patch(...)
    """
    assert unit_test_settings_enabled()
    assert_settings_patchable()


@pytest.mark.slow
def test_slow_test():
    """
    При выполнении интеграционных тестов исходные значения настроек в основном сохраняются.

    Префиксы для YT подменены на случайные.

    Подмена настроек работает точно так же, как и в случае unit-тестов.
    """
    assert not unit_test_settings_enabled()
    assert_settings_patchable()


@pytest.fixture(scope="function")
def function_fixture():
    """
    При выполнении фикстуры со scope == 'function' настройки будут такие же, как и в самом тесте.
    """
    with settings.patch(key_added_by_function_fixture=42):
        yield unit_test_settings_enabled()


def test_function_fixture_unit_test(function_fixture):
    assert function_fixture
    assert "key_added_by_function_fixture" in settings


@pytest.mark.slow
def test_function_fixture_slow_test(function_fixture):
    assert not function_fixture
    assert "key_added_by_function_fixture" in settings


def assert_settings_disabled():
    with pytest.raises(RuntimeError):
        settings("yt.default_cluster")
    with pytest.raises(RuntimeError):
        with settings.patch(answer_to_everything=42):
            pass


@pytest.fixture(scope="module")
def unit_module_fixture(unit_test_settings):
    """
    При выполнении фикстуры со scope != 'function' настройки по умолчанию отключены.

    При необходимости использования настроек в самой фикстуре надо
    воспользоваться контекстным менеджером unit_test_settings()
    либо slow_test_settings(), в зависимости от того, какие настройки нужны.

    Фикстуре не рекомендуется оставлять настройки включенными и/или пропатченными
    после завершении собственной инициализации.
    Иными словами, не надо делать yield внутри контекстного менеджера, меняющего настройки.

    Предпочтительней сохранить в фикстуре необходимый патч и вернуть его значение,
    и применить его к настройкам уже в самих тестах (как показано здесь)
    либо в фикстуре со scope == 'function'.

    Прчина в том, что фикстуры со scope != 'function' уничтожаются отложенно (конкретно, при выходе из скоупа);
    это означает, что при запуске теста могут быть активны не только фикстуры, которые в нём используются,
    но и другие фикстуры, которые ещё не дожили до своего уничтожения.
    Поэтому не следует в фикстурах со scope != 'function' создавать глобальные побочные эффекты.
    """
    patch = dict(key_added_by_unit_module_fixture=42)

    assert_settings_disabled()
    with unit_test_settings():
        assert unit_test_settings_enabled()
        assert_settings_patchable()
    assert_settings_disabled()

    yield patch


def test_fixtures_unit_test(unit_module_fixture, function_fixture):
    with settings.patch(**unit_module_fixture):
        assert "key_added_by_unit_module_fixture" in settings
        assert "key_added_by_function_fixture" in settings


@pytest.fixture(scope="module")
def slow_module_fixture(slow_test_settings):
    patch = dict(key_added_by_slow_module_fixture=42)

    assert_settings_disabled()
    with slow_test_settings():
        assert not unit_test_settings_enabled()
        assert_settings_patchable()
    assert_settings_disabled()

    yield patch


@pytest.mark.slow
def test_fixtures_slow_test(slow_module_fixture, function_fixture):
    with settings.patch(**slow_module_fixture):
        assert "key_added_by_slow_module_fixture" in settings
        assert "key_added_by_function_fixture" in settings


def test_usual_secrets_should_not_be_collected(function_fixture):
    settings_proxy = SecdistPathsCollectingProxy(settings)
    # Так как данные собираются в атрибут класса, то
    # лучше в начале теста его почистить, чтобы не было флапов:
    SecdistPathsCollectingProxy.used_keys.clear()

    assert "key_added_by_function_fixture" in settings_proxy

    assert settings_proxy("key_added_by_function_fixture") == 42

    info = settings_proxy.info("key_added_by_function_fixture")
    assert info == '<DictSettingsSource, name=PatchSettingsSource>'
    assert len(SecdistPathsCollectingProxy.used_keys) == 0


def test_settings_proxy_on_intermediate_keys():
    # Наши настройки умеют отдавать подмножество значений по ключу-префиксу.
    # Например, если в кофиге есть ключ:
    test_settings = {
        'mongodb': {
            'connections': {
                'one': 1,
                'two': 2,
            }
        }
    }
    with settings.patch(**test_settings):
        settings_proxy = SecdistPathsCollectingProxy(settings)
        # Смоделируем ситуацию, когда в новых настройках нет
        # данных про монговские коннекты. В таком случае должен
        # залоггироваться ворнинг:
        settings_proxy._secret_config = {'mongodb.connections': []}

        # Если мы запросили все соединения монги,
        settings_proxy('mongodb.connections')
        # то запись об этом будет сохранена в атрибут класса
        SecdistPathsCollectingProxy.used_keys == {'mongodb.connections'}


def test_intermediate_keys_adder():
    initial = {
        "mongodb.connections.first": 1,
        "mongodb.connections.second": 2,
    }
    result = _add_intermediate_keys(initial)
    expected = {
        "mongodb": {
            "connections": {
                "first": 1,
                'second': 2,
            },
        },
        "mongodb.connections": {
            "first": 1,
            'second': 2,
        },
        "mongodb.connections.first": 1,
        "mongodb.connections.second": 2,
    }
    assert result == expected
