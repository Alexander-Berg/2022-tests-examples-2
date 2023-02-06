"""Запуск тестов в Teamcity.

Структура директорий
--------------------
`wordir`
    |- src/
    |- test-report/
`base_env_dir`
    |- toxenv
    |- envs


Teamcity на каждую build configuration генерирует директорию, будем называть
ее `workdir`. Путь до директории не меняется между запусками (поведение тимсити
по умолчанию)

`base_env_dir` - базавая директория, где создаются/кэшируется virtualenv.
Новый virtualenv создается на каждое изменение ревизии директории с
python зависимостями. Передается из тимсити.

`workdir`/src/ - директорию куда клонируется git репозиторий. Тимсити сам
должен ее актуализировать и чистить мусор между сборками. Клонирование
настраивается в тимсити (Version Control Settings).

`workdir`/test-report/ - директория с xml файлами о статусах тестов. Тимсити
сам парсит файлы (Build Features -> XML report processing) и показывает в
своем ui количество тестов и их статусы

`base_env_dir`/envs/  -  директория с вирт. окружениеями python. Отдельная
директория выделена для того, чтобы не пересоздавать вирт. окружения на каждый
запуск тестов. Они не могут быть в `workdir`/src/, так как она чистится.

`base_env_dir`/toxenv/ - tox устанавливается в отдельное вирт. окружение, так
как на build agent он отсутсвует.
`workdir`/envs/<все прочие> - вирт. окружения прописанные в tox.ini, в отличии
от локальной разработки они не устанавливается в директории с гит
репозиторием (`workdir`/src/).

Обычно dmp_deps меняется редко и вирт. окружения не должны пересоздаваться.
Это очень сильно экономит время выполнения юнит тестов.

Цепочка вызова
--------------
teamcity build agent
-> tools/teamcity/tests/__main__.py
   -> tox
      -> tools/run_test_all_service.py
         -> pytest
"""

import os
import shlex

from tools.teamcity import tox_wrapper
from tools.teamcity.utils import get_project


def execute_tests(use_config, force_install=False):
    project = get_project(use_config=use_config)

    tox_args = shlex.split(os.environ.get('DMP_TOX_ARGS', ''))
    tox_extra_env = {}
    if use_config:
        tox_extra_env['TAXIDWH_DEV_CONFIG'] = project.config_file_path

    tox_wrapper.execute(project, tox_args, tox_extra_env, force_install)
