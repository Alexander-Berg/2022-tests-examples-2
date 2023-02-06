from contextlib import contextmanager
from datetime import timedelta, datetime
from typing import Optional

import mock
import pytest

from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.datetime_utils import parse_datetime as dttm, Period, utcnow
from dmp_suite.yt import ETLTable, Int, LayeredLayout
from dmp_suite.yt.dyntable_operation.dynamic_table_loaders import (
    OrderedDataIncrement,
    OrderedDynamicIncrementLoader
)


class TestYTTable(ETLTable):
    __layout__ = LayeredLayout(name='test', layer='test')
    __dynamic__ = True
    n = Int()


class FakeIncrement(OrderedDataIncrement):
    def __init__(self, min_updated=None, max_updated=None):
        self.min_updated = min_updated
        self.max_updated = max_updated

    def get_min_updated(self) -> Optional[datetime]:
        return self.min_updated

    def get_max_updated(self):
        return self.max_updated

    # not used
    def get_updated(self, record):
        pass

    # not used
    def get_data(self, period):
        pass


class TestDataIncrement(OrderedDataIncrement):
    def __init__(self, data, updated_field='dt'):
        self._data = list(data)
        self._updated_field = updated_field

    def get_min_updated(self) -> Optional[datetime]:
        return None

    def get_max_updated(self):
        return utcnow()

    def get_updated(self, record):
        return record[self._updated_field]

    def get_data(self, period):
        # обычно клиенты бд возращают генератор, сделаем его через yield from
        yield from self._data


def get_processing(processing_results):
    processing_results = list(processing_results)
    processing_results.reverse()

    def processing_(*arg, **kwarg):
        while processing_results:
            value = processing_results.pop()
            if isinstance(value, Exception):
                raise value
            else:
                yield value

    return processing_


