from typing import Callable

import pytest

from taxi.util import host_info


@pytest.mark.parametrize(
    'file_bodies, success_numbers, type_rollout, expected_result',
    (
        (
            ['groups=taxi_prestable_all,taxi_all'],
            [0],
            host_info.HostType.CONDUCTOR,
            host_info.HostInfo(
                host='host_name',
                cgroups=['taxi_prestable_all', 'taxi_all'],
                ngroups=[],
                is_prestable=True,
            ),
        ),
        (
            ['groups=taxi_all'],
            [0],
            host_info.HostType.CONDUCTOR,
            host_info.HostInfo(
                host='host_name',
                cgroups=['taxi_all'],
                ngroups=[],
                is_prestable=False,
            ),
        ),
        (
            ['pre_stable\n'],
            [0],
            host_info.HostType.CLOWNDUCTOR,
            host_info.HostInfo(
                host='host_name',
                cgroups=[],
                ngroups=['pre_stable'],
                is_prestable=True,
            ),
        ),
        (
            ['stable\n'],
            [0],
            host_info.HostType.CLOWNDUCTOR,
            host_info.HostInfo(
                host='host_name',
                cgroups=[],
                ngroups=['stable'],
                is_prestable=False,
            ),
        ),
        (
            ['stable\n'],
            [0],
            host_info.HostType.UNKNOWN,
            host_info.HostInfo(
                host='host_name',
                cgroups=[],
                ngroups=['stable'],
                is_prestable=False,
            ),
        ),
        (
            [None, 'groups=taxi_all'],
            [1],
            host_info.HostType.UNKNOWN,
            host_info.HostInfo(
                host='host_name',
                cgroups=['taxi_all'],
                ngroups=[],
                is_prestable=False,
            ),
        ),
        (
            ['\n', 'groups=taxi_all'],
            [1],
            host_info.HostType.UNKNOWN,
            host_info.HostInfo(
                host='host_name',
                cgroups=['taxi_all'],
                ngroups=[],
                is_prestable=False,
            ),
        ),
        (
            ['stable\n', 'groups=taxi_all'],
            [0, 1],
            host_info.HostType.UNKNOWN,
            host_info.HostInfo(
                host='host_name', cgroups=[], ngroups=[], is_prestable=None,
            ),
        ),
        (
            [],
            [],
            host_info.HostType.UNKNOWN,
            host_info.HostInfo(
                host='host_name', cgroups=[], ngroups=[], is_prestable=None,
            ),
        ),
        (
            [],
            [],
            None,
            host_info.HostInfo(
                host='host_name', cgroups=[], ngroups=[], is_prestable=None,
            ),
        ),
    ),
)
def test(
        monkeypatch,
        file_bodies,
        success_numbers,
        type_rollout,
        expected_result,
):
    class _T:
        number = -1

    def _read_and_parse_file(
            path: str, parse_function: Callable[[str], host_info.ParseResult],
    ) -> host_info.ParseResult:
        _T.number += 1
        if _T.number in success_numbers:
            return parse_function(file_bodies[_T.number])
        raise FileNotFoundError

    monkeypatch.setattr(
        host_info, '_read_and_parse_file', _read_and_parse_file,
    )
    monkeypatch.setattr(host_info, '_get_host_name', lambda: 'host_name')

    result = host_info.get_host_info(type_rollout=type_rollout)
    assert result == expected_result
