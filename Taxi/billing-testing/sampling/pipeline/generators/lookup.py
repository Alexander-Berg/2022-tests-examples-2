import json
import logging
from typing import Any

from sibilla import utils

from . import generator

logger = logging.getLogger(__name__)


class CollectionLookup(generator.Generator):
    def __init__(self, path, filters, lookup_path):
        generator.Generator.__init__(self)
        self._lookup_values = set()
        self._prepare_data(path, filters or {}, lookup_path)

    def _process_item(self, filters, lookup_path, item):
        if self._process_lookup(filters, item):
            self._lookup_values.update(utils.lookup_data(lookup_path, item))

    def _prepare_data(self, path, filters, lookup_path):
        logger.info(f'lookup: {path}')
        if path.endswith('.json'):
            with open(path) as file:
                for item in json.load(file):
                    self._process_item(filters, lookup_path, item)
        elif path.endswith('.jsonl'):
            with open(path, 'r') as file:
                for line in file.readlines():
                    item = json.loads(line)
                    self._process_item(filters, lookup_path, item)
                file.close()
        else:
            raise Exception('unknown file type')

    def _process_lookup(self, filters, item):
        for query_filter in filters:
            try:
                actual_values = utils.lookup_data(query_filter, item)
                expected_set = {filters[query_filter]}
                if not expected_set.issubset(set(actual_values)):
                    return False
            except utils.SubstitutionNotFoundError:
                return False
        return True

    def fetch(self) -> Any:
        return list(self._lookup_values)