class TestOrderedDynamicIncrementLoader:
    cdc_overlay = timedelta(hours=1)

    @staticmethod
    def assert_ctl_call(ctl_mock, dates):
        assert ctl_mock.yt.set_param.call_args_list == [
            mock.call(TestYTTable, CTL_LAST_LOAD_DATE, dt)
            for dt in dates if not isinstance(dt, Exception)
        ]

    @contextmanager
    def patch_loader(self, increment, ctl_initial_value, period,
                     processing_results):
        loader = OrderedDynamicIncrementLoader(
            TestYTTable, increment, self.cdc_overlay
        )
        # чтобы не ждать в тестах
        loader.retry_sleep = 0

        processing_patch = mock.patch.object(loader, '_processing')
        with processing_patch as processing_mock:
            processing_mock.side_effect = get_processing(processing_results)
            chunk_last_load_dttms = [last_load for last_load in loader.load_generator(ctl_initial_value, period)]
            yield chunk_last_load_dttms, processing_mock

    @contextmanager
    def patch_loader_with_ctl_mock(self, increment, ctl_initial_value, period,
                                   processing_results):
        loader = OrderedDynamicIncrementLoader(
            TestYTTable, increment, self.cdc_overlay
        )
        # чтобы не ждать в тестах
        loader.retry_sleep = 0

        get_ctl_patch = mock.patch(
            'dmp_suite.yt.dyntable_operation.dynamic_table_loaders.get_ctl')
        processing_patch = mock.patch.object(loader, '_processing')
        with get_ctl_patch as get_ctl_mock, processing_patch as processing_mock:
            ctl_mock = mock.MagicMock()
            get_ctl_mock.return_value = ctl_mock
            ctl_mock.yt.get_param.return_value = ctl_initial_value
            processing_mock.side_effect = get_processing(processing_results)
            loader.load(period)
            yield ctl_mock, processing_mock

    def test_max_update_is_none(self):
        with self.patch_loader(
                increment=FakeIncrement(),
                ctl_initial_value=None,
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=dttm('2020-03-24 10:00:00')),
                ctl_initial_value=None,
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

    def test_max_less_min(self):
        max_updated = dttm('2020-03-24 20:00:00')
        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=dttm('2020-03-24 20:00:00'),
                    max_updated=dttm('2020-03-24 08:00:00')),
                ctl_initial_value=None,
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

    # первоначальная загрузка:
    # с пустым ctl
    # min_updated не задан
    # загружается одни чанк
    def test_init_load_non_min_one_chunk(self):
        max_updated = dttm('2020-03-24 20:00:00')
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=None,
                period=None,
                processing_results=[max_updated]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [max_updated]
            proc_mock.assert_called_once_with(
                Period(max_updated - self.cdc_overlay, max_updated))

    # первоначальная загрузка с пустым ctl +  одним чанк
    def test_init_load_with_min_one_chunk(self):
        min_updated = dttm('2020-03-24 10:00:00')
        max_updated = dttm('2020-03-24 20:00:00')
        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=min_updated,
                    max_updated=max_updated),
                ctl_initial_value=None,
                period=None,
                processing_results=[max_updated]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [max_updated]
            proc_mock.assert_called_once_with(
                Period(min_updated, max_updated))

    # если processing вернет None, то это ошибка
    # chunk_last_load_dttm никогда не может быть None
    def test_chunk_date_none(self):
        with pytest.raises(Exception):
            with self.patch_loader(
                    increment=FakeIncrement(max_updated=dttm('2020-03-24 20:00:00')),
                    ctl_initial_value=None,
                    period=None,
                    processing_results=[None]):
                pass

    # первоначальная загрузка с пустым ctl + несколько чанков
    def test_init_load_many_chunks(self):
        max_updated = dttm('2020-03-24 20:00:00')
        processing_results = [
            dttm('2020-03-24 19:30:00'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=None,
                period=None,
                processing_results=processing_results) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == processing_results
            proc_mock.assert_called_once_with(
                Period(max_updated - self.cdc_overlay, max_updated))

    # первоначальная загрузка с пустым ctl + retry
    def test_init_load_non_min_and_retry(self):
        max_updated = dttm('2020-03-24 20:00:00')
        processing_results = [
            dttm('2020-03-24 19:30:00'),
            RuntimeError('test retry of chunk'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=None,
                period=None,
                processing_results=processing_results) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [result for result in processing_results if type(result) == datetime]
            assert proc_mock.call_args_list == [
                mock.call(Period(max_updated - self.cdc_overlay, max_updated)),
                mock.call(Period(dttm('2020-03-24 19:30:00'), max_updated))
            ]

    # первоначальная загрузка с пустым ctl + retry + min_updated
    def test_init_load_with_min_and_retry(self):
        min_updated = dttm('2020-03-24 10:00:00')
        max_updated = dttm('2020-03-24 20:00:00')
        processing_results = [
            dttm('2020-03-24 19:30:00'),
            RuntimeError('test retry of chunk'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=min_updated,
                    max_updated=max_updated),
                ctl_initial_value=None,
                period=None,
                processing_results=processing_results) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [result for result in processing_results if type(result) == datetime]
            assert proc_mock.call_args_list == [
                mock.call(Period(min_updated, max_updated)),
                mock.call(Period(dttm('2020-03-24 19:30:00'), max_updated))
            ]

    def test_ctl_and_max_update_is_none(self):
        # дата обновления источника не известна
        with self.patch_loader(
                increment=FakeIncrement(),
                ctl_initial_value=dttm('2020-03-24 19:00:00'),
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

        # дата обновления источника не известна
        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=dttm('2020-03-24 10:00:00')),
                ctl_initial_value=dttm('2020-03-24 19:00:00'),
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

        # максимальная дата на источнике оказалась меньше ctl
        with pytest.raises(ValueError):
            with self.patch_loader(
                    increment=FakeIncrement(
                        max_updated=dttm('2020-03-24 18:00:00')),
                    ctl_initial_value=dttm('2020-03-24 19:00:00'),
                    period=None,
                    processing_results=[]):
                pass

    # processing ничего не вернул - ctl не должен измениться
    def test_ctl_no_chunk(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock

            assert chunk_last_load_dttm == []
            proc_mock.assert_called_once_with(
                Period(ctl_initial_value - self.cdc_overlay, max_updated))

    # запись одного чанка: ctl only
    def test_ctl_one_chunk(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=[max_updated]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [max_updated]
            proc_mock.assert_called_once_with(
                Period(ctl_initial_value - self.cdc_overlay, max_updated))

    # ctl меньше min_updated - ошибка
    def test_ctl_less_min_updated(self):
        min_updated = dttm('2020-03-24 18:00:00')
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 15:00:00')
        with pytest.raises(ValueError):
            with self.patch_loader(
                    increment=FakeIncrement(
                        min_updated=min_updated,
                        max_updated=max_updated),
                    ctl_initial_value=ctl_initial_value,
                    period=None,
                    processing_results=[max_updated]):
                pass

    # запись одного чанка: ctl + min_updated
    def test_ctl_and_min_updated(self):
        min_updated = dttm('2020-03-24 10:00:00')
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 15:00:00')
        with self.patch_loader(
                increment=FakeIncrement(
                        min_updated=min_updated,
                        max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=[max_updated]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [max_updated]
            proc_mock.assert_called_once_with(
                Period(ctl_initial_value - self.cdc_overlay, max_updated))

    # запись одного чанка: (ctl - cdc_overlay) < min_updated
    # не ошибка грузим от min_updated
    def test_ctl_and_min_updated_cdc_overlay(self):
        min_updated = dttm('2020-03-24 15:00:00')
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 15:30:00')
        with self.patch_loader(
                increment=FakeIncrement(
                        min_updated=min_updated,
                        max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=[max_updated]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == [max_updated]
            proc_mock.assert_called_once_with(
                Period(min_updated, max_updated))

    # запись нескольких чанков
    def test_ctl_many_chunks(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        processing_results = [
            dttm('2020-03-24 19:30:00'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=processing_results) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == processing_results
            proc_mock.assert_called_once_with(
                Period(ctl_initial_value - self.cdc_overlay, max_updated))

    # запись нескольких чанков, но дата первого чанка меньше текущего значения ctl
    # это может быть вызвано смещением cdc_overlay
    def test_ctl_many_chunks2(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        processing_results = [
            dttm('2020-03-24 18:30:00'),
            dttm('2020-03-24 19:30:00'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader_with_ctl_mock(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=processing_results) as load_mock:
            ctl_mock, proc_mock = load_mock
            # 2020-03-24 18:30:00 - не должно быть записано в ctl, так оно
            # меньше текущего значения 2020-03-24 19:00:00
            self.assert_ctl_call(ctl_mock, [
                dttm('2020-03-24 19:30:00'),
                dttm('2020-03-24 20:00:00')
            ])
            proc_mock.assert_called_once_with(
                Period(ctl_initial_value - self.cdc_overlay, max_updated))

    # запись нескольких чанков, но дата первого чанка меньше текущего значения ctl
    # это может быть вызвано смещением cdc_overlay
    def test_ctl_retry(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        processing_results = [
            RuntimeError('test retry of chunk'),
            dttm('2020-03-24 18:30:00'),
            RuntimeError('test retry of chunk'),
            dttm('2020-03-24 19:30:00'),
            RuntimeError('test retry of chunk'),
            dttm('2020-03-24 20:00:00')
        ]
        with self.patch_loader_with_ctl_mock(
                increment=FakeIncrement(max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=None,
                processing_results=processing_results) as load_mock:
            ctl_mock, proc_mock = load_mock
            # 2020-03-24 18:30:00 - не должно быть записано в ctl, так оно
            # меньше текущего значения 2020-03-24 19:00:00
            self.assert_ctl_call(ctl_mock, [
                dttm('2020-03-24 19:30:00'),
                dttm('2020-03-24 20:00:00')
            ])
            assert proc_mock.call_args_list == [
                mock.call(Period(ctl_initial_value - self.cdc_overlay, max_updated)),
                mock.call(Period(ctl_initial_value - self.cdc_overlay, max_updated)),
                mock.call(Period(dttm('2020-03-24 18:30:00'), max_updated)),
                mock.call(Period(dttm('2020-03-24 19:30:00'), max_updated)),
            ]

    def test_exceed_retry_limit(self):
        max_updated = dttm('2020-03-24 20:00:00')
        ctl_initial_value = dttm('2020-03-24 19:00:00')
        processing_results = [RuntimeError('test retry of chunk')] * 5
        with pytest.raises(RuntimeError):
            with self.patch_loader(
                    increment=FakeIncrement(max_updated=max_updated),
                    ctl_initial_value=ctl_initial_value,
                    period=None,
                    processing_results=processing_results):
                pass

    def test_period_and_max_update_is_none(self):
        with self.patch_loader(
                increment=FakeIncrement(),
                ctl_initial_value=dttm('2020-03-24 19:00:00'),
                period=Period('2020-03-24 18:00:00', '2020-03-24 20:00:00'),
                processing_results=[]) as load_mock:
            chunk_last_load_dttm, proc_mock = load_mock
            assert chunk_last_load_dttm == []
            proc_mock.assert_not_called()

    def assert_period(self, period, processing_period,
                      min_updated=None,
                      max_updated=dttm('2020-03-24 20:00:00'),
                      ctl_initial_value=dttm('2020-03-24 19:00:00')):

        with self.patch_loader(
                increment=FakeIncrement(
                    min_updated=min_updated,
                    max_updated=max_updated),
                ctl_initial_value=ctl_initial_value,
                period=period,
                processing_results=[max_updated]) as load_mock:
            ctl_mock, proc_mock = load_mock

            assert proc_mock.call_args_list == [mock.call(processing_period)]

    def test_period(self):
        # входной период меньше ctl
        self.assert_period(
            Period('2020-03-24 14:00:00', '2020-03-24 17:00:00'),
            Period(dttm('2020-03-24 14:00:00'), dttm('2020-03-24 17:00:00'))
        )

        # дата старта меньше ctl, дата окончания больше ctl и меньше max_updated
        self.assert_period(
            Period('2020-03-24 14:00:00', '2020-03-24 19:30:00'),
            Period(dttm('2020-03-24 14:00:00'), dttm('2020-03-24 19:30:00'))
        )

        # дата старта меньше ctl, дата окончания больше ctl и max_updated
        self.assert_period(
            Period('2020-03-24 14:00:00', '2020-03-24 21:00:00'),
            Period(dttm('2020-03-24 14:00:00'), dttm('2020-03-24 20:00:00'))
        )

        # дата старта больше ctl - ошибка так как будет пропуск данных
        with pytest.raises(ValueError):
            self.assert_period(
                Period('2020-03-24 19:30:00', '2020-03-24 20:00:00'),
                None
            )

        self.assert_period(
            Period('2020-03-24 14:00:00', '2020-03-24 21:00:00'),
            Period(dttm('2020-03-24 14:00:00'), dttm('2020-03-24 20:00:00')),
            ctl_initial_value=None
        )
        # ошибка - дата старт периода превышает max_updated
        with pytest.raises(ValueError):
            self.assert_period(
                Period('2020-03-24 21:00:00', '2020-03-24 22:00:00'),
                None,
                ctl_initial_value=None
            )

        # ошибка - дата старт периода меньше min_updated
        with pytest.raises(ValueError):
            self.assert_period(
                Period('2020-03-24 14:00:00', '2020-03-24 21:00:00'),
                None,
                min_updated=dttm('2020-03-24 15:00:00'),
                ctl_initial_value=None
            )

        self.assert_period(
            Period('2020-03-24 14:00:00', '2020-03-24 21:00:00'),
            Period(dttm('2020-03-24 14:00:00'), dttm('2020-03-24 20:00:00')),
            min_updated=dttm('2020-03-24 10:00:00'),
        )

    @contextmanager
    def patch_loader_processing(self, increment):
        loader = OrderedDynamicIncrementLoader(
            TestYTTable, increment, self.cdc_overlay
        )
        # чтобы не ждать в тестах
        loader.retry_sleep = 0
        loader.chunk_size = 1

        get_ctl_patch = mock.patch(
            'dmp_suite.yt.dyntable_operation.dynamic_table_loaders.get_ctl')
        insert_patch = mock.patch(
            'dmp_suite.yt.dyntable_operation.operations.insert_chunk_in_dynamic_table')
        with get_ctl_patch as get_ctl_mock, insert_patch as insert_mock:
            ctl_mock = mock.MagicMock()
            get_ctl_mock.return_value = ctl_mock
            ctl_mock.yt.get_param.return_value = None
            loader.load()
            yield insert_mock

    def assert_processing(self, chunck_size, data, expected_chunk_dates, use_threading=False):
        loader = OrderedDynamicIncrementLoader(
            TestYTTable, TestDataIncrement(data), self.cdc_overlay,
            use_threading=use_threading
        )
        # чтобы не ждать в тестах
        loader.retry_sleep = 0
        loader.chunk_size = chunck_size

        insert_patch = mock.patch(
            'dmp_suite.yt.dyntable_operation.dynamic_table_loaders.insert_chunk_in_dynamic_table')
        with insert_patch as insert_mock:
            chunk_last_load_dates = list(loader._processing(
                Period('2020-03-24 09:30:00', '2020-03-24 20:00:00')))

            assert chunk_last_load_dates == expected_chunk_dates
            assert insert_mock.call_count == len(expected_chunk_dates)

    # нет данных
    def test_processing_no_data(self):
        self.assert_processing(2, [], [])

    # все записываемые чанки полные - состоят из двух записей
    def test_processing_full_chunk(self):
        data = [
            {'n': n, 'dt': dttm('2020-03-24 10:00:00') + timedelta(hours=n)}
            for n in range(0, 4)
        ]
        expected_chunk_dates = [
            dttm('2020-03-24 11:00:00'), dttm('2020-03-24 13:00:00')
        ]
        self.assert_processing(2, data, expected_chunk_dates)

    # последний чанк состоит из одной записи а не из двух
    def test_processing_partial_chunk(self):
        data = [
            {'n': n, 'dt': dttm('2020-03-24 10:00:00') + timedelta(hours=n)}
            for n in range(0, 5)
        ]
        expected_chunk_dates = [
            dttm('2020-03-24 11:00:00'), dttm('2020-03-24 13:00:00'),
            dttm('2020-03-24 14:00:00')
        ]
        self.assert_processing(2, data, expected_chunk_dates)

    def test_processing_use_threading(self):
        data = [
            {'n': n, 'dt': dttm('2020-03-24 10:00:00') + timedelta(hours=n)}
            for n in range(0, 4)
        ]
        expected_chunk_dates = [
            dttm('2020-03-24 11:00:00'), dttm('2020-03-24 13:00:00')
        ]
        self.assert_processing(
            2, data, expected_chunk_dates, use_threading=True)
