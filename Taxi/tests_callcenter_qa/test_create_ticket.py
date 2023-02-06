import pytest

SAVE_FEEDBACK_URL = '/cc/v1/callcenter-qa/v1/feedback/save'
CALLCENTER_QA_CUSTOM_FIELDS = {
    'linkToAdminPanel': {'key': 'linkToAdminPanel', 'enabled': True},
    'loginOperator': {'key': 'loginOperator', 'enabled': True},
    'operatorName': {'key': 'operatorName', 'enabled': True},
    'agentId': {'key': 'agentId', 'enabled': True},
    'callGuid': {'key': 'callGuid', 'enabled': True},
    'callId': {'key': 'callId', 'enabled': True},
    'callcenterId': {'key': 'callcenterId', 'enabled': True},
    'callcenterProject': {'key': 'callcenterProject', 'enabled': True},
    'commutationId': {'key': 'commutationId', 'enabled': True},
    'yandexUid': {'key': 'yandexUid', 'enabled': True},
    'callcenterPhone': {'key': 'callcenterPhone', 'enabled': True},
    'ccQueue': {'key': 'ccQueue', 'enabled': True},
    'cityCC': {'key': 'cityCC', 'enabled': True},
    'linkToVmon': {'key': 'linkToVmon', 'enabled': True},
    'metaqueue': {'key': 'metaqueue', 'enabled': True},
    'userPhone': {'key': 'userPhone', 'enabled': True},
    'loginTelegram': {'key': 'loginTelegram', 'enabled': True},
    'incidentTime': {'key': 'incidentTime', 'enabled': True},
    'codeErrorCC': {'key': 'codeErrorCC', 'enabled': True},
    'errorPath': {'key': 'errorPath', 'enabled': True},
}


