#!/bin/sh
curl https://github.yandex-team.ru/raw/taxi/notepad/master/custom_branches.md | tr '\n' ' ' | sed -r 's/```bash ([^`]+?) ```.*/\1/' > _run.sh
sh _run.sh
