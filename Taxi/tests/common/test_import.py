# pylint: disable=redefined-outer-name,too-many-locals,global-statement
# pylint: disable=too-many-nested-blocks

from ast import parse, walk, Import, ImportFrom
import glob
import os

import pytest

# Запрещаем использование модулей внутри основной ветки проекта.
# ПОЖАЛУЙСТА НЕ НАДО ДОБАВЛЯТЬ ИСКЛЮЧЕНИЯ!
# ДЛЯ ВСЕГО ЧТО ЗДЕСЬ ПЕРЕЧИСЛЕНО ЕСТЬ РАБОТАЮЩАЯ АЛЬТЕРНАТИВА (смотри комменты)
BLACKLIST = {
    # Отладки в проде быть не должно
    'pprint': {
        'whitelist': {
            # В этом модуле он нужен
            'stall/debug.py',

            # TODO: это надо вычистить
            'scripts/dev/move_from_shelf_to_shelf.py',
            'scripts/dev/move_to_trash_stocks.py',
            'scripts/dev/revert_move_to_trash.py',
        },
    },

    # Для работы с часовыми поясами есть специальная библиотека
    # from libstall.util import time2time, time2iso_utc, tzone, ...
    'pytz': {
        'whitelist': {
            # TODO: это надо вычистить в пользу libstall.util
            'stall/model/courier_shift.py',
            'stall/model/order_business/'
            'check_valid_short/processing.py',
            'stall/model/sampling_condition.py',
            'stall/model/schet_task.py',
            'scripts/dev/fill_schets.py',
        },
    },
    'dateparser': {},
    'dateutil': {},
}


@pytest.fixture
def project_basedir():
    """Вернет базовую директорию проекта"""
    def _wrapper():
        base = os.path.dirname(__file__)
        while base:
            base = os.path.dirname(base)
            if base.endswith('/tests'):
                base = os.path.dirname(base)
                break
        return base
    return _wrapper


@pytest.fixture
def project_all_py(project_basedir):
    """Найдет все *.py файлы в заданной папаке"""
    def _wrapper(path: str):
        base = project_basedir()
        search = os.path.join(base, path)
        files = glob.glob(f'{search}/**/*.py', recursive=True)
        files.sort()
        return files

    return _wrapper


@pytest.mark.parametrize('path', [
    'stall',
    'scripts',
])
async def test_import(tap, path, load_file, project_basedir, project_all_py):
    with tap:
        global BLACKLIST

        base = project_basedir()
        files = project_all_py(path)

        for file in files:
            try:
                filepath = file.replace(base + os.path.sep, "")

                src = load_file(file)
                if not src:
                    tap.passed(filepath)
                    continue

                tree = parse(src)

                fail = False
                for node in walk(tree):
                    if not isinstance(node, (Import, ImportFrom)):
                        continue

                    for alias in node.names:
                        if alias.name in BLACKLIST:
                            item = BLACKLIST[alias.name]
                            whitelist = item.get('whitelist', {})
                            if filepath not in whitelist:
                                tap.failed(
                                    f'{filepath} cодержит запрещенный'
                                    f' модуль {alias.name}'
                                )
                                fail = True

                if not fail:
                    tap.passed(filepath)
            except Exception as exc:
                tap.failed(f'{filepath} не может быть проверен {exc}')

        tap.done_testing()
