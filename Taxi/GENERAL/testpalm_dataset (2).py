import logging
import typing
import time

from .dataset import Dataset
from storages import Storage

logger = logging.getLogger(__name__)


class TestpalmDataset(Dataset):
    def __init__(
            self, storages: typing.List[Storage], definitions: typing.Iterable,
    ):
        super().__init__(storages)
        self.definitions = definitions

    def aggregate(self, data: typing.List) -> None:
        logger.info('Testpalm dataset is aggregating.')
        snapshot_time = int(time.time())
        for row in data:
            aggregated = {
                'testcase_id': row.get('id'),
                'created_time': row.get('createdTime'),
                'status': row.get('status'),
                'is_autotest': row.get('isAutotest'),
                'automation_status': self._get_attribute_value(
                    row, title='Automation Status',
                ),
                'priority': self._get_attribute_value(row, title='Priority'),
                'case_group': self._get_attribute_value(
                    row, title='CaseGroup',
                ),
                'snapshot_time': snapshot_time,
            }
            self._dataset.append(aggregated)
            logger.debug(f'Data: {aggregated}')

    def _get_definition(self, title: str) -> str:
        for definition in self.definitions:
            if definition.get('title') == title:
                return definition.get('id')

    def _get_attribute_value(
            self, testcase: typing.Dict, title: str,
    ) -> typing.Optional[str]:
        attribute_values = testcase.get('attributes', {}).get(
            self._get_definition(title),
        )
        if attribute_values:
            return attribute_values[0]
        return None
