import os
import shutil

import pytest

from stall.scripts.dorblu import generate, replace_url


async def test_dorblu(tap):
    res_dir = 'tests/scripts/dorblu/results'
    expected_dir = 'tests/scripts/dorblu/expected'
    first_file_name = 'dorblu_file_first.yaml'
    second_file_name = 'dorblu_file_second.yaml'
    os.makedirs(res_dir, exist_ok=True)
    generate(
        config='tests/scripts/dorblu/dorblu_config.yaml',
        doc_root='tests/scripts/dorblu/doc_root',
        directory=res_dir
    )
    try:
        with tap.plan(5):
            for file_name in (first_file_name, second_file_name):
                expected_file = os.path.join(expected_dir, file_name)
                res_file = os.path.join(res_dir, file_name)
                tap.ok(os.path.exists(res_file), 'File generated')
                with open(res_file, 'r') as f_res, \
                        open(expected_file, 'r') as f_exp:
                    tap.eq_ok(
                        f_res.read(),
                        f_exp.read(),
                        'Generated correctly'
                    )
            tap.eq_ok(
                len(os.listdir(res_dir)),
                2,
                'Does not generate additional files'
            )
    finally:
        shutil.rmtree(res_dir)


def eq_files(received, expected, tap, description='Files are equal'):
    rec = received.split(sep='\n')
    exp = expected.split(sep='\n')
    with tap.subtest(None, description) as taps:
        for i, (rec_i, exp_i) in enumerate(zip(rec, exp)):
            taps.eq_ok(rec_i, exp_i, f'Line {i}')


@pytest.mark.parametrize('config,expected,doc_root', [
    (
        'dorblu_config_parameterized_url.yaml',
        'expected_parameterized',
        'doc_root',
    ),
    (
        'dorblu_config_extra.yaml',
        'expected_extra',
        'doc_root',
    ),
    (
        'dorblu_config_prepend.yaml',
        'expected_prepend',
        'doc_root',
    ),
    (
        'dorblu_config_skip.yaml',
        'expected_skip',
        'doc_root_skip',
    ),
    (
        'dorblu_config_override.yaml',
        'expected_override',
        'doc_root_override',
    ),
])
async def test_parameterized_dorblu(tap, config, expected, doc_root):
    res_dir = 'tests/scripts/dorblu/results'
    expected_dir = f'tests/scripts/dorblu/{expected}'
    os.makedirs(res_dir, exist_ok=True)
    generate(
        config=f'tests/scripts/dorblu/{config}',
        doc_root=f'tests/scripts/dorblu/{doc_root}',
        directory=res_dir
    )
    try:
        with tap:
            for file_name in os.listdir(expected_dir):
                expected_file = os.path.join(expected_dir, file_name)
                res_file = os.path.join(res_dir, file_name)
                tap.ok(os.path.exists(res_file), 'File generated')
                if not os.path.exists(res_file):
                    continue
                with open(res_file, 'r') as f_res, \
                        open(expected_file, 'r') as f_exp:
                    eq_files(
                        f_res.read(), f_exp.read(), tap,
                        description=f'File {file_name} equals to expected')
            tap.eq_ok(
                len(os.listdir(res_dir)),
                len(os.listdir(expected_dir)),
                'Does not generate additional files'
            )
    finally:
        shutil.rmtree(res_dir)


async def test_replace_url_filename(tap):
    with tap.plan(1, 'Фильтруем файлы по filename'):
        replaces = {
            'filename': {
                'replace': '/api/report_data/',
                'mask': '/api/*/'
            }
        }
        file = '/doc_root/api/filename'
        doc_root = '/doc_root/api'
        url = '/api/one/two/three'

        new_url = replace_url(doc_root, file, replaces, url)
        tap.eq(new_url, '/api/report_data/two/three', 'Замена по имени файла')


async def test_replace_url_filepath(tap):
    with tap.plan(1, 'Фильтруем файлы по filepath'):
        replaces = {
            'filepath/filename': {
                'replace': '/api/report_data/',
                'mask': '/api/*/'
            }
        }
        file = '/doc_root/api/filepath/filename'
        doc_root = '/doc_root/api'
        url = '/api/one/two/three'

        new_url = replace_url(doc_root, file, replaces, url)
        tap.eq(new_url, '/api/report_data/two/three', 'Замена по целому пути')


async def test_replace_url_only_wild(tap):
    with tap.plan(1, 'Заменяем * части url по маске'):
        replaces = {
            'filepath/filename': {
                'replace': '/api/report_data/',
                'mask': '/api/two/'
            }
        }
        file = '/doc_root/api/filepath/filename'
        doc_root = '/doc_root/api'
        url = '/api/two/one/three'

        new_url = replace_url(doc_root, file, replaces, url)
        tap.eq(new_url, new_url, 'Заменяются только *')


async def test_replace_url_wrong_filepath(tap):
    with tap.plan(1, 'Если файл не найден, то не меняем'):
        replaces = {
            'wrong-name': {
                'replace': '/api/report_data/',
                'mask': '/api/*/'
            }
        }
        file = '/doc_root/api/filename'
        doc_root = '/doc_root/api'
        url = '/api/one/two/three'

        new_url = replace_url(doc_root, file, replaces, url)
        tap.eq(new_url, new_url, 'Неверное имя файла')
