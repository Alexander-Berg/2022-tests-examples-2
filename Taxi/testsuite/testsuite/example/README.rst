`Вики testsuite <https://wiki.yandex-team.ru/taxi/backend/testsuite/#mongo>`_

`Раздел про работу с mongo <https://wiki.yandex-team.ru/taxi/backend/testsuite/#mongo>`_

`Раздел про работу с PostgreSQL <https://wiki.yandex-team.ru/taxi/backend/testsuite/#postgresql>`_

Запуск в virtualenv
===================

::

  virtualenv --python=python3.7 .venv
  . .venv/bin/activate
  pip install -r requirements.txt
  PYTHONPATH=submodules/testsuite pytest ./tests -vvs
