import logging
import typing

from utils import convert_date_to_int

from .dataset import Dataset

logger = logging.getLogger(__name__)


def _parse_status_text(status_text: str) -> str:
    if status_text.startswith('Tests failed'):
        return 'Tests failed'
    if status_text.startswith('Conflicts with develop'):
        return 'Conflicts with develop'
    if status_text.startswith('Execution timeout'):
        return 'Execution timeout'
    return 'Build Step Failed'


class TestsBuildsDataset(Dataset):
    def aggregate(self, data: typing.List):
        logger.info('Test builds dataset is aggregating.')
        for row in data:
            start_date: int = convert_date_to_int(
                row['startDate'], '%Y%m%dT%H%M%S%z',
            )
            finish_date: int = convert_date_to_int(
                row['finishDate'], '%Y%m%dT%H%M%S%z',
            )
            duration = finish_date - start_date
            test_count = 0
            test_failed = 0
            test_duration = 0
            if 'testOccurrences' in row:
                test_count = row['testOccurrences'].get('count', 0)
                test_failed = row['testOccurrences'].get('failed', 0)
                test_duration = sum(
                    [
                        test.get('duration', 0)
                        for test in row['testOccurrences'].get(
                            'testOccurrence', [],
                        )
                    ],
                )
            failure_reason = None
            if row['status'] == 'FAILURE':
                failure_reason = _parse_status_text(row['statusText'])

            build_stats = row.get('statistics', {}).get('property', [])
            sandbox_build_duration = next(
                (
                    int(item['value'])
                    for item in build_stats
                    if item.get('name') == 'sandbox.build_duration'
                    and isinstance(item.get('value'), str)
                    and str.isnumeric(item.get('value'))
                ),
                None,
            )
            aggregated = {
                'build_id': int(row['id']),
                'build_number': row['number'],
                'start_date': start_date,
                'finish_date': finish_date,
                'agent_name': row['agent']['name'],
                'duration': duration,
                'sandbox_duration': sandbox_build_duration,
                'test_duration': int(test_duration),
                'test_count': int(test_count),
                'test_failed': int(test_failed),
                'status': row['status'],
                'status_text': row['statusText'],
                'failure_reason': failure_reason,
                'branch_name': row['branchName'],
            }
            self._dataset.append(aggregated)
            logger.debug(f'Data: {aggregated}')
        self._dataset.reverse()
