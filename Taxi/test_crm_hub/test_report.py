# pylint: disable=protected-access
import typing

import pytest

from taxi.logs import auto_log_extra

import crm_hub.logic.report.context as report_ctx
import crm_hub.logic.report.extra as report_extra


class DummyObj:
    def serialize(self):
        return {'dummy': 1234}


class LogExtra(typing.NamedTuple):
    key: str
    value: typing.Any
    report_only: bool = False


@pytest.fixture(autouse=True)
def log_scope():
    with auto_log_extra.log_scope(global_key='globvalue'):
        yield


@pytest.mark.parametrize(
    ['extras', 'report_context', 'log_context', 'ignore'],
    [
        (
            [
                LogExtra('key3', 'value3', True),
                LogExtra('key1', 'value1', True),
            ],
            {'key3': 'value3', 'key1': 'value1'},
            {'global_key': 'globvalue'},
            False,
        ),
        (
            [
                LogExtra('key', 'value', False),
                LogExtra('key1', 'value1', True),
            ],
            {'key1': 'value1'},
            {'global_key': 'globvalue', 'key': 'value'},
            False,
        ),
        (
            [
                LogExtra('key1', 'value1', False),
                LogExtra('key2', 'value2', True),
            ],
            None,
            {'global_key': 'globvalue', 'key1': 'value1'},
            True,
        ),
        (
            [
                LogExtra('bool_key', True, True),
                LogExtra('obj_key', DummyObj(), True),
                LogExtra('dict_key', {'some': 'value'}, True),
            ],
            {
                'bool_key': 'true',
                'obj_key': '{"dummy": 1234}',
                'dict_key': '{"some": "value"}',
            },
            {'global_key': 'globvalue'},
            True,
        ),
    ],
)
async def test_success_report(
        caplog, extras, report_context, log_context, ignore,
):
    with report_ctx.report_onexit():
        for extra in extras:
            if extra.report_only:
                report_extra.add_value(extra.key, extra.value)
            else:
                auto_log_extra.update_log_extra(**{extra.key: extra.value})
        if ignore:
            report_extra.ignore()
    if ignore:
        assert not caplog.records
    else:
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert record.levelname == 'INFO'
        assert record.msg == 'report'
        assert record.extdict == dict(success='true', **report_context)
    assert (
        auto_log_extra.get_log_extra()[auto_log_extra._EXTDICT] == log_context
    )


async def test_failure_report(caplog):
    try:
        with report_ctx.report_onexit():
            report_extra.add_value('key1', 'value1')
            auto_log_extra.update_log_extra(key2='value2')
            raise RuntimeError('some err')
    except RuntimeError:
        pass
    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelname == 'INFO'
    assert record.msg == 'report'
    assert record.extdict == dict(success='false', key1='value1')
    assert auto_log_extra.get_log_extra()[auto_log_extra._EXTDICT] == {
        'global_key': 'globvalue',
        'key2': 'value2',
    }
