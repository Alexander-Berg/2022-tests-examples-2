"""
    Main runner.
    Loops over events queue and gathers report
"""
# pylint: disable=import-only-modules

import copy
import datetime
import logging
import os
import pickle
import pprint
import sys
import traceback
import types
from typing import Any
from typing import BinaryIO
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from simulator.core import events
from simulator.core import modules
from simulator.core import queue
from simulator.core.structures import RunnerStats
from simulator.core.utils import current_time

LOG = logging.getLogger(__name__)

ReportRow = Tuple[datetime.datetime, str, Any]
ExcInfoType = Tuple[Type[BaseException], BaseException, types.TracebackType]


class Runner:
    CACHE_FILENAME = '.cache.p'
    STATS_LOG_FILENAME = '.stats.log'
    STATS_OBJ_FILENAME = '.stats.p'
    OUTPUT_FILENAME = '.output.log'
    MEMORY_MAX_SIZE = 1000

    def __init__(self, folder_path: Optional[str] = None, use_cache=False):
        self._stats = RunnerStats()

        self._error: Optional[ExcInfoType] = None
        self._memory_reports: List[ReportRow] = []
        self._folder_path = folder_path
        self._cache_file: Optional[BinaryIO] = None

        if use_cache:
            assert folder_path

            self._cache_file = open(self.cache_filename, 'wb+')

        if self._folder_path:
            open(self.stats_log_filename, 'w').close()
            open(self.output_filename, 'w').close()
            open(self.stats_obj_filename, 'w').close()

    @property
    def stats(self) -> RunnerStats:
        return self._stats

    @property
    def is_failed(self) -> bool:
        return bool(self._error)

    @property
    def cache_filename(self) -> str:
        assert self._folder_path
        return os.path.join(self._folder_path, self.CACHE_FILENAME)

    @property
    def stats_log_filename(self) -> str:
        assert self._folder_path
        return os.path.join(self._folder_path, self.STATS_LOG_FILENAME)

    @property
    def stats_obj_filename(self) -> str:
        assert self._folder_path
        return os.path.join(self._folder_path, self.STATS_OBJ_FILENAME)

    @property
    def output_filename(self) -> str:
        assert self._folder_path
        return os.path.join(self._folder_path, self.OUTPUT_FILENAME)

    async def run(self):
        self.stats.set_start(current_time.CurrentTime.get())

        while True:
            if self._error:
                break
            try:
                await self.run_event()
            except queue.EventQueueEmptyError:
                LOG.info('Empty event queue, finish simulation')
                break
            except Exception:  # pylint: disable=broad-except
                LOG.exception('Runner was failed, finish simulation')
                self._error = sys.exc_info()
                break

        if not self.is_failed:
            queue.EventQueue.put(
                current_time.CurrentTime.get(),
                events.statistics.post_finish(runner=self),
            )
            await self.run_event()

    async def run_event(self):
        # get next event from queue (events are ordered by timestamp)
        event = queue.EventQueue.pop()

        current_time.CurrentTime.set(event.timestamp)

        # execute event
        report = await event.launch()
        # deepcopy for snapshot
        self._save_report_row(event, copy.deepcopy(report))

    def __format_error(self) -> str:
        assert self._error is not None
        return ''.join(traceback.format_exception(*self._error))

    def _save_report_row(self, event: queue.Event, row: Any):
        self._save_report_row_memory(event, row)
        self._maybe_dump_report()

    def _maybe_dump_report(self):
        if self._cache_file is None:
            return

        if len(self._memory_reports) >= self.MEMORY_MAX_SIZE:
            LOG.debug('Saving runner reports to file...')
            pickle.dump(self._memory_reports, file=self._cache_file)
            self._memory_reports = []

    def _save_report_row_memory(self, event: queue.Event, row: Any):
        self._memory_reports.append(
            (event.timestamp, event.handler.func.__name__, row),
        )

    def iter_raw_report(self) -> Generator[ReportRow, None, None]:
        if self._cache_file is None:
            yield from self._memory_reports
            return

        self._cache_file.seek(0)
        while True:
            try:
                yield from pickle.load(file=self._cache_file)
            except EOFError:
                break

        yield from self._memory_reports

    def print_raw_report(self) -> None:
        pprint.pprint(list(self.iter_raw_report()))
        if self._error:
            pprint.pprint(self.__format_error())

    def dump_raw_report(self) -> None:
        with open(self.output_filename, 'w') as file:
            for timestamp, name, output in self.iter_raw_report():
                file.write(
                    f'{timestamp.isoformat(timespec="seconds")}\t'
                    f'[{name}]\t{output}\n',
                )
            if self._error:
                file.write(f'Exception: {self.__format_error()}')

    def print_statistics(self) -> None:
        pprint.pprint(self.stats.gather())

    def dump_statistics(self, custom: Optional[dict] = None) -> None:
        self._dump_statistics_log(custom=custom)
        self._dump_statistics_obj(custom=custom)

    def _dump_statistics_log(self, custom: Optional[dict]) -> None:
        with open(self.stats_log_filename, 'w') as file:
            if custom is None:
                result = self._gather_statistics()
            else:
                result = {**self._gather_statistics(), **custom}
            self._write_with_indents(file, result)

    def _dump_statistics_obj(self, custom: Optional[dict]) -> None:
        with open(self.stats_obj_filename, 'wb') as file:
            headers, row = self._gather_statistics_as_table(custom=custom)
            pickle.dump((headers, row), file=file)

    def _gather_statistics(self) -> dict:
        return {
            'run': self.stats.gather(),
            'candidate': modules.CandidatesModel.gather_statistics(),
            'order': modules.OrdersModel.gather_statistics(),
            'dispatch': modules.DispatchModel.gather_statistics(),
        }

    def _gather_statistics_as_table_helper(
            self, stats: dict, pairs: List[Tuple[str, Any]], prefix: str = '',
    ) -> None:
        for key, value in stats.items():
            if isinstance(value, dict):
                new_prefix = f'{prefix}{key}_'
                self._gather_statistics_as_table_helper(
                    value, pairs, prefix=new_prefix,
                )
            else:
                pairs.append((f'{prefix}{key}', value))

    def _gather_statistics_as_table(
            self, custom: dict = None,
    ) -> Tuple[List[str], List[Any]]:
        statistics = self._gather_statistics()

        if custom is not None:
            statistics = {**statistics, **custom}

        pairs: List[Tuple[str, Any]] = []
        self._gather_statistics_as_table_helper(statistics, pairs)

        return [str(p[0]) for p in pairs], [p[1] for p in pairs]

    @classmethod
    def _make_indents(cls, indent):
        return '\t' * indent

    @classmethod
    def _write_with_indents(cls, file, stats_dict, stats_name='', indent=0):
        if stats_name != '':
            new_indent = indent + 1
            file.write(f'{cls._make_indents(indent)}{stats_name}:\n')
        else:
            new_indent = indent
        for name, value in stats_dict.items():
            if isinstance(value, dict):
                cls._write_with_indents(
                    file, value, stats_name=name, indent=new_indent,
                )
            else:
                file.write(f'{cls._make_indents(new_indent)}{name}\t{value}\n')
