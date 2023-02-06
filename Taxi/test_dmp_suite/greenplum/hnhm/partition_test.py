import pytest

from dmp_suite.greenplum.hnhm import table as hnhm_table
from dmp_suite.table import DdsLayout, TableMeta
from dmp_suite.greenplum import String, YearPartitionScale, \
    Datetime, MAX_DATETIME_PARTITION, RangePartitionItem, resolve_meta
from dmp_suite.greenplum.hnhm import HnhmEntity, HnhmLink, HnhmLinkElement, HnhmLinkPartition
from dmp_suite.greenplum.hnhm.exceptions import AttributeControversyException


YPS_DEFAULT_VALID_TO_WO_EXTRA = YearPartitionScale(
    hnhm_table.DEFAULT_VALID_TO,
    start='2019-01-01',
    end='2023-01-01',
    )
YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA = YearPartitionScale(
    hnhm_table.DEFAULT_VALID_TO,
    start='2019-01-01',
    end='2023-01-01',
    extra_partitions=[MAX_DATETIME_PARTITION, ],
)
YPS_DEFAULT_VALID_TO_WITH_SOME_EXTRA = YearPartitionScale(
    hnhm_table.DEFAULT_VALID_TO,
    start='2019-01-01',
    end='2023-01-01',
    extra_partitions=[RangePartitionItem(start='2024-01-01', end='2025-01-01', name='2024')],
)
YPS_DEFAULT_VALID_TO_WITH_MIXED_EXTRA = YearPartitionScale(
    hnhm_table.DEFAULT_VALID_TO,
    start='2019-01-01',
    end='2023-01-01',
    extra_partitions=[
        RangePartitionItem(start='2024-01-01', end='2025-01-01', name='2024'),
        MAX_DATETIME_PARTITION,
    ],
)
YPS_DATETIME_FIELD_WO_EXTRA = YearPartitionScale(
    'datetime_field',
    start='2019-01-01',
    end='2023-01-01',
    )
YPS_DATETIME_FIELD_WO_EXTRA_WITH_SP = YearPartitionScale(
    'datetime_field',
    start='2019-01-01',
    end='2023-01-01',
)


def _serialize_meta(partition):
    if not partition:
        return
    if hasattr(partition, 'serialize_meta'):
        partition = partition.serialize_meta()
    # note: scale is flappy
    partition.pop('scale', None)
    return partition


def _extra_partitions(partition):
    if not partition:
        return
    if hasattr(partition, 'extra_partitions'):
        return partition.extra_partitions


def _get_expected_by_table(table, expected):
    name = table.__name__.lower()
    if name.endswith('key_field'):
        key = 'expected_key_field'
    elif name.endswith('datetime_field'):
        key = 'expected_datetime_field'
    elif name.endswith('string_field'):
        key = 'expected_string_field'
    else:
        raise ValueError('Unknown table type:', name)
    return expected[key]


def _assert_partition_scale(partition_scale, expected):
    partition_scale = _serialize_meta(partition_scale)
    expected = _serialize_meta(expected)
    assert partition_scale == expected


def _assert_extra_partitions(partition_scale, expected):
    partition_scale = _extra_partitions(partition_scale)
    expected = _extra_partitions(expected)
    if partition_scale and expected:
        for partition, expected_partition in zip(partition_scale, expected):
            assert partition == expected_partition
    elif partition_scale or expected:
        assert partition_scale == expected


def run_test(table, expected):
    meta = resolve_meta(table)
    partition_scale = meta.partition_scale
    _assert_partition_scale(partition_scale, expected)
    _assert_extra_partitions(partition_scale, expected)


class WoPartition(HnhmEntity):
    """Сущность без партицирования"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]


class WoPartition2(WoPartition):
    pass


class WithDefaultToPartition(HnhmEntity):
    """Сущность с партицированием полей по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]
    __partition_scale_fields__ = {
        string_field: YPS_DEFAULT_VALID_TO_WO_EXTRA,
    }


class WithDefaultToPartition2(HnhmEntity):
    """Сущность с партицированием полей по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]
    __partition_scale_fields__ = {
        string_field: YPS_DEFAULT_VALID_TO_WO_EXTRA,
        datetime_field: YPS_DEFAULT_VALID_TO_WO_EXTRA,
    }


class WithMixedPartition(HnhmEntity):
    """Сущность со смешанным партицированием (первичное: actual/historic,
    субпартиции: __partition_scale__)"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    __partition_scale__ = YearPartitionScale(
        "datetime_field", start="2019-01-01", end="2023-01-01",
    )
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]


