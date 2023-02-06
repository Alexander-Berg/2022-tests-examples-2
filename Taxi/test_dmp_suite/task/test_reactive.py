import pytest
import mock
from datetime import datetime

from connection import ctl
from dmp_suite import scales, datetime_utils as dtu
from dmp_suite.ctl import (
    CTL_LAST_LOAD_DATE,
    CTL_LAST_SYNC_DATE,
)
from dmp_suite.ctl.storage import DictStorage
from dmp_suite.task.reactive.trigger import all_arrived_by_prev_chunk

from dmp_suite.yt import table as yt_table
from dmp_suite.greenplum import table as gp_table
from dmp_suite.ext_source_proxy import ExternalSourceProxy
from dmp_suite.task.reactive import commons, trigger


def make_utc_now_mock(mock_time: datetime):
    return mock.patch(
        'dmp_suite.datetime_utils.utcnow',
        mock.MagicMock(return_value=mock_time),
    )


class FakeYtTable(yt_table.NotLayeredYtTable):
    __layout__ = yt_table.NotLayeredYtLayout('foo', 'tab')


class FakeGpTable(gp_table.ExternalGPTable):
    __layout__ = gp_table.ExternalGPLayout('foo', 'tab')


@pytest.fixture
def ctl_dict_mock():
    ctl_ = ctl.WrapCtl(DictStorage())
    patch_ = mock.patch('connection.ctl.get_ctl', return_value=ctl_)
    with patch_:
        yield ctl_


class FakeExtSourceProxy(ExternalSourceProxy):

    @property
    def ctl_entity(self):
        return 'dummy#dummy'

    def get_new_ctl_value(self):
        return datetime(2020, 10, 5, 19, 44)


# Commons tests


@pytest.mark.parametrize('entity, param, key', [
    (FakeYtTable, CTL_LAST_LOAD_DATE, 'last_load_date@//dummy/foo/tab@yt'),
    (FakeGpTable, CTL_LAST_SYNC_DATE, 'last_sync_date@foo.tab@gp'),
    (FakeExtSourceProxy(), CTL_LAST_LOAD_DATE, 'last_load_date@dummy#dummy@source'),
])
def test_get_entity_state_key(entity, param, key):
    assert commons.get_entity_state_key((entity, param)) == key


def test_get_entities_current_state(ctl_dict_mock):

    entity_params = [
        (FakeYtTable, CTL_LAST_LOAD_DATE),
        (FakeGpTable, CTL_LAST_SYNC_DATE),
    ]

    domains = [
        'yt',
        'gp',
    ]

    values = [
        datetime(2021, 5, 3, 18, 21, 37),
        datetime(2021, 5, 3, 19, 15, 51),
    ]

    expected = {
        commons.get_entity_state_key(entity_param): value
        for entity_param, value in zip(entity_params, values)
    }

    for (entity, param), domain, value in zip(entity_params, domains, values):
        getattr(ctl_dict_mock, domain).set_param(entity, param, value)
        assert getattr(ctl_dict_mock, domain).get_param(entity, param) == value

    actual = commons.get_entities_current_state(entity_params)
    assert expected == actual


# Complex trigger tests


class DummyTrigger(trigger.Trigger):

    def __init__(self, parameters, activation):
        super().__init__()
        self._parameters = parameters
        self._activation = activation

    def parameters(self):
        return self._parameters

    def is_active(self, last, current):
        return self._activation

    def __str__(self):
        return f'DummyTrigger({self._activation}, {self._parameters})'


@pytest.mark.parametrize('complex_trigger, activation', [
    (trigger.all_triggers(DummyTrigger([], False), DummyTrigger([], False)), False),
    (trigger.all_triggers(DummyTrigger([], False), DummyTrigger([], True)), False),
    (trigger.all_triggers(DummyTrigger([], True), DummyTrigger([], False)), False),
    (trigger.all_triggers(DummyTrigger([], True), DummyTrigger([], True)), True),
    (trigger.any_trigger(DummyTrigger([], False), DummyTrigger([], False)), False),
    (trigger.any_trigger(DummyTrigger([], False), DummyTrigger([], True)), True),
    (trigger.any_trigger(DummyTrigger([], True), DummyTrigger([], False)), True),
    (trigger.any_trigger(DummyTrigger([], True), DummyTrigger([], True)), True),
])
def test_complex_trigger_activations(complex_trigger: trigger.Trigger, activation: bool):
    assert complex_trigger.is_active({}, {}) == activation


