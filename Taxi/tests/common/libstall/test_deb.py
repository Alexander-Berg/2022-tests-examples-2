import os
from subprocess import Popen, PIPE

from stall import cfg


def test_deb_requirements(tap):
    if cfg('mode') == 'local':
        return

    req = os.path.abspath("config/requirements/deb.txt")
    with open(req, "r") as file:
        required=file.readlines()
        if not required:
            tap.failed("Файл без зависимостей")

        required = [x.strip() for x in required]
        tap.ok(required, f'Список зависимостей получен из {req}')

    tap.plan(len(required) + 1)

    for package in required:
        with Popen(["dpkg", "-s", package], stdout=PIPE) as process:
            (stdout, err) = process.communicate()

            if process.wait() != 0:
                tap.failed(f"{package} информация недоступна")
                continue

            if err:
                tap.diag(err)

            tap.like(stdout, 'Status: install ok installed', package)

    tap.done_testing()
