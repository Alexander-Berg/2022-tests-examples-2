# pylint: disable=C0302

import datetime
import logging
import urllib.parse

import psycopg2.tz
import pytest

logger = logging.getLogger(__name__)

ENDPOINT = '/external/v1/calls/balance'
HEADERS = {'Content-Type': 'application/x-www-form-urlencoded'}

SUBCLUSTERS = {
    's1': {
        'endpoint': 'QPROC-s1',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 1,
    },
    's2': {
        'endpoint': 'QPROC-s2',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
        'endpoint_strategy_option': 2,
    },
    'reserve': {
        'endpoint': 'QPROC-reserve',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
    },
    'broken_cluster': {
        'endpoint': 'QPROC-broken',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
    },
    'unknown_cluster': {
        'endpoint': 'QPROC-unknown',
        'endpoint_count': 2,
        'endpoint_strategy': 'TOPDOWN',
        'timeout_sec': 300,
    },
}
DEFAULT_METAQUEUES = [
    {
        'name': 'disp',
        'number': '123',
        'allowed_clusters': ['s1', 's2', 'broken_cluster'],
        'disabled_clusters': {
            'disabled_for_routing': ['broken_cluster', 'unknown_cluster'],
        },
        'tags': [],
    },
]


def fill_db(pgsql, cc_metaqueues):
    cursor = pgsql['callcenter_queues'].cursor()
    for metaqueue in cc_metaqueues:
        for cluster in metaqueue['allowed_clusters']:
            if (
                    metaqueue.get('disabled_clusters')
                    and metaqueue['disabled_clusters'].get(
                        'disabled_for_routing',
                    )
                    and cluster
                    in metaqueue['disabled_clusters']['disabled_for_routing']
            ):
                routing_enabled = False
            else:
                routing_enabled = True
            cursor.execute(
                f"""INSERT INTO callcenter_queues.callcenter_system_info
               (
               metaqueue,
               subcluster,
               enabled_for_call_balancing,
               enabled_for_sip_user_autobalancing,
               enabled
               )
               VALUES
               (
               '{metaqueue['name']}',
                '{cluster}',
                {routing_enabled},
                true,
                true
               )
               ON CONFLICT (metaqueue, subcluster) DO UPDATE SET
               enabled_for_call_balancing = {routing_enabled};""",
            )
    cursor.close()