@pytest.mark.parametrize('complex_trigger, parameters', [
    (trigger.all_triggers(DummyTrigger([], False)), []),
    (trigger.all_triggers(DummyTrigger([], False), DummyTrigger([], False)), []),
    (
        trigger.all_triggers(DummyTrigger([(FakeYtTable, CTL_LAST_SYNC_DATE)], False)),
        [(FakeYtTable, CTL_LAST_SYNC_DATE)],
    ),
    (
        trigger.all_triggers(
            DummyTrigger([(FakeYtTable, CTL_LAST_SYNC_DATE)], False),
            DummyTrigger([], False),
        ),
        [(FakeYtTable, CTL_LAST_SYNC_DATE)],
    ),
    (
        trigger.all_triggers(
            DummyTrigger([], False),
            DummyTrigger([(FakeYtTable, CTL_LAST_SYNC_DATE)], False),
        ),
        [(FakeYtTable, CTL_LAST_SYNC_DATE)],
    ),
    (
        trigger.all_triggers(
            DummyTrigger([(FakeYtTable, CTL_LAST_SYNC_DATE)], False),
            DummyTrigger([(FakeGpTable, CTL_LAST_SYNC_DATE)], False),
            DummyTrigger([(FakeExtSourceProxy(), CTL_LAST_LOAD_DATE)], False),
        ),
        [
            (FakeYtTable, CTL_LAST_SYNC_DATE),
            (FakeGpTable, CTL_LAST_SYNC_DATE),
            (FakeExtSourceProxy(), CTL_LAST_LOAD_DATE)
        ],
    ),
])
def test_complex_trigger_parameters(complex_trigger: trigger.Trigger, parameters):
    assert complex_trigger.parameters() == parameters


# Entity trigger tests


PARAM = FakeGpTable, CTL_LAST_LOAD_DATE
STATE_KEY = 'last_load_date@foo.tab@gp'

REF_PARAM = FakeYtTable, CTL_LAST_SYNC_DATE
REF_STATE_KEY = 'last_sync_date@//dummy/foo/tab@yt'


def ctl_state(year, month, day, hour=0, minute=0, second=0, microsecond=0):
    return {
        STATE_KEY: datetime(year, month, day, hour, minute, second, microsecond)
    }


def ctl_state_with_ref(entity: datetime, reference: datetime):
    return {
        STATE_KEY: entity,
        REF_STATE_KEY: reference,
    }


@pytest.mark.parametrize('min_delta, last_ctl, current_ctl, activation', [
    (None, {}, {}, False),
    (None, {}, ctl_state(2021, 4, 17, 13, 59, 59), True),
    (None, ctl_state(2021, 4, 17, 13, 59, 58), ctl_state(2021, 4, 17, 13, 59, 59), True),
    (None, ctl_state(2021, 4, 17, 13, 59, 59), ctl_state(2021, 4, 17, 13, 59, 59), False),
    ('1h', {}, {}, False),
    ('1h', {}, ctl_state(2021, 4, 17, 13, 59, 59), True),
    ('1h', ctl_state(2021, 4, 17, 12, 59, 59), ctl_state(2021, 4, 17, 13, 59, 58), False),
    ('1h', ctl_state(2021, 4, 17, 12, 59, 59), ctl_state(2021, 4, 17, 13, 59, 59), True),
    ('1h', ctl_state(2021, 4, 17, 12, 59, 59), ctl_state(2021, 4, 17, 14, 00, 00), True),
    ('6h', {}, {}, False),
    ('6h', {}, ctl_state(2021, 4, 17, 11, 59, 59), True),
    ('6h', ctl_state(2021, 4, 17, 5, 59, 59), ctl_state(2021, 4, 17, 11, 59, 58), False),
    ('6h', ctl_state(2021, 4, 17, 5, 59, 59), ctl_state(2021, 4, 17, 11, 59, 59), True),
    ('6h', ctl_state(2021, 4, 17, 5, 59, 59), ctl_state(2021, 4, 17, 12, 00, 00), True),
    ('1d', {}, {}, False),
    ('1d', {}, ctl_state(2021, 4, 17, 23, 59, 59), True),
    ('1d', ctl_state(2021, 4, 16, 23, 59, 59), ctl_state(2021, 4, 17, 23, 59, 58), False),
    ('1d', ctl_state(2021, 4, 16, 23, 59, 59), ctl_state(2021, 4, 17, 23, 59, 59), True),
    ('1d', ctl_state(2021, 4, 16, 23, 59, 59), ctl_state(2021, 4, 18, 00, 00, 00), True),
])
def test_delta_entity_trigger(min_delta, last_ctl, current_ctl, activation):
    if min_delta is None:
        test_trigger = trigger.Delta(*PARAM)
    else:
        test_trigger = trigger.Delta(*PARAM, min_delta)
    assert test_trigger.is_active(last_ctl, current_ctl) == activation


