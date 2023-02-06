from subprocess import Popen, PIPE

import pytest


@pytest.mark.parametrize('font', ['YSText-Regular', 'YSDisplay-Regular'])
async def test_render_html(tap, font):
    with tap.plan(2, f'Проверка доступности шрифта "{font}"'):
        process = Popen(["fc-match", font], stdout=PIPE)
        (stdout, err) = process.communicate()

        tap.eq(process.wait(), 0, 'Подходящих шрифтов')
        if err:
            tap.diag(err)

        stdout = stdout.decode().strip()
        tap.like(stdout, font, f'Шрифт найден: {stdout}')
