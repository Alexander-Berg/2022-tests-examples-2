import logging
import time
import typing

from eats_automation_statistics.crontasks.eats_metrics.datasets import dataset

logger = logging.getLogger(__name__)


class TestpalmDataset(dataset.Dataset):
    def __init__(self, definitions: typing.Iterable):
        super().__init__()
        self.definitions = definitions

    def aggregate(self, data: typing.List) -> None:
        logger.info('Testpalm dataset is aggregating.')
        snapshot_time = int(time.time())
        for row in data:
            attributes = row.attributes or {}
            aggregated = {
                'testcase_id': str(row.id),
                'created_time': int(row.created_time),
                'status': row.status,
                'is_autotest': str(row.is_autotest),
                'automation_status': self._get_attribute_value(
                    attributes, title='Automation Status',
                ),
                'priority': self._get_attribute_value(
                    attributes, title='Priority',
                ),
                'case_group': self._get_attribute_value(
                    attributes, title='CaseGroup',
                ),
                'snapshot_time': snapshot_time,
            }
            self._data.append(aggregated)
        logger.info(
            'Testpalm dataset is aggregated, testcase id: %s',
            ','.join(row['testcase_id'] for row in self.data),
        )

    def _get_definition_id(self, title: str) -> typing.Optional[str]:
        for definition in self.definitions:
            if definition.title == title:
                return definition.id
        logger.error('Definition %s not found', title)
        return None

    def _get_attribute_value(
            self, attributes: typing.Dict, title: str,
    ) -> typing.Optional[str]:
        attribute_values = attributes.get(self._get_definition_id(title))
        if attribute_values:
            return attribute_values[0]
        return None
