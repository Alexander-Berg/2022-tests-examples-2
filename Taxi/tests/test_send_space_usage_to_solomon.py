import datetime
import socket
from typing import NamedTuple

import freezegun
import pytest
import pytz

import send_space_usage_to_solomon

NOW = datetime.datetime(2020, 2, 15, tzinfo=pytz.timezone('Europe/Moscow'))
TIMESTAMP_NOW = int(NOW.timestamp())

DOCKER_OUTPUT = (
    """
131.8GB
10.17MB
0B
0B
""".lstrip()
)
DEFAULT_DF_OUTPUT = (
    """
Filesystem        1B-blocks         Used    Available Use% Mounted on
/dev/vda       549493252096 253034377216 296442097664  47% /
""".lstrip()
)
HOSTNAME = 'some-host'


class Params(NamedTuple):
    du_output: str
    solomon_data: dict
    df_output: str = DEFAULT_DF_OUTPUT


# pylint: disable=too-many-lines
@freezegun.freeze_time(NOW)
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(
            Params(
                du_output="""
132547084671    /home/
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 132547084671,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                    ],
                },
            ),
            id='simple_report',
        ),
        pytest.param(
            Params(
                du_output="""
5606163720      /home/buildfarm/teamcity/projects/yandex-taxi-build/
4096    /home/buildfarm/teamcity/projects/docker-integration-tests-cores/
52356 /home/buildfarm/teamcity/projects/docker-integration-tests-cache/ltocache
439310405       /home/buildfarm/buildAgent/
1161340585      /home/buildfarm/.ccache/
2282317 /home/buildfarm/.mypy_cache/
87128707567     /home/buildfarm/teamcity/projects/
109458684       /home/buildfarm/
351770092       /home/
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 52356,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 4096,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 5606163720,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 87128707567,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 2282317,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 439310405,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 1161340585,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 109458684,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 351770092,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 26425117394,
                        },
                    ],
                },
            ),
            id='real_report',
        ),
        pytest.param(
            Params(
                du_output="""
1161336489 /home/buildfarm/.arc/
2282317 /home/buildfarm/arc/
81799919794 /home/buildfarm/.ya/
109453805586 /home/buildfarm/
325125089355 /home/
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 1161336489,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 2282317,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 81799919794,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 109453805586,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 325125089355,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                    ],
                },
            ),
            id='arcadia_report',
        ),
        pytest.param(
            Params(
                du_output="""
88634662891     /home/buildfarm/teamcity/projects/
36864   /home/buildfarm/teamcity/projects/docker-integration-tests-cores/
182614684157    /home/buildfarm/
447104062442    /home/
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 36864,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 88634662891,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 182614684157,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 447104062442,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                    ],
                },
            ),
            id='cores_report',
        ),
        pytest.param(
            Params(
                du_output="""
88634662891     /home/buildfarm/teamcity/projects/
73728   /home/buildfarm/teamcity/projects/docker-integration-tests-cores/
16384   /home/buildfarm/teamcity/projects/docker-tests-cores/
182614684157    /home/buildfarm/
447104062533       /home/
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 73728,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 16384,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 88634662891,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 182614684157,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 447104062533,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                    ],
                },
            ),
            id='several_cores_report',
        ),
        pytest.param(
            Params(
                du_output="""
16384   /home/buildfarm/teamcity/projects/docker-integration-tests-cores/
28672   /home/buildfarm/teamcity/projects/docker-tests-cores/
4096    /home/buildfarm/teamcity/projects/yandex-taxi-build/
92692008227     /home/buildfarm/teamcity/projects/
4096    /home/buildfarm/.mypy_cache/
1934063239      /home/buildfarm/buildAgent/
999889064       /home/buildfarm/.arc/
3618884614      /home/buildfarm/arc/
177353923655    /home/buildfarm/.ya/
2581804140      /home/buildfarm/
1191531410      /home/
""".lstrip(),
                df_output="""
Filesystem        1B-blocks         Used    Available Use% Mounted on
udev            24251518976            0  24251518976   0% /dev
tmpfs            4853444608    550064128   4303380480  12% /run
/dev/vda       549493252096 436578209792 112898265088  80% /
tmpfs           24267214848        12288  24267202560   1% /dev/shm
tmpfs               5242880            0      5242880   0% /run/lock
tmpfs           24267214848            0  24267214848   0% /sys/fs/cgroup
tmpfs              33554432         8192     33546240   1% /run/porto/kvs
tmpfs              33554432            0     33554432   0% /run/porto/pkvs
tmpfs             134217728         4096    134213632   1% /place/vartmp/skynet
""".lstrip(),
                solomon_data={
                    'sensors': [
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cache/ltocache'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-integration-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 16384,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'docker-tests-cores/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 28672,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                    'yandex-taxi-build/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 4096,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': (
                                    '/home/buildfarm/teamcity/projects/'
                                ),
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 92692008227,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.mypy_cache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 4096,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/buildAgent/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 1934063239,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ccache/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 0,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 999889064,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/arc/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 3618884614,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/.ya/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 177353923655,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/buildfarm/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 2581804140,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/var/lib/docker/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 131810170000,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/home/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 1191531410,
                        },
                        {
                            'kind': 'IGAUGE',
                            'labels': {
                                'sensor': 'DiskUsage',
                                'space_usage': '/',
                                'host': 'some-host',
                            },
                            'ts': 1581715800,
                            'value': 24395882195,
                        },
                    ],
                },
            ),
            id='real_arcadia_mount',
        ),
    ],
)
def test_send_space_usage(params, monkeypatch, commands_mock, patch_requests):
    monkeypatch.setattr(socket, 'gethostname', lambda: HOSTNAME)

    @commands_mock('du')
    def disk_usage(args, **kwargs):
        return params.du_output

    @commands_mock('docker')
    def docker(args, **kwargs):
        return DOCKER_OUTPUT

    @commands_mock('df')
    def file_system_disk_usage(args, **kwargs):
        return params.df_output

    @patch_requests(send_space_usage_to_solomon.SOLOMON_PULL_URL)
    def solomon_request(method, url, **kwargs):
        return patch_requests.response()

    monkeypatch.setattr('os.path.exists', lambda x: True)

    send_space_usage_to_solomon.main()

    assert len(disk_usage.calls) == 1
    assert len(docker.calls) == 1
    assert len(file_system_disk_usage.calls) == 1

    solomon_calls = solomon_request.calls
    assert len(solomon_calls) == 1
    solomon_data = solomon_calls[0]['kwargs']['json']
    solomon_data['sensors'].sort(
        key=lambda x: len(x['labels']['space_usage']), reverse=True,
    )
    assert solomon_data == params.solomon_data