class Call:
    def __init__(
            self,
            agent_id,
            answered_at,
            call_guid,
            call_id,
            called_number,
            completed_at,
            endreason,
            queue,
            queued_at,
            transfered_to,
            commutation_id,
    ):
        self.agent_id = agent_id
        self.answered_at = answered_at
        self.call_guid = call_guid
        self.call_id = call_id
        self.called_number = called_number
        self.completed_at = completed_at
        self.endreason = endreason
        self.queue = queue
        self.queued_at = queued_at
        self.transfered_to = transfered_to
        self.commutation_id = commutation_id

    @staticmethod
    def from_json(call: dict):
        return Call(
            agent_id=call['agent_id'],
            answered_at=datetime.datetime.fromtimestamp(
                call['answered_at_ms'] / 1000,
                tz=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            call_guid=call['call_guid'],
            call_id=call['call_id'],
            called_number=call['called_number'],
            completed_at=datetime.datetime.fromtimestamp(
                call['completed_at_ms'] / 1000,
                tz=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            endreason=call['endreason'],
            queue=call['queue'],
            queued_at=datetime.datetime.fromtimestamp(
                call['queued_at_ms'] / 1000,
                tz=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
            ),
            transfered_to=call['transfered_to'],
            commutation_id=call['commutation_id'],
        )

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return str(self)

    @property
    def hold_time(self):
        return self.answered_at - self.queued_at

    @property
    def call_time(self):
        return self.completed_at - self.answered_at

    @property
    def hold_time_sec(self):
        return int(self.hold_time.total_seconds())

    @property
    def call_time_sec(self):
        return int(self.call_time.total_seconds())


class QappEvent:
    META_FORMAT = (
        '{{"NODE":"TESTSUITE","PARTITION":"TAXI1",'
        '"DATE":{date},'
        '"CALLID":"{call.call_id}",'
        '"QUEUENAME":"{call.queue}",'
        '"AGENT":null,'
        '"ACTION":"META",'
        '"DATA1":"0",'
        '"DATA2":"{call.call_guid}",'
        '"DATA3":"X-CC-OriginalDN",'
        '"DATA4":"{call.called_number}",'
        '"DATA5":"{call.commutation_id}",'
        '"DATA6":null,"DATA7":null,"DATA8":null,'
        '"OTHER":null}}'
    )
    ENTERQUEUE_FORMAT = (
        '{{"NODE":"TESTSUITE",'
        '"PARTITION":"TAXI1",'
        '"DATE":{date},'
        '"CALLID":"{call.call_id}",'
        '"QUEUENAME":"{call.queue}",'
        '"AGENT":null,'
        '"ACTION":"ENTERQUEUE",'
        '"DATA1":"",'
        '"DATA2":"+79991111111",'
        '"DATA3":"11",'
        '"DATA4":null,"DATA5":null,"DATA6":null,'
        '"DATA7":null,"DATA8":null,"OTHER":null}}'
    )
    CONNECT_FORMAT = (
        '{{"NODE":"TESTSUITE",'
        '"PARTITION":"TAXI1",'
        '"DATE":{date},'
        '"CALLID":"{call.call_id}",'
        '"QUEUENAME":"{call.queue}",'
        '"AGENT":"Agent/{call.agent_id}",'
        '"ACTION":"CONNECT",'
        '"DATA1":"{call.hold_time_sec}",'
        '"DATA2":"",'
        '"DATA3":"1",'
        '"DATA4":null,"DATA5":null,"DATA6":null,"DATA7":null,'
        '"DATA8":null,"OTHER":null}}'
    )
    COMPLETECALLER_FORMAT = (
        '{{"NODE":"TESTSUITE",'
        '"PARTITION":"TAXI1",'
        '"DATE":{date},'
        '"CALLID":"{call.call_id}",'
        '"QUEUENAME":"{call.queue}",'
        '"AGENT":"Agent/{call.agent_id}",'
        '"ACTION":"COMPLETECALLER",'
        '"DATA1":"{call.hold_time_sec}",'
        '"DATA2":"{call.call_time_sec}",'
        '"DATA3":"11",'
        '"DATA4":null,"DATA5":null,"DATA6":null,'
        '"DATA7":null,"DATA8":null,"OTHER":null}}'
    )

    META = 'META'
    ENTERQUEUE = 'ENTERQUEUE'
    CONNECT = 'CONNECT'
    COMPLETECALLER = 'COMPLETECALLER'
    QAPPEVENT_TYPES = [META, ENTERQUEUE, CONNECT, COMPLETECALLER]

    def __init__(
            self, event_type: str, date: int, call: Call, format_str: str,
    ):
        self.event_type = event_type
        self.date = date
        self.call = call
        self.format_str = format_str

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.format_str.format(
            call=self.call, date=int(self.date.timestamp()),
        )

    @staticmethod
    def make_meta(call: Call):
        return QappEvent(
            QappEvent.META, call.queued_at, call, QappEvent.META_FORMAT,
        )

    @staticmethod
    def make_enterqueue(call: Call):
        return QappEvent(
            QappEvent.ENTERQUEUE,
            call.queued_at,
            call,
            QappEvent.ENTERQUEUE_FORMAT,
        )

    @staticmethod
    def make_connect(call: Call):
        return QappEvent(
            QappEvent.CONNECT,
            call.answered_at,
            call,
            QappEvent.CONNECT_FORMAT,
        )

    @staticmethod
    def make_completecaller(call: Call):
        return QappEvent(
            QappEvent.COMPLETECALLER,
            call.completed_at,
            call,
            QappEvent.COMPLETECALLER_FORMAT,
        )


async def _test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        lb_message_sender,
        taxi_config,
):
    await taxi_callcenter_queues.invalidate_caches()
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))

    call_map = dict()

    @testpoint('call-routing-prioritization')
    def prioritization(data):
        nonlocal call_map
        call_guid = data['call_guid']
        if call_guid not in call_map:
            call_map[call_guid] = {'call_guid': call_guid}
        call_map[call_guid]['priorities'] = {
            sub['name']: sub['priority'] for sub in data['subclusters']
        }

    async def call_balance(
            _qapp_event, _metaqueue, metaqueue_number, expected_subcluster,
    ):
        response = await taxi_callcenter_queues.post(
            ENDPOINT,
            headers=HEADERS,
            data=urllib.parse.urlencode(
                {
                    'GUID': _qapp_event.call.call_guid,
                    'CALLED_DN': metaqueue_number,
                },
            ),
        )
        assert response.status_code == 200
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['1']
        assert queue_action['ACTION'] == 'QUEUE'
        assert (
            queue_action['VALUE'] == _metaqueue + '_on_' + expected_subcluster
        )
        _qapp_event.call.queue = _metaqueue + '_on_' + expected_subcluster

    # load calls from json
    calls_json = load_json(call_history)['items']
    # convert jsons to objects
    calls = list()
    for call_json in calls_json:
        call = Call.from_json(call_json)
        calls.append(call)
    # convert calls to Qapp events
    qapp_events = list()
    for call in calls:
        qapp_events.append(QappEvent.make_meta(call))
        qapp_events.append(QappEvent.make_enterqueue(call))
        if call.agent_id:
            qapp_events.append(QappEvent.make_connect(call))
            qapp_events.append(QappEvent.make_completecaller(call))
    expected_queue = {}
    for expected_routed_call in expected_routed_calls:
        expected_queue[expected_routed_call[0]] = (
            expected_routed_call[2].split('_on_')[0],  # metaqueue
            expected_routed_call[2].split('_on_')[1],  # subcluster
        )
    # reorder events dy date
    qapp_events.sort(key=lambda x: x.date)
    # Push data
    for qapp_event in qapp_events:
        if qapp_event.event_type == QappEvent.META:
            # Update time mock to qapp_event time
            await set_now(qapp_event.date)
            metaqueue = expected_queue[qapp_event.call.call_guid][0]
            # Call balance
            await call_balance(
                qapp_event,
                metaqueue,  # metaqueue
                [
                    i['number']
                    for i in taxi_config.get('CALLCENTER_METAQUEUES')
                    if i['name'] == metaqueue
                ][
                    0
                ],  # metaqueue_number
                expected_queue[qapp_event.call.call_guid][1],  # subcluster
            )
        await lb_message_sender.send(str(qapp_event), raw=True)
    # Map data
    assert prioritization.has_calls
    priorities = []
    expected_priorities = []
    for expected_routed_call in expected_routed_calls:
        call_guid = expected_routed_call[0]
        priorities.append(
            {
                's1': (
                    call_map[call_guid]['priorities']['s1']
                    if 's1' in call_map[call_guid]['priorities']
                    else None
                ),
                's2': (
                    call_map[call_guid]['priorities']['s2']
                    if 's2' in call_map[call_guid]['priorities']
                    else None
                ),
            },
        )
        expected_priorities.append(
            {'s1': expected_routed_call[3], 's2': expected_routed_call[4]},
        )

    # Check priorities
    assert priorities == expected_priorities


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.parametrize(
    ['call_history', 'expected_routed_calls'],
    (
        pytest.param(
            'seq_calls.json',
            [
                ('call_guid_11', '+79990007711', 'disp_on_s1', 1.0, 1.0),
                ('call_guid_12', '+79990007712', 'disp_on_s1', 1.0, 1.0),
                ('call_guid_13', '+79990007713', 'disp_on_s1', 1.0, 1.0),
                ('call_guid_14', '+79990007714', 'disp_on_s1', 1.0, 1.0),
                ('call_guid_15', '+79990007715', 'disp_on_s1', 1.0, 1.0),
            ],
            id='sequential calls',
        ),
        pytest.param(
            'sim_calls.json',
            [
                ('call_guid_11', '+79990007711', 'disp_on_s1', 1.0, 1.0),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s2',
                    0.6666666666666666,
                    1.0,
                ),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    0.6666666666666666,
                    0.5,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s2',
                    0.3333333333333333,
                    0.5,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
            ],
            id='simultaneous calls',
        ),
        pytest.param(
            # Calls pipeline in time, ms
            # @startuml pattern
            # control 100
            # control 150
            # control 200
            # control 250
            # control 300
            # control 350
            # control 400
            # control 450
            # control 500
            # control 550
            # autonumber
            # 100 -> 200: call_guid_11 - disp_on_s1 - sip11
            # 150 -> 400: call_guid_12 - disp_on_s2 - sip21
            # 250 -> 450: call_guid_13 - disp_on_s1 - sip11
            # 300 -> 550: call_guid_14 - disp_on_s1 - sip12
            # 350 -> 550: call_guid_15 - disp_on_s2 - sip22
            # 500 -> 550: call_guid_16 - disp_on_s1 - sip11
            # @enduml
            'pattern_calls.json',
            [
                ('call_guid_11', '+79990007711', 'disp_on_s1', 1.0, 1.0),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s2',
                    0.66666666666666666,
                    1.0,
                ),
                (  # call_guid_11 already ended
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    1.0,
                    0.5,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s1',
                    0.66666666666666666,
                    0.5,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s2',
                    0.33333333333333333,
                    0.5,
                ),
                (
                    'call_guid_16',
                    '+79990007716',
                    'disp_on_s1',
                    0.66666666666666666,
                    0.5,
                ),
            ],
            id='pattern calls',
        ),
        pytest.param(
            'queue_seq_calls.json',
            [
                ('call_guid_01', '+79990007701', 'disp_on_s1', 1.0, 1.0),
                (
                    'call_guid_02',
                    '+79990007702',
                    'disp_on_s2',
                    0.6666666666666666,
                    1.0,
                ),
                (
                    'call_guid_03',
                    '+79990007703',
                    'disp_on_s1',
                    0.6666666666666666,
                    0.5,
                ),
                (
                    'call_guid_04',
                    '+79990007704',
                    'disp_on_s2',
                    0.3333333333333333,
                    0.5,
                ),
                (
                    'call_guid_11',
                    '+79990007711',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
            ],
            id='sequential calls in queue',
        ),
        pytest.param(
            'queue_sim_calls.json',
            [
                ('call_guid_01', '+79990007701', 'disp_on_s1', 1.0, 1.0),
                (
                    'call_guid_02',
                    '+79990007702',
                    'disp_on_s2',
                    0.6666666666666666,
                    1.0,
                ),
                (
                    'call_guid_03',
                    '+79990007703',
                    'disp_on_s1',
                    0.6666666666666666,
                    0.5,
                ),
                (
                    'call_guid_04',
                    '+79990007704',
                    'disp_on_s2',
                    0.3333333333333333,
                    0.5,
                ),
                (
                    'call_guid_05',
                    '+79990007705',
                    'disp_on_s1',
                    0.3333333333333333,
                    0.0,
                ),
                ('call_guid_11', '+79990007711', 'disp_on_s1', 0.0, 0.0),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s2',
                    -0.3333333333333333,
                    0.0,
                ),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    -0.3333333333333333,
                    -0.5,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s2',
                    -0.6666666666666666,
                    -0.5,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s1',
                    -0.6666666666666666,
                    -1.0,
                ),
            ],
            id='simultaneous calls in queue',
        ),
        pytest.param(
            'sim_calls_s1_only.json',
            [
                (
                    'call_guid_11',
                    '+79990007711',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
            ],
            id='simultaneous calls, reduced subclusters',
            marks=pytest.mark.config(
                CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
                    's1': {
                        'endpoint': 'QPROC-s1',
                        'endpoint_count': 2,
                        'endpoint_strategy': 'TOPDOWN',
                        'timeout_sec': 300,
                        'endpoint_strategy_option': 1,
                    },
                },
            ),
        ),
        pytest.param(
            'sim_calls_s1_only.json',
            [
                (
                    'call_guid_11',
                    '+79990007711',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_12',
                    '+79990007712',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_14',
                    '+79990007714',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
                (
                    'call_guid_15',
                    '+79990007715',
                    'disp_on_s1',
                    -1.7976931348623157e308,
                    None,
                ),
            ],
            id='simultaneous calls, reduced subclusters by allowed_clusters',
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['s1', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
    ),
)
async def test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        mock_personal,
        lb_message_sender,
        taxi_config,
):
    await _test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        lb_message_sender,
        taxi_config,
    )


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.parametrize(
    ['call_history', 'expected_routed_calls'],
    (
        pytest.param(
            'postcall_processing_calls.json',
            [
                ('call_guid_01', '+79990007701', 'disp_on_s1', 1.0, 1.0),
                # second call income in 10 after first ends
                ('call_guid_02', '+79990007702', 'disp_on_s1', 1.0, 1.0),
            ],
            id='no postcall',
            marks=[
                pytest.mark.pgsql(
                    'callcenter_queues', files=['insert_agents_3_2.sql'],
                ),
                pytest.mark.config(
                    CALLCENTER_POSTCALL_PROCESSING_TIME_MAP={'__default__': 0},
                ),
            ],
        ),
        pytest.param(
            'postcall_processing_calls.json',
            [
                ('call_guid_01', '+79990007701', 'disp_on_s1', 1.0, 1.0),
                # second call income in 10 after first ends
                (
                    'call_guid_02',
                    '+79990007702',
                    'disp_on_s2',
                    0.66666666666666666,
                    1.0,
                ),
            ],
            id='20sec postcall',
            marks=[
                pytest.mark.pgsql(
                    'callcenter_queues', files=['insert_agents_3_2.sql'],
                ),
                pytest.mark.config(
                    CALLCENTER_POSTCALL_PROCESSING_TIME_MAP={
                        '__default__': 20,
                    },
                ),
            ],
        ),
    ),
)
async def test_postcall_processing_time(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        mock_personal,
        lb_message_sender,
        taxi_config,
):
    await _test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        lb_message_sender,
        taxi_config,
    )


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp',
            'number': '123',
            'allowed_clusters': ['s1', 's2', 'broken_cluster'],
            'disabled_clusters': {'disabled_for_routing': ['broken_cluster']},
        },
        {
            'name': 'corp',
            'number': '456',
            'allowed_clusters': ['s1', 's2', 'broken_cluster'],
            'disabled_clusters': {'disabled_for_routing': ['broken_cluster']},
        },
    ],
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_corp.sql'])
@pytest.mark.parametrize(
    ['call_history', 'expected_routed_calls'],
    (
        pytest.param(
            'disp_calls.json',
            [('call_guid_11', '+79990007711', 'disp_on_s1', 1.0, 1.0)],
            id='disp only calls',
        ),
        pytest.param(
            'corp_disp_calls.json',
            [
                ('call_guid_11', '+79990000000', 'corp_on_s1', 1.0, None),
                ('call_guid_12', '+79990000000', 'corp_on_s1', 0.5, None),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s2',
                    0.3333333333333333,
                    1.0,
                ),
            ],
            id='corp+disp calls (v1)',
        ),
        pytest.param(
            'corp_disp_calls.json',
            [
                ('call_guid_11', '+79990000000', 'corp_on_s1', 1.0, None),
                ('call_guid_12', '+79990000000', 'corp_on_s1', 0.5, None),
                (
                    'call_guid_13',
                    '+79990007713',
                    'disp_on_s2',
                    0.3333333333333333,
                    1.0,
                ),
            ],
            id='corp+disp calls',
        ),
    ),
)
async def test_queue_intersection(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        mock_personal,
        lb_message_sender,
        taxi_config,
):
    await _test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        lb_message_sender,
        taxi_config,
    )


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.now('2020-05-01T10:00:01.00Z')
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.pgsql('callcenter_queues', files=['insert_routed_calls.sql'])
@pytest.mark.parametrize(
    [
        'expected_code',
        'expected_queue',
        'idempotency_token',
        'expected_routed_calls',
    ],
    (
        pytest.param(
            200,
            'disp_on_s2',
            None,
            [
                'call_guid_1=>disp_on_s2',
                'call_guid_1=>disp_on_s1',
                'call_guid_2=>disp_on_s1',
            ],
            id='no idempotency_token',
        ),
        pytest.param(
            200,
            'disp_on_s1',
            'idempotency_token_1',
            ['call_guid_1=>disp_on_s1', 'call_guid_2=>disp_on_s1'],
            id='idempotency_token_1',
        ),
        pytest.param(
            200,
            'disp_on_s2',
            'idempotency_token_3',
            [
                'call_guid_1=>disp_on_s2',
                'call_guid_1=>disp_on_s1',
                'call_guid_2=>disp_on_s1',
            ],
            id='idempotency_token_3, retry after transfer',
        ),
    ),
)
async def test_balance_idempotency(
        taxi_callcenter_queues,
        testpoint,
        expected_code,
        expected_queue,
        idempotency_token,
        pgsql,
        expected_routed_calls,
        taxi_config,
):
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))
    headers = {}
    if idempotency_token:
        headers['X-Idempotency-Token'] = idempotency_token

    headers = HEADERS.copy()
    if idempotency_token:
        headers['X-Idempotency-Token'] = idempotency_token

    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=headers,
        data=urllib.parse.urlencode(
            {'GUID': 'call_guid_1', 'CALLED_DN': '123'},
        ),
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['1']
        assert queue_action['ACTION'] == 'QUEUE'
        assert queue_action['VALUE'] == expected_queue

    # Check details
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT call_guid, metaqueue, subcluster, created_at'
        ' FROM callcenter_queues.routed_calls'
        ' ORDER BY call_guid, created_at NULLS FIRST',
    )
    routed_calls = []
    for record in cursor.fetchall():
        routed_calls.append(f'{record[0]}=>{record[1]}_on_{record[2]}')

    assert set(routed_calls) == set(expected_routed_calls)


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.now('2020-05-01 10:05:00.00')
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.pgsql('callcenter_queues', files=['insert_routed_calls.sql'])
@pytest.mark.parametrize(
    ['expected_code', 'expected_queue', 'expected_routed_call'],
    (
        pytest.param(
            200,
            # 2 calls routed to disp_on_s1 are taken into account
            'disp_on_s2',
            ('disp_on_s2', 0.33333333333333333, 1.0),
            id='default ttl - 10 min',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=600,
            ),
        ),
        pytest.param(
            200,
            # 1 call routed to disp_on_s1 is taken into account
            'disp_on_s2',
            ('disp_on_s2', 0.66666666666666666, 1.0),
            id='4 min ttl',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=240,
            ),
        ),
        pytest.param(
            200,
            # calls routed to disp_on_s1 are NOT taken into account
            'disp_on_s1',
            ('disp_on_s1', 1.0, 1.0),
            id='1 min ttl',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=60,
            ),
        ),
    ),
)
async def test_routed_call_ttl(
        taxi_callcenter_queues,
        testpoint,
        expected_code,
        expected_queue,
        pgsql,
        expected_routed_call,
        taxi_config,
):
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))
    priorities = dict()

    @testpoint('call-routing-prioritization')
    def prioritization(data):
        nonlocal priorities
        priorities[data['call_guid']] = {
            sub['name']: sub['priority'] for sub in data['subclusters']
        }

    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {'GUID': 'call_guid_10', 'CALLED_DN': '123'},
        ),
    )

    # Check answer
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['1']
        assert queue_action['ACTION'] == 'QUEUE'
        assert queue_action['VALUE'] == expected_queue

    # Check details
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute(
        'SET LOCAL TIME ZONE \'UTC\';'
        'SELECT call_guid, metaqueue, subcluster'
        ' FROM callcenter_queues.routed_calls'
        ' WHERE call_guid = \'call_guid_10\'',
    )
    # Join info from priorities testpoint
    assert prioritization.has_calls
    routed_call = cursor.fetchall()[0]
    call_guid = routed_call[0]
    routed_call = (
        routed_call[1] + '_on_' + routed_call[2],
        priorities[call_guid]['s1'] if 's1' in priorities[call_guid] else None,
        priorities[call_guid]['s2'] if 's2' in priorities[call_guid] else None,
    )
    cursor.close()

    assert routed_call == expected_routed_call


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_emergency.sql'])
@pytest.mark.parametrize(
    ['expected_code', 'metaqueue', 'expected_sub'],
    (
        pytest.param(
            200,
            'disp',
            's1',
            id='normal route to disp',
            marks=pytest.mark.config(CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES),
        ),
        pytest.param(
            200,
            'disp',
            'reserve',
            id='force emergency route to disp',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={
                    'mode': 'force_enabled',
                },
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['reserve', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            200,
            'disp',
            's1',
            id='normal route to disp',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'disabled'},
                CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
            ),
        ),
        pytest.param(
            200,
            'cargo',
            'reserve',
            id='no connected agents on cargo, has reserve subcluster',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'auto'},
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'cargo',
                        'number': '123',
                        'allowed_clusters': ['reserve', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            500,
            'cargo',
            None,
            id='no connected agents on cargo and no emergency subclusters',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'auto'},
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'cargo',
                        'number': '123',
                        'allowed_clusters': ['broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            500,
            'unknown',
            None,
            id='no connected agents on unknown and no emergency subclusters',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'auto'},
            ),
        ),
        pytest.param(
            500,
            'cargo',
            None,
            id='disabled emergency route to cargo',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'disabled'},
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'cargo',
                        'number': '123',
                        'allowed_clusters': ['broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            500,
            'disp',
            None,
            id='all subclusters disabled',
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['s1', 's2'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['s1', 's2'],
                        },
                    },
                ],
            ),
        ),
    ),
)
async def test_emergency(
        taxi_callcenter_queues,
        expected_code,
        metaqueue,
        expected_sub,
        pgsql,
        taxi_config,
):
    callcenter_metaqueues = taxi_config.get('CALLCENTER_METAQUEUES')
    if metaqueue != 'unknown':
        metaqueue_number = [
            i['number']
            for i in callcenter_metaqueues
            if i['name'] == metaqueue
        ][0]
    else:
        metaqueue_number = 'unknown_number'
    fill_db(pgsql, callcenter_metaqueues)
    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {'GUID': 'call_guid_1', 'CALLED_DN': metaqueue_number},
        ),
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['1']
        assert queue_action['ACTION'] == 'QUEUE'
        assert queue_action['VALUE'] == metaqueue + '_on_' + expected_sub


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.pgsql(
    'callcenter_queues', files=['insert_routed_call_for_metrics.sql'],
)
@pytest.mark.parametrize(
    [
        'expected_code',
        'metaqueue',
        'call_guid',
        'expected_sub',
        'expected_metrics',
    ],
    (
        pytest.param(
            200,
            'disp',
            'call_guid_1',
            's1',
            {
                'disp': {
                    's1': {'1min': {'normal': 1, 'emergency': 0, 'fast': 0}},
                },
            },
            id='successfully routed call',
            marks=pytest.mark.config(CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES),
        ),
        pytest.param(
            200,
            'disp',
            'call_guid_1',
            'reserve',
            {
                'disp': {
                    'reserve': {
                        '1min': {'normal': 0, 'emergency': 1, 'fast': 0},
                    },
                },
            },
            id='force emergency route to disp',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={
                    'mode': 'force_enabled',
                },
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['reserve', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            200,
            'cargo',
            'call_guid_1',
            'reserve',
            {
                'cargo': {
                    'reserve': {
                        '1min': {'normal': 0, 'emergency': 1, 'fast': 0},
                    },
                },
            },
            id='no connected agents on cargo, has reserve subcluster',
            marks=pytest.mark.config(
                CALLCENTER_QUEUES_ROUTING_EMERGENCY_MODE={'mode': 'auto'},
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'cargo',
                        'number': '456',
                        # 'reserve' x2 - это грязный хак, чтобы
                        # НЕ сработала статическая маршрутизация,
                        # покопались в базе и мы ушли в fallback
                        'allowed_clusters': [
                            'reserve',
                            'reserve',
                            'broken_cluster',
                        ],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
        pytest.param(
            200,
            'disp',
            'call_guid_2',
            's1',
            {
                'disp': {
                    's1': {'1min': {'normal': 0, 'emergency': 0, 'fast': 1}},
                },
            },
            id='fast sub getting',
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'allowed_clusters': ['s1', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': ['broken_cluster'],
                        },
                    },
                ],
            ),
        ),
    ),
)
async def test_metrics(
        taxi_callcenter_queues,
        testpoint,
        expected_code,
        metaqueue,
        call_guid,
        expected_sub,
        expected_metrics,
        pgsql,
        taxi_config,
):
    callcenter_metaqueues = taxi_config.get('CALLCENTER_METAQUEUES')
    metaqueue_number = [
        i['number'] for i in callcenter_metaqueues if i['name'] == metaqueue
    ][0]
    fill_db(pgsql, callcenter_metaqueues)
    metrics_before = {}
    metrics_after = {}

    @testpoint('call-balancing-started')
    def call_routing_started(data):
        nonlocal metrics_before
        metrics_before = data

    @testpoint('call-balancing-finished')
    def call_routing_finished(data):
        nonlocal metrics_after
        metrics_after = data

    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {'GUID': call_guid, 'CALLED_DN': metaqueue_number},
        ),
    )

    # get subtree by template
    def filter_tree(data, tmpl):
        if not isinstance(data, dict):
            return data

        res = dict()
        for x in data:
            if x in tmpl:
                res[x] = filter_tree(data[x], tmpl[x])
        return res

    # subtract one tree from another
    def subtract_tree(data1, data2):
        assert isinstance(data1, type(data2))
        if not isinstance(data1, dict):
            return data1 - data2

        res = dict()
        for x in data1:
            assert x in data2
            res[x] = subtract_tree(data1[x], data2[x])
        return res

    # Check answer
    assert response.status_code == expected_code
    if expected_code == 200:
        data = response.json()
        queue_action = data['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']['1']
        assert queue_action['ACTION'] == 'QUEUE'
        assert queue_action['VALUE'] == metaqueue + '_on_' + expected_sub

    # Check metrics
    assert call_routing_started.has_calls
    assert call_routing_finished.has_calls
    metrics_before = filter_tree(metrics_before, expected_metrics)
    metrics_after = filter_tree(metrics_after, expected_metrics)
    metrics = subtract_tree(metrics_after, metrics_before)
    assert metrics == expected_metrics


