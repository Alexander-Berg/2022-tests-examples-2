import os

from unittest import mock

import tempfile

from dmp_suite.overlay_agent import copy_system_configs


def _read_files_with_content(directory):
    results = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(dirpath, filename)
            with open(full_path) as f:
                content = f.read().strip()
                rel_path = os.path.relpath(full_path, directory)
                results.append((rel_path,content))

    return results


def test_system_configs_copying():
    # Проверим, что функция копирования перенесёт в destination_dir
    # только файлы с суффиксом соответствующим текущему окружению
    # или без суффикса.
    test_configs_dir = os.path.join(
        os.path.dirname(__file__),
        'test-configs',
    )
    with tempfile.TemporaryDirectory() as target_dir, \
         mock.patch('dmp_suite.overlay_agent.get_current_environment', return_value='production'):
        files_to_execute = copy_system_configs(test_configs_dir, target_dir)

        copied_files = _read_files_with_content(target_dir)
        copied_files.sort()

        expected_files = [
            ('etc/yandex/other-service/config.yaml', 'Этот файл для прода.'),
            ('etc/yandex/statbox-push-client/custom/dmp.yaml', 'just a test file'),
        ]
        assert copied_files == expected_files

        # В двух директориях есть файл .restart, но только один из них executable.
        # Тот что не executable, должен быть проигнорирован:
        dot_restart = os.path.join(
            test_configs_dir,
            'etc',
            'yandex',
            'statbox-push-client',
            'custom',
            '.restart',
        )
        assert files_to_execute == [dot_restart]

        # При повторном запуске копирования, функция не должна возвращать
        # скрипт для перезапуска, ведь конфиги не поменялись и рестартить ничего не нужно:
        files_to_execute = copy_system_configs(test_configs_dir, target_dir)
        assert files_to_execute == []

        # Но если мы поменяем контент в целевой директории, то
        # при новом копировании конфигов, файл .restart должен быть запущен:
        file_to_change = os.path.join(
            target_dir,
            'etc',
            'yandex',
            'statbox-push-client',
            'custom',
            'dmp.yaml',
        )
        with open(file_to_change, 'w') as f:
            f.write('Changed content')

        files_to_execute = copy_system_configs(test_configs_dir, target_dir)
        assert files_to_execute == [dot_restart]

        # Однако если мы поменяем конфиг в другой директории, не относящейся к dot_restart,
        # то он перезапускаться не будет:
        file_to_change = os.path.join(
            target_dir,
            'etc',
            'yandex',
            'other-service',
            'config.yaml',
        )
        with open(file_to_change, 'w') as f:
            f.write('Changed content')

        files_to_execute = copy_system_configs(test_configs_dir, target_dir)
        assert files_to_execute == []


