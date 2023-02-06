import typing
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from stq_agent_py3.monitoring import stq_stats


class Args(typing.NamedTuple):
    prepared_messages: Dict[str, Tuple[int, str]]
    stq_configs: List[Dict]
    service: str
    is_command: bool
    expected_status: int
    expected_messages: str


@pytest.mark.parametrize(
    'prepared_messages, stq_configs, service, is_command, '
    'expected_status, expected_messages',
    [
        pytest.param(
            *Args(
                prepared_messages={
                    'service': (stq_stats.STATUS_WARNING, '123'),
                },
                stq_configs=[{'_id': 'service'}],
                service='service',
                is_command=True,
                expected_status=stq_stats.STATUS_WARNING,
                expected_messages='WARN: 123',
            ),
            id='warning for command',
        ),
        pytest.param(
            *Args(
                prepared_messages={
                    'service': (stq_stats.STATUS_WARNING, '123'),
                },
                stq_configs=[{'_id': 'service'}],
                service='service',
                is_command=False,
                expected_status=stq_stats.STATUS_OK,
                expected_messages='OK',
            ),
            id='ingore non-critical warning for common',
        ),
        pytest.param(
            *Args(
                prepared_messages={
                    'service': (stq_stats.STATUS_WARNING, '123'),
                },
                stq_configs=[
                    {'_id': 'service', 'monitoring': {'is_critical': True}},
                ],
                service='service',
                is_command=False,
                expected_status=stq_stats.STATUS_WARNING,
                expected_messages='WARN: 123',
            ),
            id='warning for common of critical queue',
        ),
    ],
)
def test(
        prepared_messages,
        stq_configs,
        service,
        is_command,
        expected_status,
        expected_messages,
):
    assert stq_stats.get_stq_status_and_message(
        prepared_messages=prepared_messages,
        stq_configs=stq_configs,
        service=service,
        is_command=is_command,
        verbose_log_messages=True,
    ) == (expected_status, expected_messages)
