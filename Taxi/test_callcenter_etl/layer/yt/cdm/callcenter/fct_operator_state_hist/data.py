_commutation = dict
_status = dict

STATUS_LOG = [
    # Today
    _status(
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:00:00.090",
        operator_status_log_id="kekeke00",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        # Постколл чуть позже окончания звонка
        # (1-2) talking должен закончиться в момент начала postcall
        #       считаем, что проблема в том, что коммутации до сенкуд
        #       (иногда немного расширяется talking)
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:00:48.300",
        operator_status_log_id="kekeke01",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code="postcall",
        asterisk_login="wowan",
    ),
    _status(
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:00:50.090",
        operator_status_log_id="kekeke02",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        # Постколл чуть раньше окончания звонка
        # (4-5) postcall должен начаться чуть позже (в момент окончания звонка)
        #       считаем, что проблема в рассинхроне между объектами
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:01:42.300",
        operator_status_log_id="kekeke03",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code="postcall",
        asterisk_login="wowan",
    ),
    _status(
        # Звонок без явного postcall
        # (7-10) коммутации после этого connected не должны пропасть
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:01:43.890",
        operator_status_log_id="kekeke04",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        # Разъединение во время звонка (до его окончания)
        # (11-12) звонок должен обрубиться по disconnected
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:04:10.900",
        operator_status_log_id="kekeke05",
        queue_code_list=["q1", "q2"],
        work_status_code="disconnected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        # Пересекающиеся звонки после возвращения в connected
        # (11-14) не должно получиться пересечения в статусах
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:04:11.000",
        operator_status_log_id="kekeke06",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        # Ушел в паузу на разговоре
        # (14-15) Пауза должна начаться после окончания звонка
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:05:00.000",
        operator_status_log_id="kekeke07",
        queue_code_list=["q1", "q2"],
        work_status_code="paused",
        work_substatus_code="smoke",
        asterisk_login="wowan",
    ),
    _status(
        # Вышел из паузы после начала звонка (рассихрон)
        # (15-17) Пауза должна закончиться до начала разговора
        #         этот connected  не должен пропасть
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:20:00.092",
        operator_status_log_id="kekeke08",
        queue_code_list=["q1", "q2"],
        work_status_code="connected",
        work_substatus_code=None,
        asterisk_login="wowan",
    ),
    _status(
        agent_id=100500,
        utc_created_dttm="2020-06-28 09:30:00.093",
        operator_status_log_id="kekeke09",
        queue_code_list=["q1", "q2"],
        work_status_code="disconnected",
        work_substatus_code="",
        asterisk_login="wowan",
    )
]

