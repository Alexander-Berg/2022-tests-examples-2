from datetime import datetime
from argparse import Namespace
import mock
from reactor_client.reactor_objects import ArtifactInstance

from dmp_suite import datetime_utils
from dmp_suite.ext_source_proxy.ReactorPartitionPeriods import ReactorPartitionPeriods

from dmp_suite.ext_source_proxy.reactor import ReactorArtifactProxy
from dmp_suite.scales import day, month
from dmp_suite.task.args import use_ctl_last_load_date, utcnow_arg
from dmp_suite.task.base import CTL_EPOCH
from dmp_suite.yt import YTTable, LayeredLayout

DTTM_FORMAT = '%d-%m-%Y-T%H:%M:%S'


class YTFooTable(YTTable):
    __layout__ = LayeredLayout(name='test', layer='test')


def prepare_artifact_instance(user_time):
    return ArtifactInstance(user_time=datetime.fromisoformat(user_time))


def test_reactor_partitions_regular():
    accessor = ReactorPartitionPeriods(path='dummy_path',
                                       scale=day,
                                       start=use_ctl_last_load_date(YTFooTable, default=CTL_EPOCH),
                                       end=utcnow_arg())
    artifacts = [prepare_artifact_instance(x) for x in ['2020-01-01T00:30:30', '2020-01-02T00:00:30', '2020-01-05']]
    periods = [
        datetime_utils.period(start='2020-01-01', end='2020-01-01T23:59:59:999999'),
        datetime_utils.period(start='2020-01-02', end='2020-01-02T23:59:59:999999'),
        datetime_utils.period(start='2020-01-05', end='2020-01-05T23:59:59:999999'),
    ]
    with mock.patch('dmp_suite.ext_source_proxy.ReactorPartitionPeriods.get_artifact_instance_range_by_creation_time',
                    return_value=artifacts):
        assert accessor.get_value(Namespace(), None) == periods


def test_reactor_partitions_extend_to_month():
    accessor = ReactorPartitionPeriods(path='dummy_path',
                                       scale=month,
                                       start=use_ctl_last_load_date(YTFooTable, default=CTL_EPOCH),
                                       end=utcnow_arg())
    artifacts = [prepare_artifact_instance(x) for x in ['2020-01-01T00:30:30', '2020-02-02T00:00:30', '2020-04-01']]
    periods = [
        datetime_utils.period(start='2020-01-01', end='2020-01-31T23:59:59:999999'),
        datetime_utils.period(start='2020-02-01', end='2020-02-29T23:59:59:999999'),
        datetime_utils.period(start='2020-04-01', end='2020-04-30T23:59:59:999999'),
    ]
    with mock.patch('dmp_suite.ext_source_proxy.ReactorPartitionPeriods.get_artifact_instance_range_by_creation_time',
                    return_value=artifacts):
        assert accessor.get_value(Namespace(), None) == periods


def test_reactor_partitions_no_artifacts():
    accessor = ReactorPartitionPeriods(path='dummy_path',
                                       scale=day,
                                       start=use_ctl_last_load_date(YTFooTable, default=CTL_EPOCH),
                                       end=utcnow_arg())
    with mock.patch('dmp_suite.ext_source_proxy.ReactorPartitionPeriods.get_artifact_instance_range_by_creation_time',
                    return_value=[]):
        assert accessor.get_value(Namespace(), None) == []


def test_ctl_entity_algorithm_persistent():
    # если этот тест падает, значит ты меняешь ctl.entity ключ для всех
    # внешних артефактов. Подумай, точно ли оно надо.
    proxy = ReactorArtifactProxy('dummy')
    assert proxy.ctl_entity == 'reactor#dummy'
