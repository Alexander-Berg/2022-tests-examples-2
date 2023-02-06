from datetime import timedelta

import pytest
import uuid

from dmp_suite.ctl import CTL_LAST_LOAD_DATE
from dmp_suite.descriptors import AttributeDescriptorException
from dmp_suite.greenplum.hnhm import HnhmEntity, HnhmLink, HnhmLinkElement, sla
from dmp_suite.greenplum.hnhm.exceptions import (
    PartitionKeyInGroupException, GroupWithFieldNameException, GroupChangetypeException, GroupHubLeftBoundException,
    LinkHubLeftBoundKey,
)

from dmp_suite.table import ChangeType, DdsLayout, Sla, ValidateError

from dmp_suite.greenplum import GPMeta, Int, String, YearPartitionScale, Datetime
from test_dmp_suite.greenplum.utils import TestLayout


SERVICE_ETL = 'taxi_etl'


class WrongEntity1(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    id_1 = Int()
    id_2 = Int(group='z')
    attr1 = String(change_type=ChangeType.IGNORE)

    __keys__ = [id_1, id_2]


class WrongEntity2(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('dt', start='2020-01-01')

    id_1 = Int()
    id_2 = Int()
    dt = Datetime(group='z')
    attr1 = String(change_type=ChangeType.IGNORE)

    __keys__ = [id_1, id_2]


class WrongEntity3(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('dt', start='2020-01-01')

    id_1 = Int()
    id_2 = Int()
    dt = Datetime()
    attr1 = String(group='id_1')
    attr2 = String(group='id_1')

    __keys__ = [id_1, id_2]


class WrongEntity4(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('dt', start='2020-01-01')

    id_1 = Int()
    id_2 = Int()
    dt = Datetime()
    attr1 = String(group='z', change_type=ChangeType.UPDATE)
    attr2 = String(group='z', change_type=ChangeType.NEW)

    __keys__ = [id_1, id_2]


class WrongEntity5(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('dt', start='2020-01-01')

    id_1 = Int()
    id_2 = Int()
    dt = Datetime()
    attr1 = String(group='z', hub_left_bound=True)
    attr2 = String(group='z', hub_left_bound=False)

    __keys__ = [id_1, id_2]


class Entity1(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)

    id_1 = Int()
    id_2 = Int()
    attr1 = String(change_type=ChangeType.IGNORE)

    __keys__ = [id_1, id_2]


class Entity2(HnhmEntity):
    __layout__ = DdsLayout('e_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    __partition_scale__ = YearPartitionScale('dt', start='2020-01-01')

    id_1 = Int()
    id_2 = Int()
    dt = Datetime()
    attr1 = String(change_type=ChangeType.IGNORE)

    __keys__ = [id_1, id_2]


class WrongLink1(HnhmLink):
    __layout__ = DdsLayout('l_' + str(uuid.uuid4().hex)[0:10], group='demand', prefix_key=SERVICE_ETL)
    hub_left_bound = True

    ent_1 = HnhmLinkElement(entity=Entity1())
    ent_2 = HnhmLinkElement(entity=Entity2())

    __keys__ = [ent_1, ent_2]


def test_entity():
    with pytest.raises(PartitionKeyInGroupException):
        GPMeta(WrongEntity2)

    with pytest.raises(GroupWithFieldNameException):
        GPMeta(WrongEntity3)

    with pytest.raises(GroupChangetypeException):
        GPMeta(WrongEntity4)

    with pytest.raises(GroupHubLeftBoundException):
        GPMeta(WrongEntity5)

    with pytest.raises(LinkHubLeftBoundKey):
        GPMeta(WrongLink1)


def test_validate_sla():
    # Вот так вот не надо
    with pytest.raises(ValidateError) as exception:
        class WrongWay1(HnhmEntity):
            __layout__ = TestLayout('test_layout')
            __sla__ = [
                sla.attribute('a', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
                sla.attribute('a', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
            ]
            a = Int()
            __keys__ = [a]

    assert exception.value.args[0] == 'Detected at least two identical ctl_param related to the same field: a.'

    with pytest.raises(ValidateError) as exception:
        class WrongWay2(HnhmEntity):
            __layout__ = TestLayout('test_layout')
            __sla__ = [
                sla.attribute('b', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
                sla.attribute('c', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(2))),
            ]
            a = Int()
            b = String(group='x')
            c = String(group='x')
            __keys__ = [a]

    assert exception.value.args[0].startswith(
        'Detected at least two identical ctl_param with different SLA related to the same storage_entity:'
    )

    with pytest.raises(TypeError) as exception:
        class WrongWay3(HnhmEntity):
            __sla__ = sla.attribute('a', sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),  # Wrong trailing comma!
            a = String(group='x')
            __keys__ = [a]

    with pytest.raises(ValidateError) as exception:
        class WrongWay4(HnhmEntity):
            __layout__ = TestLayout('test_layout')
            __sla__ = [
                sla.attributes('b', 'c', sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
                sla.attribute('b', sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),  # Detected field 'b'
            ]
            a = Int()
            b = String(group='x')
            c = String(group='x')
            __keys__ = [a]
    assert exception.value.args[0] == 'Detected at least two identical ctl_param related to the same field: b.'

    with pytest.raises(ValidateError) as exception:
        class WrongWay5(HnhmEntity):
            __partition_scale__ = YearPartitionScale('c')
            __layout__ = TestLayout('test_layout')
            __sla__ = [
                # Пытаемся задать SLA на поле 'c', которое использовано в __partition_scale__.
                sla.attribute('c', sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
            ]
            a = Int()
            b = String()
            c = Datetime()
            __keys__ = [a]
    assert exception.value.args[0].startswith('Detected ctl_param related to field c')

    # Надо вот так, так, так
    class RightWay1(HnhmEntity):
        __layout__ = TestLayout('test_layout')
        __sla__ = sla.attribute('a', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(123)))
        a = String()
        __keys__ = [a]
    assert len(RightWay1.get_sla()) == 1

    class RightWay2(HnhmEntity):
        __layout__ = TestLayout('test_layout')
        __sla__ = sla.default(Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(123)))
        a = String()
        __keys__ = [a]
    assert len(RightWay2.get_sla()) == 1

    class RightWay3(HnhmEntity):
        __layout__ = TestLayout('test_layout')
        __sla__ = [
            sla.attributes('b', 'c', sla=Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
        ]
        a = Int()
        b = String(group='x')
        c = String(group='x')
        __keys__ = [a]
    assert len(RightWay3.get_sla()) == 2

    class RightWay4(HnhmEntity):
        __layout__ = TestLayout('test_layout')
        __sla__ = [
            sla.default(Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(1))),
            sla.attribute('b', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(2))),
            sla.attribute('c', Sla(CTL_LAST_LOAD_DATE, warn_lag=timedelta(2))),
        ]
        a = Int()
        b = String(group='x')
        c = String(group='x')
        __keys__ = [a]
    assert len(RightWay4.get_sla()) == 3
    # Понятно, я понял


class _EntityWithoutKeys(HnhmEntity):
    __layout__ = DdsLayout(
        'e_' + str(uuid.uuid4().hex)[0:10],
        group='demand',
        prefix_key=SERVICE_ETL,
    )


def test_keys_are_required():
    with pytest.raises(AttributeDescriptorException):
        _ = _EntityWithoutKeys.__keys__

    with pytest.raises(AttributeDescriptorException):
        _ = _EntityWithoutKeys().__keys__
