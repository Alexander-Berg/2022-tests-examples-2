import copy
import logging

import pytest


@pytest.fixture
def collected_logs_with_link(monkeypatch):
    logs = []

    original_emit = logging.StreamHandler.emit

    def emit(self, record):
        if getattr(record, '_link', None):
            to_save = {
                'level': record.levelname,
                '_link': record._link,  # pylint: disable=protected-access
                'extdict': copy.deepcopy(record.extdict),
                'msg': record.getMessage(),
                'exc_info': bool(record.exc_info),
            }
            logs.append(to_save)
        return original_emit(self, record)

    monkeypatch.setattr('taxi.logs.log.StreamHandler.emit', emit)

    return logs