@pytest.mark.parametrize('max_delay, current_ctl, current_time, activation', [
    ('1h', {}, datetime(2021, 4, 19), False),
    ('1h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 15, 59, 59), True),
    ('1h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 16, 0, 0), True),
    ('1h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 16, 0, 1), False),
    ('6h', {}, datetime(2021, 4, 19, 15), False),
    ('6h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 20, 59, 59), True),
    ('6h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 21, 0, 0), True),
    ('6h', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 19, 21, 0, 1), False),
    ('1d', {}, datetime(2021, 4, 19, 15), False),
    ('1d', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 20, 14, 59, 59), True),
    ('1d', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 20, 15, 0, 0), True),
    ('1d', ctl_state(2021, 4, 19, 15), datetime(2021, 4, 20, 15, 0, 1), False),
])
def test_delay_entity_trigger(max_delay, current_ctl, current_time, activation):
    with make_utc_now_mock(current_time):
        test_trigger = trigger.Delay(*PARAM, max_delay)
        assert test_trigger.is_active({}, current_ctl) == activation


@pytest.mark.parametrize('max_delay, current_ctl, activation', [
    ('1h', ctl_state_with_ref(None, datetime(2021, 4, 19)), False),
    ('1h', ctl_state_with_ref(datetime(2021, 4, 19), None), False),
    ('1h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 15, 59, 59)), True),
    ('1h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 16, 0, 0)), True),
    ('1h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 16, 0, 1)), False),
    ('6h', ctl_state_with_ref(None, datetime(2021, 4, 19, 15)), False),
    ('6h', ctl_state_with_ref(datetime(2021, 4, 19, 15), None), False),
    ('6h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 20, 59, 59)), True),
    ('6h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 21, 0, 0)), True),
    ('6h', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 19, 21, 0, 1)), False),
    ('1d', ctl_state_with_ref(None, datetime(2021, 4, 19, 15)), False),
    ('1d', ctl_state_with_ref(datetime(2021, 4, 19, 15), None), False),
    ('1d', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 20, 14, 59, 59)), True),
    ('1d', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 20, 15, 0, 0)), True),
    ('1d', ctl_state_with_ref(datetime(2021, 4, 19, 15), datetime(2021, 4, 20, 15, 0, 1)), False),
])
def test_compare_entity_trigger(max_delay, current_ctl, activation):
    test_trigger = trigger.RefDelay(*PARAM, *REF_PARAM, max_delay)
    assert test_trigger.is_active({}, current_ctl) == activation


@pytest.mark.parametrize('scale, min_delta, last_ctl, current_ctl, activation, tz', [
    (scales.day, None, {}, {}, False, None),
    (scales.day, None, {}, ctl_state(2021, 4, 19), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, None),
    (scales.day, 1, {}, {}, False, None),
    (scales.day, 1, {}, ctl_state(2021, 4, 19), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, None),
    (scales.day, 2, {}, {}, False, None),
    (scales.day, 2, {}, ctl_state(2021, 4, 19), True, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), False, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, None),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, None),

    (scales.day, None, {}, {}, False, dtu.UTC),
    (scales.day, None, {}, ctl_state(2021, 4, 19), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.UTC),
    (scales.day, 1, {}, {}, False, dtu.UTC),
    (scales.day, 1, {}, ctl_state(2021, 4, 19), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.UTC),
    (scales.day, 2, {}, {}, False, dtu.UTC),
    (scales.day, 2, {}, ctl_state(2021, 4, 19), True, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), False, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, dtu.UTC),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.UTC),

    (scales.day, None, {}, {}, False, dtu.MSK),
    (scales.day, None, {}, ctl_state(2021, 4, 19), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
    (scales.day, 1, {}, {}, False, dtu.MSK),
    (scales.day, 1, {}, ctl_state(2021, 4, 19), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
    (scales.day, 2, {}, {}, False, dtu.MSK),
    (scales.day, 2, {}, ctl_state(2021, 4, 19), True, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 3), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 20, 21), True, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 3), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 20, 21), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 3), True, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 3), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 3), False, dtu.MSK),
    (scales.day, 2, ctl_state(2021, 4, 19, 21), ctl_state(2021, 4, 21, 21), True, dtu.MSK),
])
def test_chunk_delta_entity_trigger(scale, min_delta, last_ctl, current_ctl, activation, tz):
    test_trigger = trigger.ChunkDelta(*PARAM, scale, min_delta, tz)
    assert test_trigger.is_active(last_ctl, current_ctl) == activation