@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
        'incident_test_2': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {'queue': 'CCINCIDENT', 'tags': 'bad_tag'},
                },
            ],
        },
        'incident_test_3': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status'],
    (
        pytest.param('request_1.json', 200, id='successful_creation'),
        pytest.param(
            'request_2.json', 200, id='bad_tag_format_and_no_summary',
        ),
        pytest.param('request_3.json', 500, id='no_queue_in_cfg'),
    ),
)
async def test_create_ticket(
        taxi_callcenter_qa,
        mock_tracker,
        request_body,
        expected_status,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == expected_status


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
        'incident_test_2': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'city_test',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_QA_TRACKER_LINKS_SETTINGS={
        'settings': {
            'vmon_settings': {
                'use_new_template': False,
                'template_new': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcustom_header_1_1%22:'
                    '%22{call_guid}%22{end_bracket}'
                ),
                'template_old': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcaller%22:%22%2B{caller}%22,%22fcalled%22:%22%'
                    '2B{called}%22,%22fcallerd_type%22:1{end_bracket}'
                ),
                'duration': 5 * 60,
            },
            'admin_template': (
                'https://phoneorderbeta.taxi.yandex.ru/admin/calls/{}'
            ),
        },
    },
    CALLCENTER_QA_CUSTOM_FIELDS=CALLCENTER_QA_CUSTOM_FIELDS,
)
@pytest.mark.parametrize(
    [
        'request_body',
        'request_yandex_uid',
        'expected_status',
        'expected_ticket_body',
    ],
    (
        pytest.param(
            'request_1.json',
            'yandex_uid_test_1',
            200,
            {
                'summary': 'no sound: operator_1 call_guid_1',
                'queue': 'CCINCIDENT',
                'description': (
                    '**Feedback type:** incident_test_1\n'
                    '**Created at:** 2021-12-31T11:00:00+0000\n'
                    '**Project:** test_project\n\n'
                    '**Yandex uid:** yandex_uid_test_1\n'
                    '**Login:** operator_1\n'
                    '**Agent id:** 111\n'
                    '**Callcenter id:** volgograd_cc\n'
                    '**Telegram login:** telegram_operator_1\n'
                    '**Operator\'s name:** name surname\n\n'
                    '**Call_id:** call_id_1\n'
                    '**Commutation_id:** commutation_test\n'
                    '**Call_guid:** call_guid_1\n'
                    '**Callcenter phone:** +79999999999\n'
                    '**User phone:** +71234567890\n'
                    '**Metaqueue:** disp\n**Queue:** disp_on_1\n'
                    '**City:** city_test\n\n'
                    '**Link to admin:** https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test\n'
                    '**Link to vmon:** '
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,'
                    '%22fdateto%22:%222021-12-31T11:05:00%22,%22fcaller'
                    '%22:%22%2B71234567890%22,%22fcalled%22:%22%2B'
                    '79999999999%22,%22fcallerd_type%22:1}\n\n'
                    '**Operator\'s comment:** test_comment\n\n'
                    '<{**Extra**\n{"application":"call_center"}\n}>\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'tags': ['tag1', 'tag2'],
                'linkToAdminPanel': (
                    'https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test'
                ),
                'loginOperator': 'operator_1',
                'operatorName': 'name surname',
                'agentId': '111',
                'callGuid': 'call_guid_1',
                'callId': 'call_id_1',
                'callcenterId': 'volgograd_cc',
                'callcenterProject': 'test_project',
                'commutationId': 'commutation_test',
                'yandexUid': 'yandex_uid_test_1',
                'callcenterPhone': '+79999999999',
                'ccQueue': 'disp_on_1',
                'cityCC': 'city_test',
                'linkToVmon': (
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,%22fdateto'
                    '%22:%222021-12-31T11:05:00%22,%22fcaller%22:'
                    '%22%2B71234567890%22,%22fcalled%22:'
                    '%22%2B79999999999%22,%22fcallerd_type%22:1}'
                ),
                'metaqueue': 'disp',
                'userPhone': '+71234567890',
                'loginTelegram': 'telegram_operator_1',
                'incidentTime': '2021-12-31T11:00:00+0000',
            },
            id='full_creation',
        ),
        pytest.param(
            'request_4.json',
            'bad_yandex_uid',
            200,
            {
                'summary': 'no sound',
                'queue': 'CCINCIDENT',
                'description': (
                    '**Feedback type:** incident_test_1\n'
                    '**Created at:** 2021-12-31T11:00:00+0000\n\n'
                    '**Yandex uid:** bad_yandex_uid\n\n\n\n'
                    '<{**Extra**\n{"some_log":"log"}\n}>\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'tags': ['tag1', 'tag2'],
                'yandexUid': 'bad_yandex_uid',
                'incidentTime': '2021-12-31T11:00:00+0000',
            },
            id='no_yandex_uid_in_cache',
        ),
        pytest.param(
            'request_5.json',
            'bad_yandex_uid',
            200,
            {
                'summary': 'incident_test_2',
                'queue': 'CCINCIDENT',
                'description': (
                    '**Feedback type:** incident_test_2\n'
                    '**Created at:** 2021-12-31T11:00:00+0000\n'
                    '**User Agent:** user_agent\n'
                    '**Error code:** 500\n'
                    '**Error path:** test_url\n\n'
                    '**Yandex uid:** bad_yandex_uid\n\n\n\n'
                    '<{**Extra**\n{"lastRequests":[{"data":{"status":500,'
                    '"url":"test_url"}}],"userAgent":"user_agent"}\n}>\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'tags': ['tag1', 'tag2'],
                'yandexUid': 'bad_yandex_uid',
                'codeErrorCC': '500',
                'errorPath': 'test_url',
                'incidentTime': '2021-12-31T11:00:00+0000',
            },
            id='no_summary_and_fill_extra',
        ),
    ),
)
async def test_save_ticket_in_tracker(
        taxi_callcenter_qa,
        request_body,
        request_yandex_uid,
        expected_status,
        expected_ticket_body,
        mock_tracker,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': request_yandex_uid},
    )
    assert response.status_code == expected_status

    assert mock_tracker.create_issue.times_called == 1
    assert (
        mock_tracker.create_issue.next_call()['request'].json
        == expected_ticket_body
    )


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
        'incident_test_2': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'city_test',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_QA_TRACKER_LINKS_SETTINGS={
        'settings': {
            'vmon_settings': {
                'use_new_template': False,
                'template_new': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcustom_header_1_1%22:'
                    '%22{call_guid}%22{end_bracket}'
                ),
                'template_old': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcaller%22:%22%2B{caller}%22,%22fcalled%22:%22%'
                    '2B{called}%22,%22fcallerd_type%22:1{end_bracket}'
                ),
                'duration': 5 * 60,
            },
            'admin_template': (
                'https://phoneorderbeta.taxi.yandex.ru/admin/calls/{}'
            ),
        },
    },
    CALLCENTER_QA_CUSTOM_FIELDS=CALLCENTER_QA_CUSTOM_FIELDS,
)
@pytest.mark.parametrize(
    [
        'request_body',
        'request_yandex_uid',
        'expected_status',
        'expected_db_ticket',
        'expected_db_feedback',
    ],
    (
        pytest.param(
            'request_1.json',
            'yandex_uid_test_1',
            200,
            ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
            {
                'call_info': {
                    'city': 'city_test',
                    'fcalled': '+79999999999',
                    'metaqueue': 'disp',
                    'queue': 'disp_on_1',
                    'personal_phone_id': 'phone_pd_id',
                    'application': 'test_call_center',
                },
                'feedback_info': {'project': 'test_project'},
                'operator_info': {'callcenter': 'volgograd_cc'},
            },
            id='full_creation',
        ),
        pytest.param(
            'request_4.json',
            'bad_yandex_uid',
            200,
            ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
            None,
            id='no_yandex_uid_in_cache',
        ),
        pytest.param(
            'request_5.json',
            'bad_yandex_uid',
            200,
            ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
            {'feedback_info': {'error_code': '500', 'error_path': 'test_url'}},
            id='no_summary_and_fill_extra',
        ),
    ),
)
async def test_save_ticket_in_db(
        taxi_callcenter_qa,
        request_body,
        request_yandex_uid,
        expected_status,
        expected_db_ticket,
        expected_db_feedback,
        mock_tracker,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': request_yandex_uid},
    )
    assert response.status_code == expected_status

    assert mock_tracker.create_issue.times_called == 1

    cursor_tickets = pgsql['callcenter_qa'].cursor()
    cursor_tickets.execute(
        'SELECT ticket_name, ticket_uri, feedback_id, status'
        ' FROM callcenter_qa.tickets',
    )
    assert cursor_tickets.fetchall()[0] == expected_db_ticket
    cursor_tickets.close()

    cursor_feedbacks = pgsql['callcenter_qa'].cursor()
    cursor_feedbacks.execute(
        'SELECT external_info' ' FROM callcenter_qa.feedbacks',
    )
    assert cursor_feedbacks.fetchall()[0][0] == expected_db_feedback
    cursor_feedbacks.close()


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
                {
                    'index': 1,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT_2',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
)
@pytest.mark.parametrize(
    ['request_body', 'expected_status', 'expected_db_ticket'],
    (
        pytest.param(
            'request_1.json',
            200,
            [
                ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
                ('CCINCIDENT_2', 'https://example.ru', 'id1', 'created'),
            ],
            id='two_processors',
        ),
    ),
)
async def test_two_processors(
        taxi_callcenter_qa,
        request_body,
        expected_status,
        expected_db_ticket,
        mock_tracker,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == expected_status

    assert mock_tracker.create_issue.times_called == 2

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT ticket_name, ticket_uri, feedback_id, status'
        ' FROM callcenter_qa.tickets',
    )
    assert cursor.fetchall() == expected_db_ticket
    cursor.close()


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
)
async def test_tracker_fail(
        taxi_callcenter_qa,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/startrek/v2/issues', prefix=True)
    async def _create_issue(request):
        return mockserver.make_response(
            status=403,
            json={
                'statusCode': 'bad_access',
                'errorMessages': ['no tvm rule'],
            },
        )

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    request = load_json('request_1.json')
    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json('request_1.json'),
        headers={'X-Yandex-UID': 'test_uid'},
    )
    assert response.status_code == 500
    assert response.json() == {
        'code': 'processor_error',
        'message': (
            f'Can\'t process tracker_incident_saver with '
            f'feedback_id: {request["feedback_id"]}'
        ),
    }

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT ticket_name, ticket_uri, feedback_id, status'
        ' FROM callcenter_qa.tickets',
    )
    assert cursor.fetchall() == []


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'city_test',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_QA_TRACKER_LINKS_SETTINGS={
        'settings': {
            'vmon_settings': {
                'use_new_template': True,
                'template_new': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom'
                    '%22:%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcustom_header_1_1%22:'
                    '%22{call_guid}%22{end_bracket}'
                ),
                'template_old': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcaller%22:%22%2B{caller}%22,%22fcalled%22:%22%'
                    '2B{called}%22,%22fcallerd_type%22:1{end_bracket}'
                ),
                'duration': 5 * 60,
            },
            'admin_template': (
                'https://phoneorderbeta.taxi.yandex.ru/admin/calls/{}'
            ),
        },
    },
    CALLCENTER_QA_CUSTOM_FIELDS=CALLCENTER_QA_CUSTOM_FIELDS,
)
@pytest.mark.parametrize(
    [
        'request_body',
        'request_yandex_uid',
        'expected_status',
        'expected_ticket_body',
        'expected_db_ticket',
    ],
    (
        pytest.param(
            'request_1.json',
            'yandex_uid_test_1',
            200,
            {
                'summary': 'no sound: operator_1 call_guid_1',
                'queue': 'CCINCIDENT',
                'description': (
                    '**Feedback type:** incident_test_1\n'
                    '**Created at:** 2021-12-31T11:00:00+0000\n'
                    '**Project:** test_project\n\n'
                    '**Yandex uid:** yandex_uid_test_1\n'
                    '**Login:** operator_1\n'
                    '**Agent id:** 111\n'
                    '**Callcenter id:** volgograd_cc\n'
                    '**Telegram login:** telegram_operator_1\n'
                    '**Operator\'s name:** name surname\n\n'
                    '**Call_id:** call_id_1\n'
                    '**Commutation_id:** commutation_test\n'
                    '**Call_guid:** call_guid_1\n'
                    '**Callcenter phone:** +79999999999\n'
                    '**Metaqueue:** disp\n**Queue:** disp_on_1\n'
                    '**City:** city_test\n\n'
                    '**Link to admin:** https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test\n'
                    '**Link to vmon:** '
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,%22fdateto'
                    '%22:%222021-12-31T11:05:00%22,'
                    '%22fcustom_header_1_1%22:%22call_guid_1%22}\n\n'
                    '**Operator\'s comment:** test_comment\n\n'
                    '<{**Extra**\n{"application":"call_center"}\n}>\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'tags': ['tag1', 'tag2'],
                'linkToAdminPanel': (
                    'https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test'
                ),
                'linkToVmon': (
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,%22fdateto'
                    '%22:%222021-12-31T11:05:00%22,'
                    '%22fcustom_header_1_1%22:%22call_guid_1%22}'
                ),
                'loginOperator': 'operator_1',
                'operatorName': 'name surname',
                'yandexUid': 'yandex_uid_test_1',
                'agentId': '111',
                'callGuid': 'call_guid_1',
                'callId': 'call_id_1',
                'callcenterId': 'volgograd_cc',
                'callcenterProject': 'test_project',
                'commutationId': 'commutation_test',
                'metaqueue': 'disp',
                'callcenterPhone': '+79999999999',
                'ccQueue': 'disp_on_1',
                'cityCC': 'city_test',
                'loginTelegram': 'telegram_operator_1',
                'incidentTime': '2021-12-31T11:00:00+0000',
            },
            ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
        ),
    ),
)
async def test_personal_fail(
        taxi_callcenter_qa,
        request_body,
        request_yandex_uid,
        expected_status,
        expected_ticket_body,
        expected_db_ticket,
        mock_tracker,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return mockserver.make_response('', status=500)

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return {
            'personal_phone_id': 'phone_pd_id',
            'called_number': '+79999999999',
            'metaqueue': 'disp',
            'subcluster': '1',
        }

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': request_yandex_uid},
    )
    assert response.status_code == expected_status

    assert mock_tracker.create_attachment.times_called == 2
    assert mock_tracker.create_issue.times_called == 1
    assert (
        mock_tracker.create_issue.next_call()['request'].json
        == expected_ticket_body
    )

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT ticket_name, ticket_uri, feedback_id, status'
        ' FROM callcenter_qa.tickets',
    )
    assert cursor.fetchall()[0] == expected_db_ticket
    cursor.close()