COMMUTATIONS = [
    _commutation(
        # Постколл чуть позже окончания звонка
        utc_answered_dttm="2020-06-28 09:00:03",
        utc_completed_dttm="2020-06-28 09:00:48",
        commutation_id="ashh01",
        call_id="call01",
        phone_pd_id="hash01",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Постколл чуть раньше окончания звонка
        utc_answered_dttm="2020-06-28 09:00:52",
        utc_completed_dttm="2020-06-28 09:01:43",
        commutation_id="ashh02",
        call_id="call02",
        phone_pd_id="hash02",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Нет postcall после звонка
        utc_answered_dttm="2020-06-28 09:01:50",
        utc_completed_dttm="2020-06-28 09:02:49",
        commutation_id="ashh03",
        call_id="call03",
        phone_pd_id="hash03",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Проверяем, что до/после звонка нет дырок
        utc_answered_dttm="2020-06-28 09:02:52",
        utc_completed_dttm="2020-06-28 09:03:35",
        commutation_id="ashh04",
        call_id="call04",
        phone_pd_id="hash04",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Разъединение во время звонка (до его окончания)
        utc_answered_dttm="2020-06-28 09:03:36",
        utc_completed_dttm="2020-06-28 09:04:15",
        commutation_id="ashh05",
        call_id="call05",
        phone_pd_id="hash05",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code="support",
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Пересекается с предыдущим звонком
        # Уход в паузу до завершения звонка
        utc_answered_dttm="2020-06-28 09:04:12",
        utc_completed_dttm="2020-06-28 09:05:12",
        commutation_id="ashh06",
        call_id="call06",
        phone_pd_id="hash06",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Вышел из паузы после начала звонка (рассихрон)
        utc_answered_dttm="2020-06-28 09:20:00",
        utc_completed_dttm="2020-06-28 09:21:00",
        commutation_id="ashh07",
        call_id="call07",
        phone_pd_id="hash07",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
    _commutation(
        # Звонок после завершения рассинхрона
        utc_answered_dttm="2020-06-28 09:22:01",
        utc_completed_dttm="2020-06-28 09:22:31",
        commutation_id="ashh08",
        call_id="call08",
        phone_pd_id="hash08",
        commutation_queue_code="q1",
        callcenter_phone_number="+74959999999",
        agent_id=100500,
        transfer_destination_code=None,
        commutation_end_reason_type="completed_by_agent",
    ),
]

EXPECTED = [
    {
        # 0
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:00:00.090',
        'utc_valid_to_dttm': '2020-06-28 09:00:03.000',
        'state_dur_sec': 2.91,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke00',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 1
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:00:03.000',
        'utc_valid_to_dttm': '2020-06-28 09:00:48.300',
        'state_dur_sec': 45.3,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh01',
        'call_id': 'call01',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash01',
        'transfer_destination_code': None
    }, {
        # 2
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:00:48.300',
        'utc_valid_to_dttm': '2020-06-28 09:00:50.090',
        'state_dur_sec': 1.79,
        'operator_state_code': 'postcall',
        'work_status_code': 'connected',
        'work_substatus_code': 'postcall',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke01',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 3
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:00:50.090',
        'utc_valid_to_dttm': '2020-06-28 09:00:52.000',
        'state_dur_sec': 1.91,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke02',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 4
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:00:52.000',
        'utc_valid_to_dttm': '2020-06-28 09:01:43.000',
        'state_dur_sec': 51,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh02',
        'call_id': 'call02',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash02',
        'transfer_destination_code': None
    }, {
        # 5
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:01:43.000',
        'utc_valid_to_dttm': '2020-06-28 09:01:43.890',
        'state_dur_sec': 0.89,
        'operator_state_code': 'postcall',
        'work_status_code': 'connected',
        'work_substatus_code': 'postcall',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke03',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 6
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:01:43.890',
        'utc_valid_to_dttm': '2020-06-28 09:01:50.000',
        'state_dur_sec': 6.11,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke04',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 7
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:01:50.000',
        'utc_valid_to_dttm': '2020-06-28 09:02:49.000',
        'state_dur_sec': 59,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh03',
        'call_id': 'call03',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash03',
        'transfer_destination_code': None
    }, {
        # 8
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:02:49.000',
        'utc_valid_to_dttm': '2020-06-28 09:02:52.000',
        'state_dur_sec': 3,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_finished',
        'event_id': 'ashh03',
        'call_id': 'call03',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash03',
        'transfer_destination_code': None
    }, {
        # 9
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:02:52.000',
        'utc_valid_to_dttm': '2020-06-28 09:03:35.000',
        'state_dur_sec': 43,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh04',
        'call_id': 'call04',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash04',
        'transfer_destination_code': None
    }, {
        # 10
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:03:35.000',
        'utc_valid_to_dttm': '2020-06-28 09:03:36.000',
        'state_dur_sec': 1,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_finished',
        'event_id': 'ashh04',
        'call_id': 'call04',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash04',
        'transfer_destination_code': None
    }, {
        # 11
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:03:36.000',
        'utc_valid_to_dttm': '2020-06-28 09:04:10.900',
        'state_dur_sec': 34.9,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh05',
        'call_id': 'call05',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash05',
        'transfer_destination_code': 'support'
    }, {
        # 12
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:04:10.900',
        'utc_valid_to_dttm': '2020-06-28 09:04:11.000',
        'state_dur_sec': 0.1,
        'operator_state_code': 'disconnected',
        'work_status_code': 'disconnected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke05',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 13
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:04:11.000',
        'utc_valid_to_dttm': '2020-06-28 09:04:12.000',
        'state_dur_sec': 1,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke06',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 14
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:04:12.000',
        'utc_valid_to_dttm': '2020-06-28 09:05:12.000',
        'state_dur_sec': 60,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh06',
        'call_id': 'call06',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash06',
        'transfer_destination_code': None
    }, {
        # 15
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:05:12.000',
        'utc_valid_to_dttm': '2020-06-28 09:20:00.000',
        'state_dur_sec': 888,
        'operator_state_code': 'paused',
        'work_status_code': 'paused',
        'work_substatus_code': 'smoke',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke07',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 16
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:20:00.000',
        'utc_valid_to_dttm': '2020-06-28 09:21:00.000',
        'state_dur_sec': 60,
        'operator_state_code': 'talking',
        'work_status_code': 'paused',
        'work_substatus_code': 'smoke',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh07',
        'call_id': 'call07',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash07',
        'transfer_destination_code': None
    }, {
        # 17
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:21:00.000',
        'utc_valid_to_dttm': '2020-06-28 09:22:01.000',
        'state_dur_sec': 61,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': None,
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'operator_status_log',
        'event_id': 'kekeke08',
        'call_id': None,
        'staff_login': 'wowan',
        'callcenter_phone_number': None,
        'phone_pd_id': None,
        'transfer_destination_code': None
    }, {
        # 18
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:22:01.000',
        'utc_valid_to_dttm': '2020-06-28 09:22:31.000',
        'state_dur_sec': 30,
        'operator_state_code': 'talking',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_started',
        'event_id': 'ashh08',
        'call_id': 'call08',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash08',
        'transfer_destination_code': None
    }, {
        # 19
        'agent_id': 100500,
        'utc_valid_from_dttm': '2020-06-28 09:22:31.000',
        'utc_valid_to_dttm': '2020-06-28 09:30:00.093',
        'state_dur_sec': 449.093,
        'operator_state_code': 'waiting',
        'work_status_code': 'connected',
        'work_substatus_code': '',
        'queue_code': 'q1',
        'queues_enabled_list': ['q1', 'q2'],
        'event_type': 'commutation_finished',
        'event_id': 'ashh08',
        'call_id': 'call08',
        'staff_login': 'wowan',
        'callcenter_phone_number': '+74959999999',
        'phone_pd_id': 'hash08',
        'transfer_destination_code': None
    },
]