@pytest.mark.parametrize('scale, max_delay, current_ctl, current_time, activation, tz', [
    (scales.day, None, {}, datetime(2021, 4, 19), False, None),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, None),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, None),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, None),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), False, None),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, None),
    (scales.day, None, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 0, {}, datetime(2021, 4, 19), False, None),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, None),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 0, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 1, {}, datetime(2021, 4, 19), False, None),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, None),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, None),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, None),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, None),

    (scales.day, None, {}, datetime(2021, 4, 19), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, None, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 0, {}, datetime(2021, 4, 19), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 0, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 1, {}, datetime(2021, 4, 19), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, dtu.UTC),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.UTC),

    (scales.day, None, {}, datetime(2021, 4, 19), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, None, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, 0, {}, datetime(2021, 4, 19), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 0, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, 1, {}, datetime(2021, 4, 19), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 3), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 17, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 17, 21), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 18, 3), datetime(2021, 4, 19, 21), False, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 18, 21), datetime(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 3), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 3), datetime(2021, 4, 19, 21), True, dtu.MSK),
    (scales.day, 1, ctl_state(2021, 4, 19, 21), datetime(2021, 4, 19, 21), True, dtu.MSK),
])
def test_chunk_delay_entity_trigger(scale, max_delay, current_ctl, current_time, activation, tz):
    with make_utc_now_mock(current_time):
        test_trigger = trigger.ChunkDelay(*PARAM, scale, max_delay, tz=tz)
        assert test_trigger.is_active({}, current_ctl) == activation


@pytest.mark.parametrize('scale, max_delay, current_ctl, activation, tz', [
    (scales.day, None, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19), None), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 0, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19), None), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 1, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19), None), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, None),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, None),

    (scales.day, None, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, dtu.UTC),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.UTC),

    (scales.day, None, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, None, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 0, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(None, datetime(2021, 4, 19)), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19), None), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 3)), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 17, 21), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 21)), False, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 18, 21), datetime(2021, 4, 19, 21)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 3)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 3), datetime(2021, 4, 19, 21)), True, dtu.MSK),
    (scales.day, 1, ctl_state_with_ref(datetime(2021, 4, 19, 21), datetime(2021, 4, 19, 21)), True, dtu.MSK),
])
def test_chunk_compare_entity_trigger(scale, max_delay, current_ctl, activation, tz):
    test_trigger = trigger.ChunkRefDelay(*PARAM, *REF_PARAM, scale, max_delay, tz=tz)
    assert test_trigger.is_active({}, current_ctl) == activation


@pytest.mark.parametrize(
    'entity', [
        FakeYtTable,
        FakeGpTable,
        FakeExtSourceProxy(),
    ]
)
def test_entity_trigger_str_and_repr_not_raise(entity):
    class _EntityTrigger(trigger.EntityTrigger):
        def _str_specific_info(self):
            return 'info'

        def is_active(self, last, current):
            return False

    trigger_ = _EntityTrigger(entity, CTL_LAST_LOAD_DATE)
    str(trigger_)
    repr(trigger_)



