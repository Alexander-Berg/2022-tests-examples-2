import pytest

import mock
from pathlib import Path

from tools.doc.build import build as build_new, get_conf_dir, BuildParameters
from dmp_suite.file_utils import tempdir


@pytest.mark.enable_socket
@pytest.mark.prioritize
@mock.patch('dmp_suite.clickhouse.table.settings', mock.MagicMock(return_value='dummy'))
@mock.patch('dmp_suite.greenplum.table.get_dev_prefix_by_key', mock.MagicMock(return_value=''))
@mock.patch('dmp_suite.yt.task.logbroker.settings', mock.MagicMock(return_value='/taxi-dwh/dummy'))
def test_documentation_building(changed_services, changed_files, all_services_pythonpath):
    with all_services_pythonpath(), tempdir(prefix='taxi-dmp-doc-test-') as tmp:
        params = BuildParameters(
            cross_service_deps=False,
            render_tasks=True,
            render_domains=True,
            collect_task_graphs=False,
            collect_hnhm_graphs=False,
            use_external_doc=False,
            strict_mode=True,
            test_build=True,
        )

        # Если у нас изменился корневой сервис, то должна перестроиться вся документация.
        # Сами параметры запуска при этом не меняем, считаем, что `build` всегда будет запускать
        # полную сборку документации, если список измененных файлов пустой.
        force = 'dmp_suite' in changed_services or 'replication_rules' in changed_services
        if force:
            changed_files = []

        build_new(
            Path(tmp),
            get_conf_dir('daas'),
            params=params,
            changed_files=set(changed_files),
        )