@pytest.mark.now('2020-05-01T10:00:00.00Z')
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp',
            'number': '123',
            'allowed_clusters': ['s1', 's2', 'broken_cluster'],
            'disabled_clusters': {'disabled_for_routing': ['broken_cluster']},
        },
    ],
    CALLCENTER_QUEUES_BALANCE_ROUTED_CALL_TTL=600,
)
@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.pgsql('callcenter_queues', files=['insert_lost_routed_calls.sql'])
@pytest.mark.parametrize(
    ['events_data', 'call_history', 'expected_routed_calls'],
    (
        pytest.param(
            None,
            'for_lost_routed_calls.json',
            [
                ('call_guid_4', '+79990007701', 'disp_on_s2', 0.0, 1.0),
                ('call_guid_5', '+79990007701', 'disp_on_s2', 0.0, 0.5),
                ('call_guid_6', '+79990007701', 'disp_on_s1', 0.0, 0.0),
            ],
            # Три lost routed изначально в таблице
            # (приоритет первого саба должен быть 0)
            id='3 lost routed calls on s1',
        ),
        pytest.param(
            'meta.txt',
            'for_lost_routed_calls.json',
            [
                ('call_guid_4', '+79990007701', 'disp_on_s1', 1.0, 1.0),
                (
                    'call_guid_5',
                    '+79990007701',
                    'disp_on_s2',
                    0.6666666666666666,
                    1.0,
                ),
                (
                    'call_guid_6',
                    '+79990007701',
                    'disp_on_s1',
                    0.6666666666666666,
                    0.5,
                ),
            ],
            # Вначале отсылаем 3 МЕТА, чтобы заполнить call_id
            # в таблице -> должно быть 0 lost routed calls
            id='no lost routed calls',
        ),
    ),
)
async def test_lost_routed_engagement(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        events_data,
        call_history,
        expected_routed_calls,
        mock_personal,
        lb_message_sender,
        taxi_config,
):
    if events_data:
        await lb_message_sender.send(events_data)
    await _test_static(
        taxi_callcenter_queues,
        testpoint,
        load_json,
        pgsql,
        set_now,
        call_history,
        expected_routed_calls,
        lb_message_sender,
        taxi_config,
    )


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_METAQUEUES=DEFAULT_METAQUEUES,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.experiments3(filename='exp3_balancing_extraactions.json')
async def test_extraactions_config(
        taxi_callcenter_queues, pgsql, taxi_config, experiments3,
):
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))
    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'CALLED_DN': '123',
                'CALLERID': '+1234',
                'ORIGINAL_DN': 'original_dn',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '1': {
            'ACTION': 'QUEUE',
            'PARAMS': {
                'ENDPOINT': 'QPROC-s1',
                'ENDPOINTCOUNT': 2,
                'ENDPOINTSTATEGY': 'TOPDOWN',
                'ENDPOINTSTATEGYOPT': 1,
                'TIMEOUT': 300,
            },
            'VALUE': 'disp_on_s1',
        },
        '2': {
            'ACTION': 'DIAL',
            'PARAMS': {'ROUTE': 'GLOBAL_ROUTING', 'TIMEOUT': 300},
            'VALUE': 'GLOBAL/98400',
        },
    }
    assert {'1': data['1'], '2': data['2']} == expected_action


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300},
)
@pytest.mark.parametrize(
    ['expected_route'],
    (
        pytest.param(
            'test_project',
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'queue_project_key': 'test_project',
                        'allowed_clusters': ['s1', 's2', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': [
                                'broken_cluster',
                                'unknown_cluster',
                            ],
                        },
                        'tags': [],
                    },
                ],
            ),
            id='without route',
        ),
        pytest.param(
            'test_route',
            marks=pytest.mark.config(
                CALLCENTER_METAQUEUES=[
                    {
                        'name': 'disp',
                        'number': '123',
                        'queue_project_key': 'test_project',
                        'queue_route': 'test_route',
                        'allowed_clusters': ['s1', 's2', 'broken_cluster'],
                        'disabled_clusters': {
                            'disabled_for_routing': [
                                'broken_cluster',
                                'unknown_cluster',
                            ],
                        },
                        'tags': [],
                    },
                ],
            ),
            id='with route',
        ),
    ),
)
async def test_project_key_config(
        taxi_callcenter_queues, expected_route, pgsql, taxi_config,
):
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))
    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'CALLED_DN': '123',
                'CALLERID': '+1234',
                'ORIGINAL_DN': 'original_dn',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '0': {
            'ACTION': 'SET',
            'PARAM': 'COMMUTATION_ID',
            'PARAMTYPE': 'HEADER',
            'VALUE': '1641fa924bc3ab9a173c33192a770fa701db3307',
        },
        '1': {
            'ACTION': 'SET',
            'PARAM': 'PROJECTKEY',
            'PARAMTYPE': 'HEADER',
            'VALUE': 'test_project',
        },
        '2': {
            'ACTION': 'SET',
            'PARAM': 'Route',
            'PARAMTYPE': 'HEADER',
            'VALUE': expected_route,
        },
        '3': {
            'ACTION': 'QUEUE',
            'PARAMS': {
                'ENDPOINT': 'QPROC-s1',
                'ENDPOINTCOUNT': 2,
                'ENDPOINTSTATEGY': 'TOPDOWN',
                'ENDPOINTSTATEGYOPT': 1,
                'TIMEOUT': 300,
            },
            'VALUE': 'disp_on_s1',
        },
    }
    assert data == expected_action


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents_3_2.sql'])
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP=SUBCLUSTERS,
    CALLCENTER_QUEUES_BALANCING_TIMEOUTS={'__default__': 300, 'disp': 100},
    CALLCENTER_METAQUEUES=[
        {
            'name': 'disp',
            'number': '123',
            'queue_project_key': 'test_project',
            'allowed_clusters': ['s1', 's2', 'broken_cluster'],
            'disabled_clusters': {
                'disabled_for_routing': ['broken_cluster', 'unknown_cluster'],
            },
            'tags': [],
        },
    ],
)
async def test_timeout_config(taxi_callcenter_queues, pgsql, taxi_config):
    fill_db(pgsql, taxi_config.get('CALLCENTER_METAQUEUES'))
    response = await taxi_callcenter_queues.post(
        ENDPOINT,
        headers=HEADERS,
        data=urllib.parse.urlencode(
            {
                'GUID': 'call_guid',
                'CALLED_DN': '123',
                'CALLERID': '+1234',
                'ORIGINAL_DN': 'original_dn',
            },
        ),
    )
    assert response.status_code == 200
    data = response.json()['CONTENT']['EXAMPLE_ACTION']['ACTIONVALUE']
    expected_action = {
        '0': {
            'ACTION': 'SET',
            'PARAM': 'COMMUTATION_ID',
            'PARAMTYPE': 'HEADER',
            'VALUE': '1641fa924bc3ab9a173c33192a770fa701db3307',
        },
        '1': {
            'ACTION': 'SET',
            'PARAM': 'PROJECTKEY',
            'PARAMTYPE': 'HEADER',
            'VALUE': 'test_project',
        },
        '2': {
            'ACTION': 'SET',
            'PARAM': 'Route',
            'PARAMTYPE': 'HEADER',
            'VALUE': 'test_project',
        },
        '3': {
            'ACTION': 'QUEUE',
            'PARAMS': {
                'ENDPOINT': 'QPROC-s1',
                'ENDPOINTCOUNT': 2,
                'ENDPOINTSTATEGY': 'TOPDOWN',
                'ENDPOINTSTATEGYOPT': 1,
                'TIMEOUT': 100,  # !!!
            },
            'VALUE': 'disp_on_s1',
        },
    }
    assert data == expected_action