@pytest.mark.parametrize('scale, last_ctl_dt_1, current_ctl_dt_1, last_ctl_dt_2, current_ctl_dt_2, activation', [
    #  last_ctl_dt                current_ctl_dt
    (
        scales.day,
        datetime(2021, 4, 19, 3), datetime(2021, 4, 20, 3), # FakeGpTable1
        datetime(2021, 4, 19, 3), datetime(2021, 4, 20, 3), # FakeGpTable2
        True # для всех пришли новые данные за вчера
    ),
    (
        scales.day,
        datetime(2021, 4, 17, 3), datetime(2021, 4, 20, 6),  # FakeGpTable1
        datetime(2021, 4, 19, 8), datetime(2021, 4, 20, 1),  # FakeGpTable2
        True  # для FakeGpTable1 данные пришли за 3 суток сразу
    ),
    (
        scales.day,
        datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3),  # FakeGpTable1
        datetime(2021, 4, 19, 3), datetime(2021, 4, 20, 3),  # FakeGpTable2
        False # для FakeGpTable1 нет данных за сегодня
    ),
    (
        scales.day,
        datetime(2021, 4, 18, 3), datetime(2021, 4, 19, 3),  # FakeGpTable1
        datetime(2021, 4, 18, 8), datetime(2021, 4, 19, 3),  # FakeGpTable2
        False  # нет данных за сегодня
    ),
    (
        scales.day,
        datetime(2021, 4, 20, 3), datetime(2021, 4, 20, 8),  # FakeGpTable1
        datetime(2021, 4, 20, 8), datetime(2021, 4, 20, 9),  # FakeGpTable2
        False  # сегодня уже обновляли
    ),

    # scales.month
    (
        scales.month,
        datetime(2021, 3, 19, 3), datetime(2021, 4, 20, 3), # FakeGpTable1
        datetime(2021, 3, 19, 3), datetime(2021, 4, 20, 3), # FakeGpTable2
        True # для всех пришли новые данные за вчера
    ),
    (
        scales.month,
        datetime(2021, 3, 19, 3), datetime(2021, 4, 18, 8),  # FakeGpTable1
        datetime(2021, 3, 15, 3), datetime(2021, 4, 20, 3),  # FakeGpTable2
        True  # актуальная дата отличается, но попадает в текущий месяц,
              # т.е. одна из таблиц обновилась на несколько дней раньше другой
    ),
    (
        scales.month,
        datetime(2021, 1, 17, 3), datetime(2021, 4, 20, 6),  # FakeGpTable1
        datetime(2021, 3, 19, 8), datetime(2021, 4, 20, 1),  # FakeGpTable2
        True  # для FakeGpTable1 данные пришли за 3 месяца сразу
    ),
    (
        scales.month,
        datetime(2021, 1, 18, 3), datetime(2021, 3, 19, 3),  # FakeGpTable1
        datetime(2021, 4, 19, 3), datetime(2021, 4, 20, 3),  # FakeGpTable2
        False  # для FakeGpTable1 неполные данные - актуальный ctl не в текущем месяце
    ),
    (
        scales.month,
        datetime(2021, 1, 18, 3), datetime(2021, 3, 19, 3),  # FakeGpTable1
        datetime(2021, 1, 18, 8), datetime(2021, 3, 19, 3),  # FakeGpTable2
        False  # неполные данные - актуальный ctl не в текущем месяце
    ),
    (
        scales.month,
        datetime(2021, 4, 2, 3), datetime(2021, 4, 4, 8),  # FakeGpTable1
        datetime(2021, 4, 5, 8), datetime(2021, 4, 11, 9),  # FakeGpTable2
        False  # уже обновили данные за
    ),

])
def test_all_arrived_by_prev_chunk(scale, last_ctl_dt_1, current_ctl_dt_1, last_ctl_dt_2, current_ctl_dt_2, activation):
    current_time = datetime(2021, 4, 20, 6)

    last_ctl = {
        'last_load_date@foo1.tab1@gp': last_ctl_dt_1,
        'last_load_date@foo2.tab2@gp': last_ctl_dt_2,
    }
    current_ctl = {
        'last_load_date@foo1.tab1@gp': current_ctl_dt_1,
        'last_load_date@foo2.tab2@gp': current_ctl_dt_2,
    }

    class FakeGpTable1(gp_table.ExternalGPTable):
        __layout__ = gp_table.ExternalGPLayout('foo1', 'tab1')

    class FakeGpTable2(gp_table.ExternalGPTable):
        __layout__ = gp_table.ExternalGPLayout('foo2', 'tab2')

    test_trigger = all_arrived_by_prev_chunk([FakeGpTable1, FakeGpTable2], scale=scale)

    with make_utc_now_mock(current_time):
        assert test_trigger.is_active(last_ctl, current_ctl) == activation
