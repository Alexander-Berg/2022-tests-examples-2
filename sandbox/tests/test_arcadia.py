from sandbox.projects.yabs.qa.utils.arcadia import get_arcadia_file_extension, get_arcanum_url

import pytest


@pytest.mark.parametrize(['oneshot_path', 'extension'], [
    ('//arcadia.yandex.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/BSSERVER-123_1560423613.sql', '.sql'),
    ('//arcadia.yandex.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/main.py', '.py'),
    ('//arcadia.yandex.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/main.py@12345', '.py'),
    ('//arcadia.yandex.ru/arc/trunk/arcadia/junk/oneshot.py@12345', '.py'),
    ('//arcadia.yandex.ru/arc/trunk/arcadia/junk/oneshot', ''),
    ('', ''),
    ('helloworld', ''),
])
def test_get_arcadia_file_extension(oneshot_path, extension):
    assert get_arcadia_file_extension(oneshot_path) == extension


@pytest.mark.parametrize(['arcadia_url', 'arcanum_url'], [
    (
        '//arcadia.yandex.ru/arc/trunk/arcadia/junk/oneshot.py',
        'https://a.yandex-team.ru/arc/trunk/arcadia/junk/oneshot.py'
    ),
    (
        '//arcadia.yandex.ru/arc/trunk/arcadia/junk/oneshot.py@12345',
        'https://a.yandex-team.ru/arc/trunk/arcadia/junk/oneshot.py?rev=12345'
    ),
    (
        '//arcadia.yandex.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/BSSERVER-123_1560423613.sql',
        'https://a.yandex-team.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/BSSERVER-123_1560423613.sql'
    ),
    (
        '//arcadia.yandex.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/BSSERVER-123_1560423613.sql@12345',
        'https://a.yandex-team.ru/robots/trunk/yabs/one-shot-scripts/BSSERVER-123/BSSERVER-123_1560423613.sql?rev=12345'
    ),

])
def test_get_arcanum_url(arcadia_url, arcanum_url):
    assert get_arcanum_url(arcadia_url) == arcanum_url
