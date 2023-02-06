import os
import re
from subprocess import Popen, PIPE

import pytest


@pytest.mark.skip(reason='падает по непонятной причине')
def test_pip_check(tap):
    with tap.plan(1):
        with Popen(["pip", "check"], stdout=PIPE) as process:
            (_, err) = process.communicate()

            tap.eq(process.wait(), 0, 'Проверка прошла успешно')
            if err:
                tap.diag(err)


def test_pip_requirements(tap):

    req = os.path.abspath("config/requirements/pip.txt")
    with open(req, "r") as file:
        required=file.readlines()
        if not required:
            tap.failed("Файл без зависимостей")

        required = [x.strip() for x in required]
        tap.ok(required, f"Список зависимостей получен из {req}")


    tap.plan(len(required) + 2)

    cmd = ["pip", "list", "--local", "--format", "columns"]
    with Popen(cmd, stdout=PIPE) as process:
        (stdout, err) = process.communicate()

        tap.eq(process.wait(), 0, 'Список установленных пакетов получен')
        if err:
            tap.diag(err)

        available = (stdout.splitlines())[2:]
        available = [x.decode().strip() for x in available]
        available = dict(re.split('\\s+', x, 1) for x in available)

        for row in required:
            (package, version) = re.split('[><=]+', row, 1)

            if package not in available:
                tap.failed(f"Пакет {package} {version} не установлен")
                continue

            tap.eq(version, available[package], f"{package} {version}")

    tap.done_testing()