class WithIncorrectPartition(HnhmEntity):
    """Сущность с некорректным партицированием: поля партицирования нет среди
    полей сущности и это не hnhm_table.DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]
    __partition_scale_fields__ = {
        string_field: YearPartitionScale(
            "some_absent_field_dttm", start="2019-01-01", end="2023-01-01",
        ),
    }


class WithIncorrectPartition2(HnhmEntity):
    """Сущность с некорректным партицированием: сущность партицирована
    по какому-то полю, в то же время еще какое-то поле партицировно отдельно.
    Считаем, что в этом случае партиций (вместе с вложенными субпартициями)
    получится слишком много, запрещаем такое определение сущности"""
    __layout__ = DdsLayout(name="some_name", group="some_group")
    __partition_scale__ = YearPartitionScale("datetime_field", start="2015-01-01")
    key_field = String()
    string_field = String()
    datetime_field = Datetime()
    __keys__ = [key_field]
    __partition_scale_fields__ = {
        string_field: YPS_DEFAULT_VALID_TO_WO_EXTRA,
    }


class LinkWoPartition(HnhmLink):
    """Линк без партицирования"""
    __layout__ = DdsLayout(name="some_name", group="link")
    wo_partition = HnhmLinkElement(entity=WoPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    __keys__ = [wo_partition]


class LinkWithDefaultToPartitionWoExtra(HnhmLink):
    """Линк с партицированием по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="link")
    __partition_scale__ = YPS_DEFAULT_VALID_TO_WO_EXTRA
    wo_partition = HnhmLinkElement(entity=WoPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    __keys__ = [wo_partition]


class LinkWithDefaultToPartitionWithMaxExtra(HnhmLink):
    """Линк с партицированием по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="link")
    __partition_scale__ = YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA
    wo_partition = HnhmLinkElement(entity=WoPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    __keys__ = [wo_partition]


class LinkWithDefaultToPartitionWithSomeExtra(HnhmLink):
    """Линк с партицированием по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="link")
    __partition_scale__ = YPS_DEFAULT_VALID_TO_WITH_SOME_EXTRA
    wo_partition = HnhmLinkElement(entity=WoPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    __keys__ = [wo_partition]


class LinkWithDefaultToPartitionWithMixedExtra(HnhmLink):
    """Линк с партицированием по DEFAULT_VALID_TO"""
    __layout__ = DdsLayout(name="some_name", group="link")
    __partition_scale__ = YPS_DEFAULT_VALID_TO_WITH_MIXED_EXTRA
    wo_partition = HnhmLinkElement(entity=WoPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    __keys__ = [wo_partition]


class LinkWithMixedPartition(HnhmLink):
    """Линк со смешанным партицированием (первичное: actual/historic,
    вторичное: HnhmLinkPartition)"""
    __layout__ = DdsLayout(name="some_name", group="link")
    with_mixed_partition = HnhmLinkElement(entity=WithMixedPartition())
    wo_partition2 = HnhmLinkElement(entity=WoPartition2())
    some_field3 = HnhmLinkPartition(
        partition_position=1, link_element=with_mixed_partition)
    __keys__ = [with_mixed_partition]


@pytest.mark.parametrize(
    'cls, entity_class_name, attributes, storage_parameters',
    [
        (hnhm_table.HnhmHubTemplate, 'some_hub_name', {}, None),
        (hnhm_table.HnhmAttributeTemplate, 'some_attribute_name', {},
            hnhm_table.HnhmAttributeTemplate.__storage_parameters__),
        (hnhm_table.HnhmGroupTemplate, 'some_group_name', {},
         hnhm_table.HnhmGroupTemplate.__storage_parameters__),
        (hnhm_table.HnhmLinkTemplate, 'some_link_name', {},
         hnhm_table.HnhmLinkTemplate.__storage_parameters__),
    ]
)
def test__gen_entity_class(cls, entity_class_name, attributes, storage_parameters):
    entity_class = hnhm_table._gen_entity_class(
        cls, entity_class_name, attributes, storage_parameters)
    assert type(entity_class) == TableMeta


@pytest.mark.parametrize(
    'partition_scale, expected',
    [
        (None, False),
        (YearPartitionScale('some_field'), False),
        (YearPartitionScale(hnhm_table.DEFAULT_VALID_TO), True),
    ]
)
def test__is_partitioning_by_default_valid_to(partition_scale, expected):
    assert hnhm_table._is_partitioning_by_default_valid_to(partition_scale) == expected


@pytest.mark.parametrize(
    'partition_scale, expected',
    [
        (None, None),
        (YearPartitionScale('some_field'), YearPartitionScale('some_field')),
        (
            YearPartitionScale(hnhm_table.DEFAULT_VALID_TO, extra_partitions=[MAX_DATETIME_PARTITION]),
            YearPartitionScale(hnhm_table.DEFAULT_VALID_TO, extra_partitions=[MAX_DATETIME_PARTITION]),
        ),
        (
            YearPartitionScale(hnhm_table.DEFAULT_VALID_TO),
            YearPartitionScale(hnhm_table.DEFAULT_VALID_TO, extra_partitions=[MAX_DATETIME_PARTITION]),
        ),
        (
            YPS_DEFAULT_VALID_TO_WO_EXTRA,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
        ),
        (
            YPS_DEFAULT_VALID_TO_WITH_SOME_EXTRA,
            YPS_DEFAULT_VALID_TO_WITH_MIXED_EXTRA,
        ),
    ]
)
def test__add_extra_partition_if_need(partition_scale, expected):
    partition_scale = hnhm_table._add_extra_partition_if_need(partition_scale)
    _assert_partition_scale(partition_scale, expected)
    _assert_extra_partitions(partition_scale, expected)


@pytest.mark.parametrize(
    'cls, expected_common, expected_hub, expected_key_field, expected_string_field, expected_datetime_field',
    [
        (
            WoPartition,
            None,
            None,
            None,
            dict(partition_key='utc_valid_to_dttm'),
            dict(partition_key='utc_valid_to_dttm'),
        ),
        (
            WithDefaultToPartition,
            None,
            None,
            None,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
            dict(partition_key='utc_valid_to_dttm'),
        ),
        (
            WithDefaultToPartition2,
            None,
            None,
            None,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
        ),
        (
            WithMixedPartition,
            YPS_DATETIME_FIELD_WO_EXTRA,
            YPS_DATETIME_FIELD_WO_EXTRA_WITH_SP,
            YPS_DATETIME_FIELD_WO_EXTRA_WITH_SP,
            dict(partition_key='utc_valid_to_dttm'),
            None,
        ),
    ]
)
def test_entity_partitioning(
        cls, expected_common, expected_hub, expected_key_field,
        expected_string_field, expected_datetime_field,
):
    """создаем объект класса HnhmEntity и смотрим на его поля в аспекте партицирования и экстра-партиций"""

    expected = {
        'expected_key_field': expected_key_field,
        'expected_string_field': expected_string_field,
        'expected_datetime_field': expected_datetime_field,
    }

    common_table = cls()
    run_test(common_table, expected_common)
    hub_table = common_table._hub_class
    run_test(hub_table, expected_hub)
    for table in common_table._field_classes.values():
        run_test(table, _get_expected_by_table(table, expected))


@pytest.mark.parametrize(
    'cls, expected_exception',
    [
        (
            WithIncorrectPartition,
            AttributeControversyException,
        ),
        (
            WithIncorrectPartition2,
            AttributeControversyException,
        ),
    ]
)
def test_incorrect_entity_partitioning(cls, expected_exception):
    """создаем объект класса HnhmEntity, а оно падает"""

    with pytest.raises(AttributeControversyException):
        cls()


@pytest.mark.parametrize(
    'cls, expected',
    [
        (
            LinkWoPartition,
            dict(partition_key='utc_valid_to_dttm'),
        ),
        (
            LinkWithDefaultToPartitionWoExtra,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
        ),
        (
            LinkWithDefaultToPartitionWithMaxExtra,
            YPS_DEFAULT_VALID_TO_WITH_MAX_EXTRA,
        ),
        (
            LinkWithDefaultToPartitionWithSomeExtra,
            YPS_DEFAULT_VALID_TO_WITH_MIXED_EXTRA,
        ),
        (
            LinkWithDefaultToPartitionWithMixedExtra,
            YPS_DEFAULT_VALID_TO_WITH_MIXED_EXTRA,
        ),
        (
            LinkWithMixedPartition,
            dict(partition_key='utc_valid_to_dttm'),
        ),
    ]
)
def test_link_partitioning(cls, expected):
    """создаем объект класса HnhmLink и смотрим на него поля в аспекте партицирования и экстра-партиций"""
    run_test(cls()._link_class, expected)