@pytest.mark.now('2021-12-31T11:00:00+0000')
@pytest.mark.config(
    CALLCENTER_QA_FEEDBACK_SETTINGS={
        'incident_test_1': {
            'synchronized_processors': [
                {
                    'index': 0,
                    'name': 'tracker_incident_saver',
                    'settings': {
                        'queue': 'CCINCIDENT',
                        'summary': 'no sound',
                        'tags': ['tag1', 'tag2'],
                    },
                },
            ],
        },
    },
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '__default__': {
            'application': 'test_call_center',
            'city_name': 'city_test',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
    CALLCENTER_QA_TRACKER_LINKS_SETTINGS={
        'settings': {
            'vmon_settings': {
                'use_new_template': True,
                'template_new': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom'
                    '%22:%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcustom_header_1_1%22:'
                    '%22{call_guid}%22{end_bracket}'
                ),
                'template_old': (
                    'https://vmon.tel.yandex.net/'
                    'admin.php?cdr_filter={start_bracket}%22fdatefrom%22:'
                    '%22{date_from}%22,%22fdateto%22:%22{date_to}%22,'
                    '%22fcaller%22:%22%2B{caller}%22,%22fcalled%22:%22%'
                    '2B{called}%22,%22fcallerd_type%22:1{end_bracket}'
                ),
                'duration': 5 * 60,
            },
            'admin_template': (
                'https://phoneorderbeta.taxi.yandex.ru/admin/calls/{}'
            ),
        },
    },
    CALLCENTER_QA_CUSTOM_FIELDS=CALLCENTER_QA_CUSTOM_FIELDS,
)
@pytest.mark.parametrize(
    [
        'request_body',
        'request_yandex_uid',
        'expected_status',
        'expected_ticket_body',
        'expected_db_ticket',
    ],
    (
        pytest.param(
            'request_1.json',
            'yandex_uid_test_1',
            200,
            {
                'summary': 'no sound: operator_1 call_guid_1',
                'queue': 'CCINCIDENT',
                'description': (
                    '**Feedback type:** incident_test_1\n'
                    '**Created at:** 2021-12-31T11:00:00+0000\n'
                    '**Project:** test_project\n\n'
                    '**Yandex uid:** yandex_uid_test_1\n'
                    '**Login:** operator_1\n'
                    '**Agent id:** 111\n'
                    '**Callcenter id:** volgograd_cc\n'
                    '**Telegram login:** telegram_operator_1\n'
                    '**Operator\'s name:** name surname\n\n'
                    '**Call_id:** call_id_1\n'
                    '**Commutation_id:** commutation_test\n'
                    '**Call_guid:** call_guid_1\n\n'
                    '**Link to admin:** https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test\n'
                    '**Link to vmon:** '
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,%22fdateto'
                    '%22:%222021-12-31T11:05:00%22,'
                    '%22fcustom_header_1_1%22:%22call_guid_1%22}\n\n'
                    '**Operator\'s comment:** test_comment\n\n'
                    '<{**Extra**\n{"application":"call_center"}\n}>\n'
                ),
                'descriptionRenderType': 'PLAIN',
                'tags': ['tag1', 'tag2'],
                'agentId': '111',
                'callGuid': 'call_guid_1',
                'callId': 'call_id_1',
                'callcenterId': 'volgograd_cc',
                'callcenterProject': 'test_project',
                'commutationId': 'commutation_test',
                'yandexUid': 'yandex_uid_test_1',
                'linkToAdminPanel': (
                    'https://phoneorderbeta.taxi.yandex.ru/'
                    'admin/calls/commutation_test'
                ),
                'linkToVmon': (
                    'https://vmon.tel.yandex.net/admin.php?cdr_filter='
                    '{%22fdatefrom%22:%222021-12-31T10:55:00%22,%22fdateto'
                    '%22:%222021-12-31T11:05:00%22,'
                    '%22fcustom_header_1_1%22:%22call_guid_1%22}'
                ),
                'loginOperator': 'operator_1',
                'operatorName': 'name surname',
                'loginTelegram': 'telegram_operator_1',
                'incidentTime': '2021-12-31T11:00:00+0000',
            },
            ('CCINCIDENT', 'https://example.ru', 'id1', 'created'),
        ),
    ),
)
async def test_cc_queues_fail(
        taxi_callcenter_qa,
        request_body,
        request_yandex_uid,
        expected_status,
        expected_ticket_body,
        expected_db_ticket,
        mock_tracker,
        load_json,
        mockserver,
        pgsql,
        mock_callcenter_operators_list_full,
):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    async def _phones_retrieve(request):
        return {'id': 'phone_pd_id', 'value': '+71234567890'}

    @mockserver.json_handler('/callcenter-queues/v1/call_info')
    async def _mock_call_info(request):
        return mockserver.make_response('', status=500)

    response = await taxi_callcenter_qa.post(
        SAVE_FEEDBACK_URL,
        json=load_json(request_body),
        headers={'X-Yandex-UID': request_yandex_uid},
    )
    assert response.status_code == expected_status

    assert mock_tracker.create_attachment.times_called == 2
    assert mock_tracker.create_issue.times_called == 1
    assert (
        mock_tracker.create_issue.next_call()['request'].json
        == expected_ticket_body
    )

    cursor = pgsql['callcenter_qa'].cursor()
    cursor.execute(
        'SELECT ticket_name, ticket_uri, feedback_id, status'
        ' FROM callcenter_qa.tickets',
    )
    assert cursor.fetchall()[0] == expected_db_ticket
    cursor.close()
