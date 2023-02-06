# coding=utf-8
from passport.backend.core.logging_utils.loggers.tskv import (
    TskvLogEntry,
    TskvLogger,
)
from passport.backend.utils.time import get_unixtime


class YasmLogEntry(TskvLogEntry):
    def __init__(self, **params):
        params.setdefault('tskv_format', 'tus-log')
        params.setdefault('unixtime', get_unixtime())
        super(YasmLogEntry, self).__init__(**params)


class YasmLogger(TskvLogger):
    """
    Логгер для statbox. Имеет контекст (данные, которые записываются при каждой записи; не включают стандартные
    поля tskv_format, unixtime, py) и текущие данные (которые будут единоразово записаны при следующем вызове log).
    """
    default_logger_name = 'tus.yasm-logger'
    entry_class = YasmLogEntry
