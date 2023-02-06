Настройка окружения
-------------------

Надо использовать taxi-python3 или собрать окружение самостоятельно::

  sudo apt install taxi-deps-py3-2

  ИЛИ

  ./setupenv.sh


Запуск тестов (direct)
----------------------

Testsuite основан на pytest_, запуск происходит через скрипт-обертку::

  .../logistic-dispatcher/testsuite$ ./runtests


Можно передать путь к конкретному файлу с тестами, можно выбрать только
некоторые тесты::

  ./runtests test_ping.py
  ./runtests -k test_ping

Запуск тестов (ya make)
-----------------------

::
   ya make -tt


Запуск тестов c GDB
-------------------


Тестьсьют можно запустить с фалгом --service-wait, с этим флагом testsuite не
сам поднимает сервис, а ждет, когда пользователь его запустит самостоятельно,
при этом показывает подсказку, как его запустить::

   ./runtests --service-wait

В другом терминале надо будет запустить сам сервис::

  gdb --args ../dispatcher/dispatcher ../dispatcher/configs/config_testsuite -V LogDir=logs/taxi-logistic-dispatcher -V BasePort=8080 -V ControllerPort=8888 -V HomeDir=/work -V MockserverPort=9999 -V MockserverHost=localhost --secdist secdist.json --secdist-service logistic-dispatcher

На MacOS лучше пользоваться lldb:
  lldb -- ../dispatcher/dispatcher ../dispatcher/configs/config_testsuite -V LogDir=logs/taxi-logistic-dispatcher -V BasePort=8080 -V ControllerPort=8888 -V HomeDir=/work -V MockserverPort=9999 -V MockserverHost=localhost --secdist secdist.json --secdist-service logistic-dispatcher

При запуске под дебаггером рекомендуется при запуске тестов указать бесконечный таймаут, чтобы тесты не падали по таймауту до завершения дебага::

   ./runtests --service-wait --service-timeout 1000000

Больше документации
-------------------

Многие рецепты таксишного тестсьюта будут работать и с ЛД:

https://wiki.yandex-team.ru/taxi/backend/testsuite/


.. _pytest: https://pytest.org/
