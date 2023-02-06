import asyncio
import re

from noc.grad.grad.lib.fns import FNS
from noc.grad.grad.lib.functions import dict_to_map
from noc.grad.grad.lib.pipeline import pipeline, finalization_cast
from noc.grad.grad.lib.scheduler import Job
from noc.grad.grad.lib.snmp_helper import Oid
from noc.grad.grad.lib.structures import FrozenDict
from noc.grad.grad.pollers.snmp_poller import Poller as snmp_poller
from noc.grad.grad.test.data import debugspb1s2


def test_pipeline():
    host = "host"
    skip_key_expr = FrozenDict({'ifname': re.compile('(Tunnel|NULL|(In)?LoopBack|.+-mplste|Sip|Virtual-Template)')})
    counters = (
        Oid(oid_name="ifmib.ifDescr", options=('use_snmpbulkget',)),
        Oid(oid_name="ifmib.ifAlias", options=('use_snmpbulkget',)),
        Oid(oid_name="ifmib.ifHighSpeed", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifHCInOctets", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifHCOutOctets", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifHCInUcastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifHCOutUcastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifInNUcastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOutNUcastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.hwIfEtherStatInJumboPkts", options=('use_snmpget', 'none_to_zero')),
        Oid(oid_name="ifmib.hwIfEtherStatOutJumboPkts", options=('use_snmpget', 'none_to_zero')),
        Oid(oid_name="ifmib.hwIfEtherStatInPausePkts", options=('use_snmpget', 'none_to_zero')),
        Oid(oid_name="ifmib.hwIfEtherStatOutPausePkts", options=('use_snmpget', 'none_to_zero')),
        Oid(oid_name="ifmib.ifInDiscards", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOutDiscards", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifInErrors", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOutErrors", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOperStatus", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifAdminStatus", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifLastChange", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifInMulticastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOutMulticastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifInBroadcastPkts", options=('use_snmpget',)),
        Oid(oid_name="ifmib.ifOutBroadcastPkts", options=('use_snmpget',)),
    )
    interval = 60
    key_data = FrozenDict(
        {
            'series_params': FrozenDict({'min_interval': interval}),
            'exchange': 'local_grad',
            'orig_poller_name': 'SNMP network huawei',
            'series_interval': interval,
            'connect': host,
            'host': host,
            'series': 'network',
            'interval': interval,
            'poller_params': FrozenDict(
                {
                    'post_fn': (
                        'rearrange_partial_data',
                        'huawei_counters_workaround',
                        'sum_ifmib_counters_new',
                        'check_net_data_sanity',
                    ),
                    'timeout': 10,
                    'skip_key_expr': skip_key_expr,
                    'counters': counters,
                }
            ),
            'host_key': host,
            'poller_name': 'SNMP network huawei',
        }
    )
    aux_data = {'host_data': {'host': host, 'connect': host}}
    job = Job(
        name='host_unique in SNMP network huawei',
        key_data=key_data,
        aux_data=aux_data,
        afterburn=1,
        job_type=None,
        scattering_percent=False,
    )
    poller = snmp_poller(asyncio.Queue(), asyncio.Queue())
    poller.prepare_job(job)

    fns = FNS(
        all_keys=(
            'speed',
            'rx',
            'tx',
            'rx_unicast',
            'tx_unicast',
            'rx_nunicast',
            'tx_nunicast',
            'rx_jumbo',
            'tx_jumbo',
            'rx_pause',
            'tx_pause',
            'rx_drop',
            'tx_drop',
            'rx_errs',
            'tx_errs',
            'oper_status',
            'admin_status',
            'flap',
            'rx_multicast',
            'tx_multicast',
            'rx_broadcast',
            'tx_broadcast',
        )
    )
    fns._data = dict_to_map(
        {
            'speed': ['resampler_repeat_60_720'],
            'rx': [('speed', ({'max_time_delta': 720, 'resample': interval, 'factor': 8}))],
            'tx': [('speed', ({'max_time_delta': 720, 'resample': interval, 'factor': 8}))],
            'rx_unicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_unicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_nunicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_nunicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_jumbo': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_jumbo': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_pause': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_pause': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_drop': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_drop': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_errs': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_errs': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'oper_status': ['resampler_repeat_60_720'],
            'admin_status': ['resampler_repeat_60_720'],
            'flap': ['delta_count', 'resampler_repeat_60_720'],
            'rx_multicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_multicast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'rx_broadcast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
            'tx_broadcast': [('speed', ({'max_time_delta': 720, 'resample': interval}))],
        }
    )

    cast_fn_args = FrozenDict({'speed': 'int', 'oper_status': 'int', 'admin_status': 'int'})
    post_fn = [
        'rearrange_partial_data',
        'huawei_counters_workaround',
        'sum_ifmib_counters_new',
        'check_net_data_sanity',
        lambda: finalization_cast(cast_fn_args),
    ]
    p = pipeline(job, fns, post_fn, additional_tags={"host": host})

    res = []

    for data in debugspb1s2.datas:
        item_res = p.send(data)
        res.append(item_res)

    assert res == debugspb1s2.exp_res
